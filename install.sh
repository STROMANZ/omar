#!/bin/bash

# Variables
export DIR=$(pwd)
export VERSION=$(lsb_release -r | awk '{print $2}' | awk -F\. '{print $1}')

# A function to stop execution and to inform user of failure
die() {
	echo ${@}
	exit 1
}

if ! [ ${VERSION} -ge 20 ];
then
	die "This software is not compatible, Ubuntu 20(.04) or greater is required"
fi

# Check for local availability of the ripper.desktop file
if [ -f ripper.desktop ];
then
	cp ripper.desktop ~/Desktop
else
	die "ripper.desktop not found"
fi

# Modify local settings to match environment
if [ -f ~/Desktop/ripper.desktop ];
then
	if [ -f ripper.py ];
	then
		sed -i "s,Exec=.*,Exec=${DIR}/ripper.py," ~/Desktop/ripper.desktop
	else
		die "ripper.py not found"
	fi

	if [ -f cd.png ];
	then
		sed -i "s,Icon=.*,Icon=${DIR}/cd.png," ~/Desktop/ripper.desktop
	else
		die "cd.png not found"
	fi

	gio set ~/Desktop/ripper.desktop metadata::trusted true
	chmod u+x ~/Desktop/ripper.desktop
fi

# Install Dependencies - UI and userland ISO mount software
sudo apt install python-is-python3
sudo apt install python3-tk || die "installation of python3-tk was unsuccesful"
sudo apt install fuseiso || die "installation of fuseiso was unsuccesful"
