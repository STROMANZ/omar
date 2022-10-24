#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *
import os
import time
import signal
import shutil
import subprocess
from subprocess import Popen, PIPE

window = tk.Tk()
window.title("CD/DVD imager")
window.geometry('525x245')

def checksum_from_file(file_name):
    file = open(file_name, 'r')
    line = file.readline()
    sum = line.split()
    return(sum[0])

def md5sum_compare(media_md5, iso_md5):
    if (str(media_md5) != str(iso_md5)):
        console_output.insert("end-1c", "Het gemaakte iso bestand komt niet overeen met het orignele optische media")
        window.update_idletasks()
        return 1

def progress_indicator(number):
    progress['value'] = number
    window.update_idletasks()

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def handle_button_exit_press(event):
    window.destroy()

def handle_button_action_press(event):
    try:
        id = int(digitalid.get())
    except:
        messagebox.showerror('Error', 'Error: Dig-ID geen nummer')
        button_action = tk.Button(window, relief='raised')
        window.update_idletasks()
    else:
	### Change the variable outpath to modify the output path
        outpath = "/home/stromanz/Desktop/" + str(id) + "/"
        create_directory(outpath)
        iso_name = outpath + str(id) + ".iso"
        iso_md5_name = iso_name + ".md5"
        iso_md5_optical_name = iso_name + ".optical.md5"
        subprocess.run(["umount", optical_device])
        progress_indicator(5)
        dd = Popen(["dd", "if=" + optical_device, "of=" + iso_name], stderr=PIPE)
        while dd.poll() is None:
            time.sleep(.3)
            dd.send_signal(signal.SIGUSR1)
            while 1:
                line = dd.stderr.readline()
                if 'bytes' in str(line):
                    console_output.delete('1.0',tk.END)
                    console_output.insert("end-1c", line)
                    window.update_idletasks()
                    break
        progress_indicator(35)
        with open(iso_md5_optical_name, 'w') as chksum_file:
            process = subprocess.run(["md5sum", optical_device], stdout=chksum_file)
        chksum_file.close()
        md5_a = checksum_from_file(iso_md5_optical_name)
        progress_indicator(65)
        with open(iso_md5_name, 'w') as chksum_file:
            process = subprocess.run(["md5sum", iso_name ], stdout=chksum_file)
        chksum_file.close()
        md5_b = checksum_from_file(iso_md5_name)
        md5sum_compare(md5_a, md5_b)
        progress_indicator(70)
        console_output.insert("end-1c", "Checksum validatie succesvol" + '\n')
        window.update_idletasks()
        progress_indicator(75)
        create_directory(outpath + "temp/")
        subprocess.run(["fuseiso", iso_name , outpath + "temp/"])
        shutil.copytree(outpath + "temp", outpath + "content")
        subprocess.run(["fusermount", "-u", outpath + "temp"])
        subprocess.run(["rm", "-rf", outpath + "temp/"])
        progress_indicator(95)
        subprocess.run(["eject"])
        console_output.insert("end-1c", "Done")
        progress_indicator(100)

optical_device = "/dev/sr0"
digitalid = tk.StringVar()

# Label
IDLabel = tk.Label(window, text="Dig-ID:")
IDLabel.grid(row=0, column=0)

# TextBox Creation
inputtxt = tk.Entry(window, width = 30, textvariable=digitalid)
inputtxt.grid(row=0, column=1)

# Button Creation
button_action = tk.Button(text="Run", relief='raised')
button_action.bind('<Button-1>', handle_button_action_press)
button_action.grid(row=0, column=2, sticky='E')

# Empty Line 01
empty_line_01 = tk.Label(window)
empty_line_01.grid(row=1, column=0)

prog_label = tk.Label(window, text="Voortgang:")
prog_label.grid(row=2, column=0)

# Progress bar widget
progress = Progressbar(window, length = 100, mode = 'determinate')
progress.grid(row=2, column=1, columnspan=3, sticky='EW')

# Empty Line 02
empty_line_02 = tk.Label(window)
empty_line_02.grid(row=3, column=0)

# Console Output
console_output = tk.Text(window, bg='black', fg='white', height=5, width=64, insertborderwidth=2)
console_output.grid(row=4, columnspan=3, sticky='E')

# Empty Line 03
empty_line_03 = tk.Label(window)
empty_line_03.grid(row=5, column=0)

# Button Exit
button_exit = tk.Button(text="Exit")
button_exit.bind('<Button-1>', handle_button_exit_press)
button_exit.grid(row=6, column=2, sticky='E')

# Start the event loop.
window.mainloop()
