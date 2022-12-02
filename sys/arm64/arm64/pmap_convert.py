

publics = 'void pmap_page_set_memattr(vm_page_t m, vm_memattr_t ma);\
    void	pmap_activate_vm(pmap_t);\
    void	pmap_bootstrap(vm_offset_t, vm_offset_t, vm_paddr_t, vm_size_t);\
    int	pmap_change_attr(vm_offset_t va, vm_size_t size, int mode);\
    int	pmap_change_prot(vm_offset_t va, vm_size_t size, vm_prot_t prot);\
    void	pmap_kenter(vm_offset_t sva, vm_size_t size, vm_paddr_t pa, int mode);\
    void	pmap_kenter_device(vm_offset_t, vm_size_t, vm_paddr_t);\
    bool	pmap_klookup(vm_offset_t va, vm_paddr_t *pa);\
    vm_paddr_t pmap_kextract(vm_offset_t va);\
    void	pmap_kremove(vm_offset_t);\
    void	pmap_kremove_device(vm_offset_t, vm_size_t);\
    void	*pmap_mapdev_attr(vm_offset_t pa, vm_size_t size, vm_memattr_t ma);\
    bool	pmap_page_is_mapped(vm_page_t m);\
    int	pmap_pinit_stage(pmap_t, enum pmap_stage, int);\
    bool	pmap_ps_enabled(pmap_t pmap);\
    uint64_t pmap_to_ttbr0(pmap_t pmap);\
    \
    void	*pmap_mapdev(vm_offset_t, vm_size_t);\
    void	*pmap_mapbios(vm_paddr_t, vm_size_t);\
    void	pmap_unmapdev(vm_offset_t, vm_size_t);\
    void	pmap_unmapbios(vm_offset_t, vm_size_t);\
    \
    boolean_t pmap_map_io_transient(vm_page_t *, vm_offset_t *, int, boolean_t);\
    void	pmap_unmap_io_transient(vm_page_t *, vm_offset_t *, int, boolean_t);\
    \
    bool	pmap_get_tables(pmap_t, vm_offset_t, pd_entry_t **, pd_entry_t **, pd_entry_t **, pt_entry_t **);\
    \
    int	pmap_fault(pmap_t, uint64_t, uint64_t);\
    \
    int pmap_senter(pmap_t pmap, vm_offset_t va, vm_paddr_t pa, vm_prot_t prot, u_int flags);\
    int pmap_sremove(pmap_t pmap, vm_offset_t va);\
    void pmap_sremove_pages(pmap_t pmap);\
    \
    struct pcb *pmap_switch(struct thread *, struct thread *);\
    ' + \
    'void		 pmap_activate(struct thread *td);\
    void		 pmap_advise(pmap_t pmap, vm_offset_t sva, vm_offset_t eva, int advice);\
    void		 pmap_align_superpage(vm_object_t, vm_ooffset_t, vm_offset_t *, vm_size_t);\
    void		 pmap_clear_modify(vm_page_t m);\
    void		 pmap_copy(pmap_t, pmap_t, vm_offset_t, vm_size_t, vm_offset_t);\
    void		 pmap_copy_page(vm_page_t, vm_page_t);\
    void		 pmap_copy_pages(vm_page_t ma[], vm_offset_t a_offset, vm_page_t mb[], vm_offset_t b_offset, int xfersize);\
    int		 pmap_enter(pmap_t pmap, vm_offset_t va, vm_page_t m, vm_prot_t prot, u_int flags, int8_t psind);\
    void		 pmap_enter_object(pmap_t pmap, vm_offset_t start, vm_offset_t end, vm_page_t m_start, vm_prot_t prot);\
    void		 pmap_enter_quick(pmap_t pmap, vm_offset_t va, vm_page_t m, vm_prot_t prot);\
    vm_paddr_t	 pmap_extract(pmap_t pmap, vm_offset_t va);\
    vm_page_t	 pmap_extract_and_hold(pmap_t pmap, vm_offset_t va, vm_prot_t prot);\
    void		 pmap_growkernel(vm_offset_t);\
    void		 pmap_init(void);\
    boolean_t	 pmap_is_modified(vm_page_t m);\
    boolean_t	 pmap_is_prefaultable(pmap_t pmap, vm_offset_t va);\
    boolean_t	 pmap_is_referenced(vm_page_t m);\
    boolean_t	 pmap_is_valid_memattr(pmap_t, vm_memattr_t);\
    vm_offset_t	 pmap_map(vm_offset_t *, vm_paddr_t, vm_paddr_t, int);\
    int		 pmap_mincore(pmap_t pmap, vm_offset_t addr, vm_paddr_t *pap);\
    void		 pmap_object_init_pt(pmap_t pmap, vm_offset_t addr, vm_object_t object, vm_pindex_t pindex, vm_size_t size);\
    boolean_t	 pmap_page_exists_quick(pmap_t pmap, vm_page_t m);\
    void		 pmap_page_init(vm_page_t m);\
    int		 pmap_page_wired_mappings(vm_page_t m);\
    int		 pmap_pinit(pmap_t);\
    void		 pmap_pinit0(pmap_t);\
    void		 pmap_protect(pmap_t, vm_offset_t, vm_offset_t, vm_prot_t);\
    void		 pmap_qenter(vm_offset_t, vm_page_t *, int);\
    void		 pmap_qremove(vm_offset_t, int);\
    vm_offset_t	 pmap_quick_enter_page(vm_page_t);\
    void		 pmap_quick_remove_page(vm_offset_t);\
    void		 pmap_release(pmap_t);\
    void		 pmap_remove(pmap_t, vm_offset_t, vm_offset_t);\
    void		 pmap_remove_all(vm_page_t m);\
    void		 pmap_remove_pages(pmap_t);\
    void		 pmap_remove_write(vm_page_t m);\
    void		 pmap_sync_icache(pmap_t, vm_offset_t, vm_size_t);\
    int		 pmap_ts_referenced(vm_page_t m);\
    void		 pmap_unwire(pmap_t pmap, vm_offset_t start, vm_offset_t end);\
    void		 pmap_zero_page(vm_page_t);\
    void		 pmap_zero_page_area(vm_page_t, int off, int size);'

