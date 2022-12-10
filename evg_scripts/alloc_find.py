if __name__ == "__main__":
    contents = None
    with open('sys/arm64/arm64/pmap~.c', 'r') as pmapc:
        contents = pmapc.read()

    pmapc = contents.lower()

    matches = set()
    blacklist = set(['&pv_entry_allocs', 'vm_alloc_zero', '"pmap_alloc_l3:', '>', 'allocation/deallocation', 'allocs', 'allocation', 'allocation.'])
    for word_wh in pmapc.split():
        for word in word_wh.split('('):
            if 'alloc' in word and word not in blacklist and word not in matches:
                # fail = False
                # for black in blacklist:
                #     if black in word:
                #         fail = True
                #         break
                # if not fail:
                    matches.add(word)

    print('\n'.join(matches))