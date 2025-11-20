aper(image_path):
    if not os.path.exists(NITROGEN_CFG_PATH):
        show_message("Error", "Nitrogen config not found.", True)
        return
    with open(NITROGEN_CFG_PATH, 'r') as f:
        lines = f.readlines()
    with open(NITROGEN_CFG_PATH, 'w') as f:
        for line in lines:
            if line.startswith("file="):
                f.write(f"file={image_path}\n")
            else:
                f.write(line)
    
    subprocess.run(["nitrogen", "--restore"])
    subprocess.run(
    'qtile cmd-obj -o cmd -f restart && source ./color_changer.sh && sleep 3 && ~/.config/qtile/trayer.py &',
    shell=True)
    subprocess.run('sleep 1',shell=True)
    subprocess.run('~/.config/qtile/trayer.py',shell=True)

    show_message("Suc