log_level = 'ERROR'

debug_counter = 0

def ddd(*strs):
    if log_level not in ('DEBUG'):
        return
    global debug_counter
    print('\nDEBUG', debug_counter)
    print(*strs)
    print()
    debug_counter += 1

warn_counter = 0

def www(*strs):
    if log_level not in ('DEBUG', 'WARN'):
        return
    global warn_counter
    print('\nWARN', warn_counter)
    print(*strs)
    print()
    warn_counter += 1

error_counter = 0

def eee(*strs):
    global error_counter
    print('\nERROR', error_counter)
    print(*strs)
    print()
    error_counter += 1

class Func:

    def __init__(self, declaration):
        self.declaration = declaration
        self.rettype = None
        self.name = None
        self.argtypes = []
        self.argnames = []
        self.search_def = None
        self.unused_macro = []

        # search_def 
        for word_white in declaration.split():
            for word_comma_w in word_white.split(','):
                for word in word_comma_w.split(')'):
                    if '(' in word:
                        if self.name:
                            eee('double (')
                            exit()
                        self.search_def = word.strip('*')
        
        # return type and name
        self.name = self.search_def.split('(')[0]
        self.rettype = declaration.split(self.search_def)[0]
        self.rettype = ' '.join(self.rettype.split()) # replace all whitespace with single space
    
    def signature_from_dotc(self, lines):
        for idx, line in enumerate(lines):
            if self.search_def not in line:
                continue
            if self.argtypes:
                eee('double definition')
                exit()

            line = line.strip()
            if ')' not in line:
                line += lines[idx + 1].strip()

            assert line.count('(') == 1
            assert line.count(')') == 1
            line = line.split('(')[1]
            line = line.split(')')[0]

            # arg types and names
            for argstr in line.split(','):
                argstr = argstr.strip()
                if argstr == 'void':
                    self.argnames.append('void')
                    self.argtypes.append('')
                    self.unused_macro.append(False)
                    continue
                unused_macro = False
                if ' __unused' in argstr:
                    argstr = argstr.replace(' __unused', '').strip()
                    unused_macro = True

                argname = argstr.split()[-1].strip('*[]')

                name_idx = argstr.rindex(argname)
                argtype_words = argstr[:name_idx].strip().split()
                argtype = ' '.join(argtype_words)

                if '[]' in argstr:
                    if '*' in argtype_words[-1]:
                        argtype += '*'
                    else:
                        argtype += ' *'

                self.argnames.append(argname)
                self.argtypes.append(argtype)
                self.unused_macro.append(unused_macro)
    
    def build_call_like(self, args = [], name_transform = None):
        name = name_transform(func) if name_transform else func.name
        if func.argnames[0] == 'void':
            return name + ('()' if args else '(void)')
        fn_str = name + '('
        for idx in range(len(func.argtypes)):
            argtype = func.argtypes[idx]
            if args:
                fn_str += '(' + argtype + ') ' + args[idx] + ', '
            else:
                argname = func.argnames[idx]
                unused_macro_str = ' __unused' if func.unused_macro[idx] else ''
                fn_str += argtype + ' ' + argname + unused_macro_str + ', '
        
        return fn_str[:-2] + ')'


    def __str__(self):
        return '"' + self.rettype + ' ' + self.name + '"'

    def dump(self):
        return 'DUMP\n'\
            + 'declaration: "' + self.declaration + '"\n'\
            + 'rettype: "' + self.rettype + '"\n'\
            + 'name: "' + self.name + '"\n'\
            + 'search_def: "' + self.search_def + '"\n'\
            + 'argtypes: ' + str(self.argtypes) + '\n'\
            + 'argnames: ' + str(self.argnames) + '\n\n'

    def validate(self):
        fail = self._fail_name(self.name, 'name')
        
        if not self.argnames:
            fail = True
            eee('argnames empty, so definition was not found')

        for argname in self.argnames:
            fail = self._fail_name(argname, 'argname') or fail

        if fail:
            print(self.dump())
    
    def _fail_symbol(self, symb, field, fieldname):
        if symb in field:
            eee(symb + ' in ' + fieldname + ' "' + field + '"')
            return True
    
    def _fail_name(self, field, fieldname):
        fail = self._fail_symbol('*', field, fieldname)
        fail = self._fail_symbol('[', field, fieldname) or fail
        fail = self._fail_symbol(']', field, fieldname) or fail
        return fail
    
