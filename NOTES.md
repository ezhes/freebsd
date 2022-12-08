# Notes

## Replacement description

"pmap_enter_with_options(a,b,c)" -> "trampoline_func(PMAP_ENTER_WITH_OPTIONS_CALL_NR, a, b, c)"

allison will provide:
void *
zone_enter(enum zone_id, void *ur_dispatch_data)

you need to provide a function of signature:
void *
pmap_dispatch(void *ur_dispatch_data)

for testing before zone manager is done:
void *
zone_enter(enum zone_id, void *ur_dispatch_data) {
	return pmap_dispatch(ur_dispatch_data);
}

## What does what

I'll work on the zone manager stuff in the middle which will allow you to specify a pointer/other arguments and the zone you want to enter. The zone manager will switch the protections and then begin execution from that zone's dispatch function, which it can then use to invoke whatever actual protected function you want

## Build & run kernel

* How to run a built kernel image (use the qemu instructions from above, scp the kernel image (for me it's at obj/home/allison/freebsd/src/arm64.aarch64/sys/GENERIC/kernel) to /boot/kernel/kernel, reboot and pray. if the image doesn't work, delete the image and reboot the clean one to install a new image. There's a better way to do this on FreeBSD since you can actually mount the disk image for the VM to install the kernel (i.e. without using scp) but on linux it's a pain in the ass since Linux doesn't support writing to UFS. This should save y'all from needing actual hardware and UARTs. I'm still going to test on hardware since I don't trust qemu's watchpoints fully since we're doing really weird shit but we'll see.

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
rwlock.h

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
$ESR_EL1
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
  * TODO replace with `smh_calloc`, seems to be just getting page table pages
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
