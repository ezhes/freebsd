# Notes

## Important status of implementation notes

* often get "panic: data abort in critical section or under mutex" at handle_el0_sync+0x38
* spinlocks get stuck sometimes
* replacement can sleep (uses `M_WAITOK` in `vm_page_getfake`)
  * easily fixed by having a separate version of this that doesn't allow sleep
* `kmem_malloc` replacement requires `smh_init` to be before `pmap_init`
  * causes a lot of the above panics, but can boot and stay up for some time
* `pmap_grow_kernel_zoned` uses `vm_page_alloc_noobj`
  * `kmem_init` causes `pmap_grow_kernel_zoned`, but `smh_init` can't be before `kmem_init`
  * idea: have a `pmap_grow_kernel_early` that uses `vm_page_alloc_noobj`, check if early boot, panic if not

## Problems -> memory mapped watchpoints

fun implementation hack/problem: there aren't enough breakpoint registers to properly protect everything we need. This is because we need to protect (under kernel code execution):
	1. Any writes to the watchpoint registers (each watchpoint has a control and virtual address register, so 2x4=8 registers)
	2. Any writes to SPSR (saved program status register) since that can be used to disable debug exceptions and thwart the watchpoints system
	3. Any writes to TTBR0 (the page table base register) outside of the pmap zone since the ability to arbitrary page tables thwarts the pmap protection.


This means *at minimum* we would need 10 breakpoints. In practice though, we only have six. But, ahah!, we can do something kinda hacky: the watchpoint control registers are actually memory mapped in addition to being writable with instructions!

This is cool because instead of our original plan of doing something like (which uses eight breakpoints):
	msr DAIFSet, #0b1111  /* disable all exceptions */
	msr DBGWCR0_EL1, xxx  /* [BREAKPOINT] configure watchpoint 0     */
	msr DBGWVR0_EL1, xxx  /* [BREAKPOINT] configure watchpoint 0  VA */
	...
	msr DAIFClr, #0b1111  /* re-enable debug exceptions */
	isb

We can instead simply never use these instructions and prevent any code containing those instructions from ever being mapped. Then, if we stuff the watchpoint configuration page into a zone like, say, the pmap zone (since the two mutually assure each other's security as if the pmap falls, arbitrary code can be mapped and if the zone manager falls, the pmap falls), we can just stop using the breakpoint on these configuration changes all together:
	msr DAIFSet, #0b1111   /* disable all exceptions */
	dmb NSH                /* do not reorder loads or stores across barrier */
	str xxx, [DBGWCR0 addr]/* configure watchpoint 0 w/ MMIO    */
	str xxx, [DBGWVR0 addr]/* configure watchpoint 0 VA w/ MMIO */
	...
	dmb NSH                /* do not reorder loads or stores across barrier */
	msr DAIFClr, #0b1111   /* re-enable debug exceptions */

Note though that now that we're using memory mapped IO instead of the control registers, we have to use fences to prevent an older store from being retired after the watchpoints are reconfigured or a younger store from being retired before the watchpoints are reconfigured. This makes things a lot easier for us since it means we can have as many little routines that modify these registers are we want without needing to worry about keeping the number of protected instructions under a limit.

So, problem discovered and problem solved lol.

## Immediate work

@Zoey Mengzhu Sun and you need to write the black shims and the pmap_zone_dispatch stuff. I'll provide the glue that gets you from zone_enter to dispatch, but y'all need to a) do the plumbing for this and b) figure out a way to allocate all page table data into a single contiguous section of virtual memory. Right now a lot of the operations are probably going through the physmap (a region which is just all of physical memory mapped into virtual memory) but we intend to make the pmap owned pages read-only in the physmap to prevent them from being tampered through it

find the exec syscall, and to every function all the way through to pmap_pinit, add a boolean for secure process to the args

inside struct pmap, add a secure process boolean

inside pmap_pinit, set the thing to true based on fn arg

inside the following functions, add a line to pmap_kremove the physical addresses (use pmap_kextract to get kernel-space va if needed):
pmap_enter
pmap_enter_quick
pmap_enter_object

