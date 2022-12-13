#!/usr/bin/python
import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import os
import time
import signal
import shutil
import subprocess
from subprocess import Popen, PIPE
import stat
from threading import Thread
from datetime import datetime
from time import sleep
from pathlib import Path
from contextlib import redirect_stdout

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
    drive_config = open('.drive.config', 'w+')
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
    output_config = open('.output.config', 'w+')
    output_config.write('%s' % path)
    output_config.close()


def check_mount_point(path):
    if not os.path.ismount(path):
        tk.messagebox.showinfo(title="Externe USB Check", message=f'\"{path}\" is geen USB-disk')


def find_owner(filename):
    return Path(filename).owner()


def drive_exists(path):
    try:
        return stat.S_ISBLK(os.stat(path).st_mode)
    except:
        return False


def create_directory(path):
    if os.path.exists(path):
        return False
    else:
        os.makedirs(path)
        return True


def progress_indicator(deviceid, number):
    drives[deviceid]['progress']['value'] = number
    window.update_idletasks()


def checksum_from_file(file_name):
    file = open(file_name, 'r')
    line = file.readline()
    checksum = line.split()
    return checksum[0]


def md5sum_compare(deviceid, media_md5, iso_md5):
    if str(media_md5) != str(iso_md5):
        drives[deviceid]['console_output'].insert("end-1c", "Het gemaakte iso bestand komt niet overeen met het \
        orignele optische media")
        return 1


def queryoutputpath():
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

def thread_runner(deviceid):
    x = "device"
    z = {x: "t" + str(deviceid)}
    z["device"] = Thread(target=handle_button_action_press, args=(deviceid,))
    z["device"].start()

def drives_rem(numberofdrives):
    global drives
    for drive in range(numberofdrives):
        drives[drive].popitem()

