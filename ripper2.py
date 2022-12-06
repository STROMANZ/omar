#!/usr/bin/python
import tkinter as tk
import os
from tkinter.ttk import *
from tkinter import filedialog

geo_width = 1280
geo_height = 57
drives = {}

def drive_config_reader():
    drive_config = open('.drive.config', 'r')
    if len(drive_config.read()) == 0:
        drive_config_writer(12)
    drive_config = open('.drive.config', 'r')
    value = drive_config.read()
    drive_config.close()
    return value

def drive_config_writer(number):
    drive_config = open('.drive.config', 'w')
    drive_config.write('%d' % number)
    drive_config.close()

def output_config_reader():
    output_config = open('.output.config', 'r')
    if len(output_config.read()) == 0:
        output_config_writer("/media")
    output_config = open('.output.config', 'r')
    path = output_config.read()
    output_config.close()
    return path

def output_config_writer(path):
    output_config = open('.output.config', 'w')
    output_config.write('%s' % path)
    output_config.close()

def check_mount_point(path):
    if not os.path.ismount(path):
        tk.messagebox.showinfo(title="Externe USB Check", message=f'{path} is geen USB-disk')

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def queryOutputPath():
    global outpath
    outpath = tk.filedialog.askdirectory(parent=window, initialdir="/media/", title='Selecteer output directory (USB-Disk)')
    output_config_writer(outpath)
    check_mount_point(outpath)

def applySettings(event):
    global drives
    global geo_height
    new_geo_height = geo_height * slidervalue.get()
    window.geometry(f'{geo_width}x{new_geo_height}')

    drive_config_writer(slidervalue.get())

    if slidervalue.get() < len(drives):
        drives_rem(slidervalue.get())
    elif slidervalue.get() > len(drives):
        drives_add(slidervalue.get())
    else:
        pass

def drives_rem(numberofdrives):
    global drives
    for drive in range(numberofdrives):
        drives[drive].popitem()

def handle_button_action_press(instanceID):
    try:
        id = int(drives[instanceID]['inputtxt'].get())
    except:
        tk.messagebox.showerror('Error', 'Error: Dig-ID geen nummer')
    else:
        outputdir = output_config_reader() + "/" + str(drives[instanceID]['inputtxt'].get()) + "/"
        create_directory(outputdir)
        iso_name = outputdir + str(drives[instanceID]['inputtxt'].get()) + ".iso"
        print(iso_name)
        iso_md5_name = iso_name + ".md5"
        print(iso_md5_name)
        iso_md5_optical_name = iso_name + ".optical.md5"
        print(iso_md5_optical_name)
        optical_device = "/dev/sr" + str(instanceID)
        print(optical_device)

def drives_add(numberofdrives):
    global drives
    for drive in range(numberofdrives):
        drives[drive] = {'digid': 0, 'running': False, 'deviceID': drive}

        # Label
        drives[drive]['IDLabel'] = tk.Label(window, text="Dig-ID:")
        drives[drive]['IDLabel'].grid(row=drive, column=1)

        # TextBox Creation
        drives[drive]['inputtxt'] = tk.Entry(window, width=30)
        drives[drive]['inputtxt'].grid(row=drive, column=2)

        # Button Creation (needs work)
        if drive == 0:
            button_action_0 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(0))
            button_action_0.grid(row=drive, column=10, sticky='E')
        elif drive == 1:
            button_action_1 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(1))
            button_action_1.grid(row=drive, column=10, sticky='E')
        elif drive == 2:
            button_action_2 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(2))
            button_action_2.grid(row=drive, column=10, sticky='E')
        elif drive == 3:
            button_action_3 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(3))
            button_action_3.grid(row=drive, column=10, sticky='E')
        elif drive == 4:
            button_action_4 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(4))
            button_action_4.grid(row=drive, column=10, sticky='E')
        elif drive == 5:
            button_action_5 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(5))
            button_action_5.grid(row=drive, column=10, sticky='E')
        elif drive == 6:
            button_action_6 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(6))
            button_action_6.grid(row=drive, column=10, sticky='E')
        elif drive == 7:
            button_action_7 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(7))
            button_action_7.grid(row=drive, column=10, sticky='E')
        elif drive == 8:
            button_action_8 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(8))
            button_action_8.grid(row=drive, column=10, sticky='E')
        elif drive == 9:
            button_action_9 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(9))
            button_action_9.grid(row=drive, column=10, sticky='E')
        elif drive == 10:
            button_action_10 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(10))
            button_action_10.grid(row=drive, column=10, sticky='E')
        elif drive == 11:
            button_action_11 = tk.Button(text="Run", relief='raised', command=lambda: handle_button_action_press(11))
            button_action_11.grid(row=drive, column=10, sticky='E')

        drives[drive]['prog_label'] = tk.Label(window, text="Voortgang:")
        drives[drive]['prog_label'].grid(row=drive, column=6)

        # Progress bar widget
        drives[drive]['progress'] = Progressbar(window, length=300, mode='determinate')
        drives[drive]['progress'].grid(row=drive, column=7, columnspan=3, sticky='EW')

        # Console Output
        drives[drive]['console_output'] = tk.Text(window, state='disabled', bg='black', fg='white', height=3, width=64, insertborderwidth=2)
        drives[drive]['console_output'].grid(row=drive, columnspan=3, column=3, sticky='E')

def openSettingsWindow():
    SettingsWindow = tk.Toplevel(window)
    SettingsWindow.lift()
    SettingsWindow.title("Settings")
    SettingsWindow.geometry("200x100")

    global slidervalue

    slider = tk.Scale(
        SettingsWindow,
        variable=slidervalue,
        from_=1,
        to=12,
        orient='horizontal',
    )
    slider.pack()

    outputButton = tk.Button(
        SettingsWindow,
        text="Opslag Locatie",
        command=queryOutputPath
    )
    outputButton.pack()

    applyButton = tk.Button(
        SettingsWindow,
        text="Toepassen",
        command=SettingsWindow.destroy
    )
    applyButton.bind('<Button-1>', applySettings)
    applyButton.pack()

#-------------------------------------------------------------------------------------------------------------

window = tk.Tk()
window.title("Optical Media Archive Ripper")
window.geometry(f'{geo_width}x{geo_height}')

menubar = tk.Menu(window)
window.config(menu=menubar)
file_menu = tk.Menu(menubar)

file_menu.add_command(
    label='Settings',
    command=openSettingsWindow,
)

file_menu.add_command(
    label='Exit',
    command=window.destroy,
)

menubar.add_cascade(
    label="File",
    menu=file_menu,
    underline=0
)

check_mount_point(output_config_reader())

slidervalue = tk.IntVar()
slidervalue.set(int(drive_config_reader()))
applySettings(True)

if __name__ == '__main__':
    window.mainloop()
