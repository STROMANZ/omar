#!/usr/bin/python3
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tkinter import filedialog
import os
import time
import signal
import shutil
import subprocess
from subprocess import Popen, PIPE
from types import SimpleNamespace
import threading
window = tk.Tk()
window.title("CD/DVD imager")
window.geometry('1580x860')


class Gui:
    def refresh(self):
        self.window.update()
        self.window.after(1000,self.refresh)

    def start(self):
        self.refresh()
        threading.Thread(target=handle_button_action_press()).start()
        threading.Thread(target=display_selected()).start()

# GUI = Gui(Tk())

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


# ui = {}
# ui_amount = 1
#
# def create_ui_entries(amount):
#     global ui
#     global ui_amount
#     global u
#     u = SimpleNamespace(**ui)
#     while ui_amount <= amount:
#         ui[ui_amount] = {'digitalid':"digitalid" + str(ui_amount),
#                          'inputtxt':"inputtxt" + str(ui_amount),
#                          'IDLabel': "IDLabel" + str(ui_amount),
#                          'button_action': "button_action" + str(ui_amount),
#                          'prog_label': "prog_label" + str(ui_amount),
#                          'progress': "progress" + str(ui_amount),
#                          'console_output': "console_output" + str(ui_amount),
#                          '': "" + str(ui_amount),
#                          '': "" + str(ui_amount),
#                          }
#         ui_amount = ui_amount + 1
#
# create_ui_entries(12)

# def show_entry_fields():
#     print("First %s\nSecond %s\nThird %s" % (inputtxts[0].get(), inputtxts[1].get(), inputtxts[2].get()))

def display_selected(self):
    global number
    global inputtxts
    global inputtxt_x
    number = int(Instance_nr.get())
    inputtxts = []
    for x in range(number):
        global nrx
        nrx = x

        inputtxt_x = tk.StringVar()
        inputtxt = tk.Entry(window, width=30, textvariable=inputtxt_x)
        inputtxt.grid(column=2, row=x)

        print(inputtxts)

        # Label
        IDLabel = tk.Label(window, text="Dig-ID:")
        IDLabel.grid(row=x, column=1)

        # Button Creation
        button_action = tk.Button(text="Run", relief='raised')
        button_action.bind('<Button-1>', handle_button_action_press)
        button_action.grid(row=x, column=10, sticky='E')

        # tk.Button(window, text='Enter', command=show_entry_fields).grid(row=3,
        #                                                               column=1,
        #                                                               sticky=tk.W,
        #                                                               pady=4)

        prog_label = tk.Label(window, text="Voortgang:")
        prog_label.grid(row=x, column=6)

        # Progress bar widget
        global progress
        progress = Progressbar(window, length=300, mode='determinate')
        progress.grid(row=x, column=7, columnspan=3, sticky='EW')

        # Console Output
        global console_output
        console_output = tk.Text(window, bg='black', fg='white', height=3, width=64, insertborderwidth=2)
        console_output.grid(row=x, columnspan=3, column=3, sticky='E')
    # global number
    # number = int(Instance_nr.get())
    # for x in range(number):
    #     # Label
    #     IDLabel = tk.Label(window, text="Dig-ID:")
    #     IDLabel.grid(row=x, column=1)
    #
    #     # TextBox Creation
    #     inputtxt = tk.Entry(window, width=30, textvariable=digitalid)
    #     inputtxt.grid(row=x, column=2)
    #
    #     # Button Creation
    #     button_action = tk.Button(text="Run", relief='raised')
    #     button_action.bind('<Button-1>', handle_button_action_press)
    #     button_action.grid(row=x, column=10, sticky='E')
    #
    #     prog_label = tk.Label(window, text="Voortgang:")
    #     prog_label.grid(row=x, column=6)
    #
    #     # Progress bar widget
    #     global progress
    #     progress = Progressbar(window, length=300, mode='determinate')
    #     progress.grid(row=x, column=7, columnspan=3, sticky='EW')
    #
    #     # Console Output
    #     global console_output
    #     console_output = tk.Text(window, bg='black', fg='white', height=3, width=64, insertborderwidth=2)
    #     console_output.grid(row=x, columnspan=3, column=3, sticky='E')
display_selected
def handle_button_action_press(event):
    try:
        inputtxts.append(inputtxt_x.get())
        print(inputtxts)
        id = int(inputtxts[0])
    except:
        messagebox.showerror('Error', 'Error: Dig-ID geen nummer')
        button_action = tk.Button(window, relief='raised')
        window.update_idletasks()
    else:
        ### Change the variable outpath to modify the output path
        outpath = output + "/" + str(id) + "/"
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
                    console_output.delete('1.0', tk.END)
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
            process = subprocess.run(["md5sum", iso_name], stdout=chksum_file)
        chksum_file.close()
        md5_b = checksum_from_file(iso_md5_name)
        md5sum_compare(md5_a, md5_b)
        progress_indicator(70)
        console_output.insert("end-1c", "Checksum validatie succesvol" + '\n')
        window.update_idletasks()
        progress_indicator(75)
        create_directory(outpath + "temp/")
        subprocess.run(["fuseiso", iso_name, outpath + "temp/"])
        shutil.copytree(outpath + "temp", outpath + "content")
        subprocess.run(["fusermount", "-u", outpath + "temp"])
        subprocess.run(["rm", "-rf", outpath + "temp/"])
        progress_indicator(95)
        subprocess.run(["eject"])
        console_output.insert("end-1c", "Done")
        progress_indicator(100)

optical_device = "/dev/sr0"
digitalid = tk.StringVar()
output = "/home/users/u00c788/Desktop/"
def select_dir(event):
    global output
    output = tk.filedialog.askdirectory(initialdir="/media/", )

# Instance Number
inst_nr = range(0, 13)

Instance_nr = StringVar()
Instance_nr.set(inst_nr[0])

drop_inst = OptionMenu(window, Instance_nr, *inst_nr, command=display_selected)
drop_inst.pack(expand=True)
drop_inst.grid(row=0, column=0)

# Output Directory
Nav_button = tk.Button(text="Output", relief='raised')
Nav_button.bind('<Button-1>', select_dir)
Nav_button.grid(row=0, column=20, sticky='E')

# Button Exit
button_exit = tk.Button(text="Exit")
button_exit.bind('<Button-1>', handle_button_exit_press)
button_exit.grid(row=25, column=20, sticky='E')

# Start the event loop.
window.mainloop()