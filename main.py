import minecraft_launcher_lib as mll
from customtkinter import *
import os
import json
from tkinter import PhotoImage
import webbrowser
import subprocess
import tkinter.messagebox, threading

minecraftDirectory = mll.utils.get_minecraft_directory()

if os.path.exists(os.path.join(minecraftDirectory, '.openlauncher')):
    launcherData = json.loads(open(os.path.join(os.path.join(minecraftDirectory,
                                                             '.openlauncher'), 'launcher_data.json')).read())
else:
    os.mkdir(os.path.join(minecraftDirectory, '.openlauncher'))
    launchOptions = mll.utils.generate_test_options()
    launcherData = {
        'launchOptions': launchOptions,
        'showVanillas': True,
        'showSnapshots': True,
        'showOld': False
    }
    open(os.path.join(os.path.join(minecraftDirectory,
                                   '.openlauncher'), 'launcher_data.json'), 'w').write(json.dumps(launcherData))

vanillaVersions = []

def parseVersions():
    for v in mll.utils.get_version_list():
        if v['type'] == 'release':
            vanillaVersions.append(f"{v['type']} {v['id']}")

parseVersions()


class App(CTk):
    def __init__(self, *args, **kwargs):
        CTk.__init__(self, *args, **kwargs)

        self.github_icon = PhotoImage(file='github-mark-white.png')
        self.folder_icon = PhotoImage(file='icons8-folder-30.png')

        self.nickname = StringVar(value=launcherData['launchOptions']['username'])

        self.title('OpenLauncher')
        self.geometry('900x600')
        self.resizable(False, False)

        self.bottom_frame = CTkFrame(self, height=50, width=900, fg_color='#282828')
        self.bottom_frame.place(x=0, y=550)

        self.side_frame = CTkFrame(self, height=600, width=50)
        self.side_frame.place(x=0,y=0)


        self.github_button = CTkButton(self.side_frame, width=0, height=0, image=self.github_icon, text='', fg_color='transparent', hover_color='#545454', command=lambda: webbrowser.open('https://github.com/cuboidweb/OpenLauncher'))
        self.github_button.place(x=5,y=557)

        self.folder_button = CTkButton(self.side_frame, width=0, height=0, image=self.folder_icon, text='',
                                       fg_color='transparent', hover_color='#545454',
                                       command=lambda: os.system(f'explorer {minecraftDirectory}'))
        self.folder_button.place(x=6, y=507)

        self.version_menu = CTkOptionMenu(self.bottom_frame, height=30, values=vanillaVersions)
        self.version_menu.place(x=70, y=10)

        self.nickname_entry = CTkEntry(self.bottom_frame, width=150, height=30, placeholder_text='Nickname', textvariable=self.nickname)
        self.nickname_entry.place(y=10, x=720)

        self.play_button = CTkButton(self.bottom_frame, text='Play', width=100, height=30, command=self.play)
        self.play_button.place(x=590, y=10)

        self.install_button = CTkButton(self.bottom_frame, text='Install', width=100, height=30, command=self.install)
        self.install_button.place(x=460, y=10)

        self.nickname.trace('w', self.nickname_edit)

        self.protocol('WM_DELETE_WINDOW', self.destroyed)
    def play(self):
        ver = self.version_menu.get().split(' ')[1]
        try:
            command = mll.command.get_minecraft_command(ver, minecraftDirectory, launcherData['launchOptions'])
            self.withdraw()
            subprocess.call(command)
            self.deiconify()
        except mll.exceptions.VersionNotFound:
            tkinter.messagebox.showerror('Error!', 'Minecraft version '+ver+' not found!')
    def nickname_edit(self, *args):
        launcherData['launchOptions']['username'] = self.nickname.get()
    def destroyed(self):
        open(os.path.join(os.path.join(minecraftDirectory,
                                       '.openlauncher'), 'launcher_data.json'), 'w').write(json.dumps(launcherData))
        self.destroy()
    def install(self):
        ver = self.version_menu.get().split(' ')[1]
        def setMax(m):
            global max
            max = m
        def setProgress(p):
            self.title(f"OpenLauncher - {p}/{max}")
        def setStatus(s):
            self.title(f'OpenLauncher - {s}')
        callback = {"setMax": setMax, "setProgress": setProgress, "setStatus": setStatus}
        threading.Thread(target=lambda: mll.install.install_minecraft_version(ver, minecraftDirectory, callback)).start()


app = App()
app.mainloop()