if __name__ == "__main__":
    lines = None
    with open('pmap~.c', 'r') as pmapc:
        
        lines = pmapc.readlines()


    funcs = []
    skip_names = set(['pmap_mapdev_attr', 'pmap_mapdev', 'pmap_unmapdev'])
    skip_decls = []

    # look through fn declarations of .h files
    for line in publics.split(';'):
        line = line.strip()
        if not line:
            continue

        func = Func(line)

        if func.name in skip_names:
            www('Skipping func:')
            www(func.dump())
            skip_decls.append(line)
            continue

        funcs.append(func)

    # get exact arg names from .c files
    for func in funcs:
        func.signature_from_dotc(lines)
        func.validate()

    # construct the code
    preface = '\n/*\n * unzoned calls into priveleged instructions\n */\n\n'
    preface += '#include <machine/zone_manager.h>\n'

    def zoned_name(func: Func):
        return func.name + '_zoned'

    enum = '\nenum pmap_external_fn {'
    def enum_name(func: Func):
        return func.name + '_enum'
    def enum_line(func: Func):
        return '\n\t' + enum_name(func) + ','
    enum_tail = "\n};\n"


    transfer_type = 'uint64_t'
    struct = '\nstruct pmap_call {\n\tenum pmap_external_fn func;\n\t' + transfer_type + ' * args;\n};\n'

    
    dispatch = '\n' + transfer_type + '\npmap_dispatch(void* call_uncasted)\n{' + \
        '\n\tstruct pmap_call *call = (struct pmap_call *) call_uncasted;\n\tswitch(call->func) {'
    def dispatch_line(func: Func):
        case_line = '\n\t\tcase ' + enum_name(func) + ':'
        call = func.build_call_like(args = ['call->args[' + str(idx) + ']' for idx in range(len(func.argtypes))], name_transform=zoned_name) + ';'

        case_body = '\n\t\t\treturn (' + transfer_type + ') ' + call
        if func.rettype == 'void':
            case_body = '\n\t\t\t' + call + '\n\t\t\treturn 0;'
        
        return case_line + case_body
    dispatch_tail = '\n\t}\n}\n'


    public_fns = ''
    def public_fn(func: Func):
        declr = '\n' + func.rettype + '\n' + func.build_call_like()

        args_copy = '\n\t' + transfer_type + ' args[] = {'
        if func.argnames[0] != 'void':
            args_copy += ''.join(['(' + transfer_type + ') ' + argname + ', ' for argname in func.argnames])[:-2]
        args_copy += '};'

        pmap_call = '\n\tstruct pmap_call call = {' + enum_name(func) + ', args};'
        
        zm_call = 'zm_zone_enter(ZONE_STATE_PMAP, (void *) &call);'
        if func.rettype != 'void':
            zm_call = 'return (' + func.rettype + ') ' + zm_call
        
        return declr + '\n{' + args_copy + pmap_call + '\n\t' + zm_call + '\n}\n'
    
    skipped_cmt = ''
    def skipped_cmt_of(skip):
        return '\n// because defn not in pmap.c, skipped ' + ' '.join(skip.split())

    def additions():
        return preface + enum + enum_tail + struct + dispatch + dispatch_tail + public_fns + skipped_cmt

    new_declarations = ''
    def new_declaration_of(func: Func):
        declr = func.build_call_like(name_transform=zoned_name)
        return func.rettype + ' ' + declr + ';\n'

    pmapc = ''.join(lines)
    for func in funcs:
        enum += enum_line(func)
        dispatch += dispatch_line(func)
        public_fns += public_fn(func)
        new_declarations += new_declaration_of(func)
        pmapc = pmapc.replace(func.name + '(', zoned_name(func) + '(')
    
    for skip in skip_decls:
        skipped_cmt += skipped_cmt_of(skip)
    skipped_cmt += '\n'

    pmapc_top, pmap_bottom = pmapc.split('static void	free_pv_chunk(struct pv_chunk *pc);')
    pmap_bottom = 'static void	free_pv_chunk(struct pv_chunk *pc);' + pmap_bottom
    with open('pmap_candidate.c', 'w') as pmapc_candidate:
        pmapc_candidate.write(pmapc_top)
        pmapc_candidate.write(new_declarations)
        pmapc_candidate.write(pmap_bottom)
        pmapc_candidate.write(additions())
        
