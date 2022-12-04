if __name__ == "__main__":
    lines = None
    with open('pmap~.c', 'r') as pmapc:
        
        lines = pmapc.readlines()

    pmapc = ''.join(lines).lower()

    locks = set()
    blacklist = set(['lockp', 'lock.', 'lock,', 'block', 'locks.', '*new_lock;', 'list'])
    for word_wh in pmapc.split():
        for word in word_wh.split('('):
            if 'lock' in word and word not in blacklist and word not in locks:
                fail = False
                for black in blacklist:
                    if black in word:
                        fail = True
                        break
                if not fail:
                    locks.add(word)
    
    with open('pmap_analysis_results.txt', 'w') as file:
        for lock in locks:
            file.write(lock + '\n')