## Useful files

pmap
subr_vmem
kmem
vm
vm_map
vm_extern
vm_kern // has vm_maps
vm_page
vm_phys

## Interesting structs & fns

struct vmspace { !! owns pmap
vmspace_alloc
PMAP_LOCK_INIT(

## Weird things

Are #define macros used unzoned?

Find definition of `pmap_mapdev_attr(vm_offset_t pa`, `pmap_mapdev(vm_offset_t`, `pmap_unmapdev(vm_offset_t`.
What to do with extern fn's `pmap_clean_stage2_tlbi` and `pmap_invalidate_vpipt_icache`?

## functions that might map protected phys page into an attacker pmap

### need

pmap_copy
pmap_sync_icache
pmap_extract_and_hold -- gets va
pmap_extract -- gets physical address
pmap_map -- public PHYS_TO_DMAP

### removes (tails)

pmap_remove_pt_page -- from remove_pages
pmap_unuse_pt -- from remove_all
pmap_kremove
pmap_remove

### protect priority 1

pmap_kenter
pmap_enter
pmap_enter_object
pmap_enter_quick

### dunno

pmap_protect

### private

pmap_pte

### protection code

physmem_avail // still don't know how to get amnt of physical mem though

```c
// into top of pmap.c
// each value is 4 bytes, but counter & protection will fit in 1 byte
// lowest bit is for protected bool
uint32_t *pmap_pageuse;

#define pageuse_pageid(pa) (pa) >> L3_SHIFT
#define pageuse_storagesize 32
#define pageuse_fieldbits 2
#define pageuse_fieldmask ((1 << pageuse_fieldbits) - 1)
#define pageuse_fieldsize (pageuse_storagesize / (1 << pageuse_fieldbits))
#define pageuse_pageid_bitpos(pageid) ((pageid) & pageuse_fieldmask) * pageuse_fieldsize
```

```c

```

#### enter

```c
vm_paddr_t ppage_id = pageuse_pageid(pa);
uint32_t ppage_id_bitpos = pageuse_pageid_bitpos(ppage_id);
ppage_id = ppage_id >> pageuse_fieldbits;
uint32_t increment = 0b10 << ppage_id_bitpos;
// add must be before check
atomic_add_32(pmap_pageuse + ppage_id, increment);
if (pmap_pageuse[ppage_id] >> ppage_id_bitpos & 1) {
    panic("violating pmap_pageuse, pa: 0x%lx", pa);
}
if (pmap_pageuse[ppage_id] >> ppage_id_bitpos == 0) {
    // todo: this check is not thread safe -- can miss the overflow
    panic("pmap_pageuse overflow, pa: 0x%lx", pa);
}
```

#### remove

```c
static __inline void
decrement(vm_paddr_t pa)
{
    vm_paddr_t ppage_id = pageuse_pageid(pa);
    uint32_t ppage_id_bitpos = pageuse_pageid_bitpos(ppage_id);
    ppage_id = ppage_id >> pageuse_fieldbits;
    uint32_t increment = 0b10 << ppage_id_bitpos;
    atomic_sub_32(pmap_pageuse + p_page, increment);
}
```

#### protected enter

```c
vm_paddr_t ppage_id = pageuse_pageid(pa);
uint32_t ppage_id_bitpos = pageuse_pageid_bitpos(ppage_id);
ppage_id = ppage_id >> pageuse_fieldbits;
uint32_t protected = 0b1 << ppage_id_bitpos;
uint32_t old_pageuse = pmap_pageuse[ppage_id];
do {
    // todo: assumes that page starts mapped in dmap and nowhere else
    if (old_pageuse & protected || (old_pageuse >> ppage_id_bitpos) > 0b10) {
        panic("protected map failed on already-mapped page, pa: 0x%lx", pa);
    }
} while (atomic_fcmpset_32(pmap_pageuse + ppage_id, &old_pageuse, old_pageuse & protected));
pmap_remove_zoned(kernel_pmap, PHYS_TO_DMAP(pa & (~L3_SIZE)), PHYS_TO_DMAP((pa & (~L3_SIZE)) + 1));
```

### safe

pmap_copy_page
pmap_copy_pages

## lock notes

### pmap.c

mtx_lock -> mtx_lock_spin
mtx_unlock -> mtx_unlock_spin

#### rw locks -- yikes

rw_wlock
rw_rlock
rw_wunlock
rw_runlock

### inlcude pmap.h

PMAP_LOCK etc.

## debugging

exception link register -- thing before interrupt maybe

```bash
p/x $ELR_EL1
```

view some assembly instrs

```bash
x/10i instr
```

view symbol that instr is a part of

```bash
p/a instr
```

exception.S:269

exception reason:

```bash
p/x $ESR_EL1
p/t $ESR_EL1 >> 26
```

objdump

```bash
llvm-objdump-14 -D path/to/kernel --start-address=your_address | less
```

## allocation

### init relevant

* alloc_pages(var, np)
  * in `pmap_bootstrap_zoned`
  * allocated things in the pre-vm time, so should be fine
* kmem_malloc(vm_size_t size, int flags)
  * in `pmap_init_asids` and `pmap_init_zoned`
  * TODO replace with `smh_calloc`

### rest

* vmem_alloc(vmem_t *vm, vmem_size_t size, int flags, vmem_addr_t *addrp)
  * in `pmap_map_io_transient_zoned`
  * `pmap_map_io_transient_zoned` is never called, so replacing with panic
* vm_page_alloc_noobj(int req)
  * seen attrs: vm_alloc_wired, vm_alloc_interrupt, vm_alloc_zero, vm_alloc_waitok
  * can pass VM_ALLOC_NOWAIT
  * replace with `smh_calloc`, seems to be just getting page table pages
* kva_alloc(vm_size_t size)
  * allocates VA only, not actual memory
  * used in conjunction with `pmap_kenter_zoned` to add a phys page somewhere in kernel, later remove
  * `kva_alloc` in `pmap_demote_l1` and `pmap_demote_l2_locked`: need to replace `pmap_kenter_zoned` with an internal-only version so that secure processes can use that and `pmap_kenter_zoned` can be disallowed for secure processes.
  * `kva_alloc` in `pmap_mapbios_zone`: seems to be for kernel work; can try replacing with smh but probably not

### vm_page_alloc_noobj(int req)

* `vm_domainset_iter_page_init(struct`
  * safe: `vm_domainset_iter_init(struct`
    * safe: `vm_object_reserv(vm_object_t`
  * safe: `vm_domainset_iter_first(struct`
    * safe: `PCPU_GET` & `DOMAINSET_ISSET`
    * safe: `vm_domainset_iter_rr(struct`
    * safe: `vm_domainset_iter_interleave(struct`
  * safe: `vm_page_count_min_domain(`
  * `vm_domainset_iter_page(struct`
    * lock safe: `VM_OBJECT_WUNLOCK` -- `obj` is `NULL`
    * above safe: `vm_page_count_min_domain` `vm_domainset_iter_first`
    * safe: `vm_domainset_iter_next(struct`
      * safe: `vm_domainset_iter_rr(struct`
      * safe: `vm_domainset_iter_prefer(struct`
    * **BAD** sleeps, locks: `vm_wait_doms(const`
      * safe: `vm_page_count_min_set(const`
* `vm_page_alloc_noobj_domain(int` -> `_vm_page_alloc_noobj_domain(int`
  * safe: `VM_DOMAIN(n)`
  * **BAD**: `uma_zalloc`
  * **BAD**: `pmap_zero_page`
  * `vm_domain_allocate(struct` -> `_vm_domain_allocate(struct`
    * safe : `vm_paging_needed`
    * **BAD** locks: `pagedaemon_wakeup(int`
      * **BAD** wakeup: `wakeup(const`
    * **BAD** locks: `vm_domain_set(struct`
  * : `vm_domain_free_lock`
  * : `vm_phys_alloc_pages`
  * : `vm_phys_alloc_freelist_pages`
  * : `vm_domain_free_unlock`
  * : `vm_domain_freecnt_inc`
  * : `vm_reserv_reclaim_inactive`
  * : `vm_domain_alloc_fail`
  * : `vm_page_dequeue`
  * : `vm_page_alloc_check`
  * : `vm_wire_add`
* above bad: `vm_domainset_iter_page(struct`

## 12/9 crashes

### illegal data abort in handle_el0_sync

Earliest this happens is at "Trying to mount root from ufs:/dev/gpt/rootfs \[rw\]...". Can happen after boot as well.

Making `vm_page_alloc_noobj` replacement use `VM_MEMATTR_WRITE_BACK` made this happen most of the time right after the above.

`smh_init` before `pmap_init` makes this way more probable a little after fs mount starts.

```
  x0:         40a13000
  x1:                0
  x2:                1
  x3:         40418720
  x4:          28f5c28
  x5:           a3d70b
  x6:               83
  x7:              16d
  x8:           13abc8
  x9:         3b049374
 x10:                0
 x11:               11
 x12:           13ac08
 x13:            75220
 x14:               1a
 x15:         ffffffff
 x16:           13a978
 x17:           119ca0
 x18:                1
 x19:         40a392a0
 x20:         40a23060
 x21:                0
 x22:           13abc0
 x23:                b
 x24:           13a000
 x25:                0
 x26:         3b9aca00
 x27:           13a000
 x28:           10377c
 x29:     ffffffffe9e0
  sp:     ffffffffe9e0
  lr:           115f3c
 elr:           119ca0
spsr:              200
 far:     ffffffffe9d0
 esr:         9200004f
panic: data abort in critical section or under mutex
cpuid = 3
time = 1652353500
KDB: stack backtrace:
#0 0xffff0000004f80a8 at kdb_backtrace+0x60
#1 0xffff0000004a43e8 at vpanic+0x178
#2 0xffff0000004a426c at panic+0x44
#3 0xffff0000007d4ee8 at data_abort+0x268
#4 0xffff0000007b58fc at handle_el0_sync+0x38
Uptime: 11m1s
```

### spin lock held for too long

```
spin lock 0xffff0000497cb100 (sched lock 1) held by 0xffff00005ad53580 (tid 100059) too long
  x0: ffff0000008d1000
  x1: ffff000049bf2070
  x2: ffff0000008b9a30
  x3:         deadc0d8
  x4:                0
  x5: ffff0000007d4c68
  x6:                1
  x7:              501
  x8: ffff000000de1b28
  x9:         deadc0de
 x10:          3938700
 x11:           9897fe
 x12:                f
 x13: ffff0000007c3588
 x14:         7ff6d8cd
 x15:               40
 x16:               8c
 x17:              cf4
 x18: ffff000049bf2060
 x19: ffff000000de1b28
 x20: ffff00005ad53580
 x21:                0
 x22: ffff00005ad53580
 x23:                0
 x24: ffff000000b8f000
 x25:           98967f
 x26: ffff000000de1b40
 x27: ffff000049fcadfc
 x28: ffff000000e7144c
 x29: ffff000049bf2060
  sp: ffff000049bf2060
  lr: ffff00000047c290
 elr: ffff00000047c0d8
spsr:              2c5
 far:         deadc178
 esr:         96000004
timeout stopping cpus
panic: spin lock held too long
cpuid = 0
time = 1652351310
KDB: stack backtrace:
#0 0xffff0000004f80a8 at kdb_backtrace+0x60
#1 0xffff0000004a43e8 at vpanic+0x178
#2 0xffff0000004a426c at panic+0x44
#3 0xffff00000047c0f0 at _mtx_lock_indefinite_check+0x88
#4 0xffff00000047c28c at thread_lock_flags_+0xd8
#5 0xffff0000004583cc at intr_event_schedule_thread+0x6c
#6 0xffff000000458974 at swi_sched+0xa4
#7 0xffff000000420d60 at handleevents+0x188
#8 0xffff0000004219a4 at timercb+0x304
#9 0xffff0000007ac028 at arm_tmr_intr+0x5c
#10 0xffff000000458a44 at intr_event_handle+0xa8
#11 0xffff0000007a7d28 at intr_isrc_dispatch+0x70
#12 0xffff0000007aca3c at arm_gic_intr+0x120
#13 0xffff0000007a7ae0 at intr_irq_handler+0x7c
#14 0xffff0000007b5870 at handle_el1h_irq+0xc
#15 0xffff000000755c90 at ufs_open+0x7c
#16 0xffff000000893b44 at VOP_OPEN_APV+0x2c
#17 0xffff00000044afd4 at exec_check_permissions+0xe8
timeout stopping cpus
panic: data abort in critical section or under mutex
cpuid = 1
time = 1652351310
KDB: stack backtrace:
#0 0xffff0000004f80a8 at kdb_backtrace+0x60
#1 0xffff0000004a43e8 at vpanic+0x178
#2 0xffff0000004a426c at panic+0x44
#3 0xffff0000007d4ed0 at data_abort+0x268
#4 0xffff0000007b5810 at handle_el1h_sync+0x10
#5 0xffff00000047c28c at thread_lock_flags_+0xd8
#6 0xffff00000047c28c at thread_lock_flags_+0xd8
#7 0xffff0000004200e4 at statclock+0xd8
#8 0xffff000000420cd4 at handleevents+0xfc
#9 0xffff0000004219a4 at timercb+0x304
#10 0xffff0000007ac028 at arm_tmr_intr+0x5c
#11 0xffff000000458a44 at intr_event_handle+0xa8
#12 0xffff0000007a7d28 at intr_isrc_dispatch+0x70
#13 0xffff0000007aca3c at arm_gic_intr+0x120
#14 0xffff0000007a7ae0 at intr_irq_handler+0x7c
#15 0xffff0000007b5870 at handle_el1h_irq+0xc
#16 0xffff0000007cdfd8 at pmap_fault+0x2c
#17 0xffff0000007d4ce0 at data_abort+0x78
```

### test user program

```c
int fib(int n) {
	if (n == 0)
		return 0;
	if (n == 1)
		return 1;
	return fib(n-1) + fib(n-2);
}

int main() {
	int *ptr = 0;
	while (fib(10) == 55) {
		; // currently even this immediately crashes
	}
	if (0) { // correct execution
		int result = *ptr;
	}
  // else, syscall
	return 0;
}
```

```c
#include <stdio.h>

int main() {
    printf("Hello World.\n");
    return 0;
}
```

```c
#include <stdio.h>
#include <stdlib.h>
int fib(int n) {
	if (n == 0)
		return 0;
	if (n == 1)
		return 1;
	return fib(n-1) + fib(n-2);
}

int main(int argc, char **argv) {
    int n;

    if (argc != 2) {
      printf("Wrong number of arguments.\n");
      return 0;
    }

    n = atoi(argv[1]);

    printf("Fib %d = %d\n", n, fib(n));

    return 0;
}
```

```c
#include <stdio.h>
int main(int argc, char **argv) {
    int n;
    scanf("%d", &n);
    printf("Read: %d\n", n);
    return 0;
}
```

```c
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("Wrong number of arguments.\n");
    return 0;
  }
  int loop = 0; // have an infinite loop
  do {
    char *fname = argv[1];
    int fd = open(fname, O_RDONLY);
    printf("Opened.\n");
    int read_cnt = 0;
    int remaining = 100;
    char *str = calloc(sizeof(char), 4096);
    printf("Allocated.\n");

    while ((read_cnt = read(fd, str, remaining)) > 0) {
      remaining -= read_cnt;
    }
    printf("Finished reading.\n");
    str[remaining - 1] = '\0';
    printf("Read: \"%s\".\n", str);
  } while (loop);

  return 0;
}
```
