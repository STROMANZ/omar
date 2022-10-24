#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *
import time
import signal
import subprocess
from subprocess import Popen, PIPE

window = tk.Tk()
window.title("CD/DVD imager")
window.geometry('525x245')

def handle_button_exit_press(event):
    window.destroy()

def handle_button_action_press(event):
    try:
        id = int(digitalid.get())
    except:
        messagebox.showerror('Error', 'Error: Dig-ID geen nummer')
        button_action = tk.Button(relief='raised')
    else:
        iso_name = outpath + str(id) + ".iso"
        iso_md5_name = iso_name + ".md5"
        subprocess.run(["umount", "/dev/sr0"])
        progress['value'] = 5
        window.update_idletasks()
        dd = Popen(["dd", "if=/dev/sr0", "of=" + iso_name], stderr=PIPE)
        while dd.poll() is None:
            time.sleep(3)
            dd.send_signal(signal.SIGUSR1)
            while 1:
                line = dd.stderr.readline()
                if 'bytes' in str(line):
                    console_output.delete('1.0',tk.END)
                    console_output.insert("end-1c", line)
                    window.update_idletasks()
                    break
        console_output.insert("end-1c", dd.stderr.readline())
        window.update_idletasks()
        progress['value'] = 40
        window.update_idletasks()
        with open(iso_md5_name, 'w') as chksum_file:
            process = subprocess.Popen(["md5sum", "/dev/sr0"], stdout=chksum_file)
        chksum_file.close()
        progress['value'] = 85
        window.update_idletasks()
        process = subprocess.Popen(["md5sum", "-c", iso_name])
        progress['value'] = 95
        window.update_idletasks()
        subprocess.run(["eject"])
        progress['value'] = 100
        window.update_idletasks()

outpath = "/tmp/"
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