def handle_button_action_press(deviceid):
    # Sanity checks, is the dig-id input an integer and is this instance already active
    try:
        int(drives[deviceid]['inputtxt'].get())
    except:
        tk.messagebox.showerror('Error', 'Error: Dig-ID geen nummer')
        # We need a return value to end the thread
        return 1
    else:
        if drives[deviceid]['running']:
            tk.messagebox.showerror('Error', f'Niet gestart, drive /dev/sr{drives[deviceid]["deviceID"]} \
            is al actief')
            # We need a return value to end the thread
            return 1

    # Does the CD/DVD drive exist, otherwise it has no use starting
    if not drive_exists("/dev/sr" + str(drives[deviceid]['deviceID'])):
        tk.messagebox.showerror('Error', f'Niet gestart, drive /dev/sr{drives[deviceid]["deviceID"]} bestaat niet')
        # We need a return value to end the thread
        return 1

    # Make sure no information on disk is overwriten
    outputdir = output_config_reader() + "/" + str(drives[deviceid]['inputtxt'].get()) + "/"
    if not create_directory(outputdir):
        tk.messagebox.showerror('Error', f'Niet gestart, {outputdir} bestaat al')
        drives[deviceid]['running'] = False
        return 1

    # Start time registration, required to gather sector error logging
    begin_time = datetime.now()
    drives[deviceid]['running'] = True

    # Register the required variables
    iso_name = outputdir + str(drives[deviceid]['inputtxt'].get()) + ".iso"
    iso_md5_name = iso_name + ".md5"
    iso_md5_optical_name = iso_name + ".optical.md5"
    iso_sector_log = outputdir + "sector_errors.log"
    iso_content_log = outputdir + "content_errors.log"
    optical_device = "/dev/sr" + str(deviceid)

    # Give user some visual feedback via the progress indicator
    progress_indicator(deviceid, 5)

    # Gather disk copy progress from dd-command
    dd = Popen(["dd", "if=" + optical_device, "of=" + iso_name, "conv=noerror"], stderr=PIPE)
    while dd.poll() is None:
        time.sleep(.3)
        dd.send_signal(signal.SIGUSR1)
        while 1:
            line = dd.stderr.readline()
            if 'bytes' in str(line):
                drives[deviceid]["console_output"].delete('1.0', tk.END)
                drives[deviceid]["console_output"].insert("end-1c", line)
                window.update_idletasks()
                break
    progress_indicator(deviceid, 35)

    # Gather checksum from both source device and output for comparison
    with open(iso_md5_optical_name, 'w') as chksum_file:
        subprocess.run(["md5sum", optical_device], stdout=chksum_file)
    chksum_file.close()
    md5_a = checksum_from_file(iso_md5_optical_name)
    progress_indicator(deviceid, 65)
    with open(iso_md5_name, 'w+') as chksum_file:
        subprocess.run(["md5sum", iso_name], stdout=chksum_file)
    chksum_file.close()
    md5_b = checksum_from_file(iso_md5_name)
    progress_indicator(deviceid, 70)
    if md5sum_compare(deviceid, md5_a, md5_b):
        drives[deviceid]["console_output"].insert("end-1c", "Checksum validatie succesvol" + '\n')
    progress_indicator(deviceid, 75)

    # Create a temporary directory in order to mount the ISO-image via fuseISO as a non-priv user
    create_directory(outputdir + "temp/")
    subprocess.run(["fuseiso", iso_name, outputdir + "temp/"])

    # Error output when transferring content from ISO-image
    with open(iso_content_log, 'w+') as content_error_file:
        with redirect_stdout(content_error_file):
            shutil.copytree(outputdir + 'temp', outputdir + 'content')
    content_error_file.close()

    # Make sure the temp directory is unmounted, as it belongs to 'root', otherwise temp can not be removed.
    while find_owner(outputdir + "temp/") == "root":
        subprocess.run(["fusermount", "-u", outputdir + "temp"])
        sleep(0.5)
    subprocess.run(["rm", "-rf", outputdir + "temp/"])
    progress_indicator(deviceid, 95)

    # Notify user of completion, both in UI as via physical ejection of media
    drives[deviceid]["console_output"].insert("end-1c", "Done")
    subprocess.run(["eject"])
    progress_indicator(deviceid, 100)

    end_time = datetime.now()

    delta_time = end_time - begin_time
    delta_seconds = int(delta_time.total_seconds())

    # Gather device specific kernel logging that where generated during operation
    with open(iso_sector_log, 'w') as sector_error_file:
        get_sector_log = subprocess.run(["journalctl", "--no-pager", "-kS", "-" + str(delta_seconds) + "sec"],
                                            check=True, capture_output=True)
        subprocess.run(["grep", "sr" + str(deviceid)], input=get_sector_log.stdout, stdout=sector_error_file)
    sector_error_file.close()

    # Now that we are truly done, update the device status
    drives[deviceid]['running'] = False

    # We need a return value to end the thread
    return 0


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
        # Using a lambda function with variables, while iterating, causes all variable to be set to last iteration value
        if drive == 0:
            button_action_0 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(0))
            button_action_0.grid(row=drive, column=10, sticky='E')
        elif drive == 1:
            button_action_1 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(1))
            button_action_1.grid(row=drive, column=10, sticky='E')
        elif drive == 2:
            button_action_2 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(2))
            button_action_2.grid(row=drive, column=10, sticky='E')
        elif drive == 3:
            button_action_3 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(3))
            button_action_3.grid(row=drive, column=10, sticky='E')
        elif drive == 4:
            button_action_4 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(4))
            button_action_4.grid(row=drive, column=10, sticky='E')
        elif drive == 5:
            button_action_5 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(5))
            button_action_5.grid(row=drive, column=10, sticky='E')
        elif drive == 6:
            button_action_6 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(6))
            button_action_6.grid(row=drive, column=10, sticky='E')
        elif drive == 7:
            button_action_7 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(7))
            button_action_7.grid(row=drive, column=10, sticky='E')
        elif drive == 8:
            button_action_8 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(8))
            button_action_8.grid(row=drive, column=10, sticky='E')
        elif drive == 9:
            button_action_9 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(9))
            button_action_9.grid(row=drive, column=10, sticky='E')
        elif drive == 10:
            button_action_10 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(10))
            button_action_10.grid(row=drive, column=10, sticky='E')
        elif drive == 11:
            button_action_11 = tk.Button(text="Run", relief='raised', command=lambda: thread_runner(11))
            button_action_11.grid(row=drive, column=10, sticky='E')

        drives[drive]['prog_label'] = tk.Label(window, text="Voortgang:")
        drives[drive]['prog_label'].grid(row=drive, column=6)

        # Progress bar widget
        drives[drive]['progress'] = Progressbar(window, length=300, mode='determinate')
        drives[drive]['progress'].grid(row=drive, column=7, columnspan=3, sticky='EW')

        # Console Output
        drives[drive]['console_output'] = tk.Text(window, bg='black', fg='white',
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

def open_about_window():
    about_window = tk.Toplevel(window)
    about_window.lift()
    about_window.title("Settings")
    about_window.geometry("200x100")

    title = Label(about_window, text="Optical Media Archive Ripper")
    title.pack()

    version = Label(about_window, text="Version: 0.9")
    version.pack()

    sep = Separator(about_window, orient='horizontal')
    sep.pack()

    rinus = Label(about_window, text="Marinus Collignon")
    rinus.pack()

    marco = Label(about_window, text="Marinus Stroosnijder")
    marco.pack()

    apply_button = tk.Button(
        about_window,
        text="Sluiten",
        command=about_window.destroy
    )
    apply_button.bind('<Button-1>', applysettings)
    apply_button.pack()

# -------------------------------------------------------------------------------------------------------------

window = tk.Tk()
window.title("Optical Media Archive Ripper")
window.geometry(f'{geo_width}x{geo_height}')

menubar = tk.Menu(window)
window.config(menu=menubar)
file_menu = tk.Menu(menubar, tearoff=0)

file_menu.add_command(
    label='Settings',
    command=open_settings_window,
)

file_menu.add_command(
    label='About',
    command=open_about_window,
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

if (os.path.exists('.drive.config') == False):
    drive_config_writer(12)

if (os.path.exists('.output.config') == False):
    output_config_writer("/media")

check_mount_point(output_config_reader())

slidervalue = tk.IntVar()
slidervalue.set(int(drive_config_reader()))
applysettings(True)

if __name__ == '__main__':
    window.mainloop()
