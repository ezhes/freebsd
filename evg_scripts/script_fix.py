if __name__ == "__main__":
    import os

    if os.getcwd().split('/')[-1] != 'shiny_tools':
        print('Error, wrong cwd.')
        exit()

    whitelist = set(['cqemu.sh', 'evgeny_image_update.sh', 'script_fix.py'])
    mark = '# file edited by shiny_tools/script_fix.py\n'

    for file_name in os.listdir():
        if not os.path.isfile(file_name) or file_name in whitelist or '.sh' not in file_name:
            continue
        
        contents = None
        with open(file_name, "r") as file:
            contents = file.read()
        if mark in contents:
            continue

        with open(file_name, "w") as file:
            file.write(contents.replace('allison/freebsd', 'evgeny/shiny').replace('-netdev user,id=net0', '-netdev user,id=net0,hostfwd=tcp::10022-:22'\
                ).replace('fbd', 'free@localhost').replace('free@localhost_', 'fbd_').replace('ssh', 'ssh -p 10022').replace('rsync', 'rsync -arvz -e \'ssh -p 10022\''))
            file.write(mark)
