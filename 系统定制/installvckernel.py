# -*- coding: utf-8 -*-


import os
import sys
import time
sys.path.append("/usr/vmd")

from support.fileutil.file_option import FileOption

def get_rootdevice():

    # e.g /dev/mapper/System-root for vcenter ; /dev/mapper/live-rw for vsrever
    file_name = "/etc/mtab"
    lines = FileOption(file_name).read_file()
    for x in lines:
        xlist = x.strip().split()
        if xlist < 2:
            continue
        if x[1] == "/":
            return x[0]
    return "/dev/mapper/System-root"

if __name__ == "__main__":

    baserootdev = get_rootdevice()
    
    os.chroot("/mnt/sysimage")
    
    os.system("rm -rf %s" % baserootdev)

    cmd = "rpm -e mkinitrd-6.0.52-2 --nodeps"
    os.system(cmd)
    time.sleep(3)

    cmd = "rpm -ivh /etc/mkinitrd-5.1.19.6-44.i386.rpm --nodeps"
    ret = os.system(cmd)
    if ret:
        time.sleep(1)
        os.system(cmd)
    time.sleep(2)

    cmd = "rm -rf /sbin/mkinitrd"
    os.system(cmd)
    time.sleep(1)

    cmd = "scp -l 24576 /etc/mkinitrd /sbin/"
    os.system(cmd)
    time.sleep(2)

    cmd = "new-kernel-pkg --mkinitrd --depmod --install `uname -r`"
    os.system(cmd)
    time.sleep(3)

    cmd = "scp -l 24576 /boot/initrd-2.6.18-164.6.1.el5.img /boot/initrd-splash.img"
    os.system(cmd)
    time.sleep(1)

    cmd = "/usr/share/bootsplash/scripts/make-boot-splash /boot/initrd-splash.img 1024*"
    os.system(cmd)
    time.sleep(3)

    cmd = "mv -f /boot/initrd-splash.img /boot/initrd-2.6.18-164.6.1.el5.img"
    os.system(cmd)

    os.chroot(".")
    sys.exit(0)


