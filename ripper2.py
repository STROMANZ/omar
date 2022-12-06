#!/usr/bin/python
import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
import os
import time
import signal
import shutil
import subprocess
from subprocess import Popen, PIPE
import stat
from threading import Thread


geo_width = 1280
geo_height = 57
drives = {}
output = "/media"


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
        tk.messagebox.showinfo(title="Externe USB Check", message=f'\"{path}\" is geen USB-disk')


def drive_exists(path):
    try:
        return stat.S_ISBLK(os.stat(path).st_mode)
    except:
        return False

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def progress_indicator(deviceid, number):
    drives[deviceid]['progress'] = number


def checksum_from_file(file_name):
    file = open(file_name, 'r')
    line = file.readline()
    sum = line.split()
    return sum[0]


def md5sum_compare(deviceid, media_md5, iso_md5):
    if str(media_md5) != str(iso_md5):
        drives[deviceid]['console_output'].insert("end-1c", "Het gemaakte iso bestand komt niet overeen met het \
        orignele optische media")
        window.update_idletasks()
        return 1


def queryoutputpath():
    global outpath
    outpath = tk.filedialog.askdirectory(parent=window, initialdir="/media/",
                                         title='Selecteer output directory (USB-Disk)')
    output_config_writer(outpath)
    check_mount_point(outpath)


def applysettings(event):
    global drives
    global geo_height

    modifydrives = True

    if len(drives) == 0:
        pass
    else:
        for drive in range(len(drives)):
            if drives[drive]['running']:
                tk.messagebox.showerror('Error', f'Aanpassing afgewezen, drive /dev/sr{drives[drive]["deviceID"]} \
                is actief')
                modifydrives = False

    if modifydrives:
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


def handle_button_action_press(deviceid):
    runjob = True

    try:
        int(drives[deviceid]['inputtxt'].get())
    except:
        tk.messagebox.showerror('Error', 'Error: Dig-ID geen nummer')
    else:
        if drives[deviceid]['running']:
            tk.messagebox.showerror('Error', f'Niet gestart, drive /dev/sr{drives[deviceid]["deviceID"]} \
            is al actief')
            runjob = False

    if not drive_exists("/dev/sr" + str(drives[deviceid]['deviceID'])):
        tk.messagebox.showerror('Error', f'Niet gestart, drive /dev/sr{drives[deviceid]["deviceID"]} bestaat niet')
        runjob = False

    if runjob:
        drives[deviceid]['running'] = True
        outputdir = output_config_reader() + "/" + str(drives[deviceid]['inputtxt'].get()) + "/"
        create_directory(outputdir)
        iso_name = outputdir + str(drives[deviceid]['inputtxt'].get()) + ".iso"
        print(iso_name)
        iso_md5_name = iso_name + ".md5"
        print(iso_md5_name)
        iso_md5_optical_name = iso_name + ".optical.md5"
        print(iso_md5_optical_name)
        optical_device = "/dev/sr" + str(deviceid)
        print(optical_device)
        progress_indicator(deviceid, 5)
        dd = Popen(["dd", "if=" + optical_device, "of=" + iso_name, "conv=noerror"], stderr=PIPE)
        while dd.poll() is None:
            time.sleep(.3)
            dd.send_signal(signal.SIGUSR1)
            while 1:
                line = dd.stderr.readline()
                if 'bytes' in str(line):
                    drives[deviceid]['console_output'].delete('1.0', tk.END)
                    drives[deviceid]['console_output'].insert("end-1c", line)
                    window.update_idletasks()
                    break
        progress_indicator(deviceid, 35)
        with open(iso_md5_optical_name, 'w') as chksum_file:
            subprocess.run(["md5sum", optical_device], stdout=chksum_file)
        chksum_file.close()
        md5_a = checksum_from_file(iso_md5_optical_name)
        progress_indicator(deviceid, 65)
        with open(iso_md5_name, 'w') as chksum_file:
            subprocess.run(["md5sum", iso_name], stdout=chksum_file)
        chksum_file.close()
        md5_b = checksum_from_file(iso_md5_name)
        md5sum_compare(deviceid, md5_a, md5_b)
        progress_indicator(deviceid, 70)
        drives[deviceid]['console_output'].insert("end-1c", "Checksum validatie succesvol" + '\n')
        window.update_idletasks()
        progress_indicator(deviceid, 75)
        create_directory(outpath + "temp/")
        subprocess.run(["fuseiso", iso_name, outpath + "temp/"])
        shutil.copytree(outpath + "temp", outpath + "content")
        subprocess.run(["fusermount", "-u", outpath + "temp"])
        subprocess.run(["rm", "-rf", outpath + "temp/"])
        progress_indicator(deviceid, 95)
        subprocess.run(["eject"])
        drives[deviceid]['console_output'].insert("end-1c", "Done")
        progress_indicator(deviceid, 100)

        drives[deviceid]['running'] = False


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

        # thread_1 = Thread(target=handle_button_action_press(0))

        # Button Creation (needs work)
        # Calling a function with an argument gets executed when adding to grid.
        # Using a lambda function with variables, while iterating, causes all variable to be set to last iteration val.
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
        drives[drive]['console_output'] = tk.Text(window, state='disabled', bg='black', fg='white',
                                                  height=3, width=64, insertborderwidth=2)
        drives[drive]['console_output'].grid(row=drive, columnspan=3, column=3, sticky='E')


def open_settings_window():
    settings_window = tk.Toplevel(window)
    settings_window.lift()
    settings_window.title("Settings")
    settings_window.geometry("200x100")

    global slidervalue

    slider = tk.Scale(
        settings_window,
        variable=slidervalue,
        from_=1,
        to=12,
        orient='horizontal',
    )
    slider.pack()

    output_button = tk.Button(
        settings_window,
        text="Opslag Locatie",
        command=queryoutputpath
    )
    output_button.pack()

    apply_button = tk.Button(
        settings_window,
        text="Toepassen",
        command=settings_window.destroy
    )
    apply_button.bind('<Button-1>', applysettings)
    apply_button.pack()


# -------------------------------------------------------------------------------------------------------------

window = tk.Tk()
window.title("Optical Media Archive Ripper")
window.geometry(f'{geo_width}x{geo_height}')

menubar = tk.Menu(window)
window.config(menu=menubar)
file_menu = tk.Menu(menubar)

file_menu.add_command(
    label='Settings',
    command=open_settings_window,
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
applysettings(True)

if __name__ == '__main__':
    window.mainloop()
