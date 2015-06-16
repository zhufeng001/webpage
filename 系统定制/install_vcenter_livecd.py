# -*- coding: utf-8 -*-


import os
import time
import syslog
import subprocess

import support.cmd_pipe
import optevent_db_op
import check_install_tohd

from support.fileutil.file_option import FileOption
from support.fileutil.dir_option import DirOption

def check_create_parttion(event):

    params = {}
    harddisk = event.param["harddisk"]
    bootdisk = event.param["bootdisk"]
    bootsize = event.param["bootsize"]
    rootdisk = event.param["rootdisk"]
    rootsize = event.param["rootsize"]

    if ("/dev/sd" not in harddisk) and ("/dev/cciss" not in harddisk):
        if ("/dev/hd" not in harddisk):
            return (False, "HardDisk only support SCSI/IDE")

    if float(bootsize) < 300:
        return (False, "Bootparttion size must be large than 300M")
    if float(rootsize) < 10240:
        return (False, "Rootparttion size must be large than 10G")

    params["bootdisk"] = bootdisk
    params["bootsize"] = bootsize
    params["rootdisk"] = rootdisk
    params["rootsize"] = rootsize
    return (True, params)

def clear_tmp_dir():

    dirlist = ["/mnt/tmp", "/mnt/sysimage"]
    for x in dirlist:
        cmd = "/bin/rm -rf %s/*" % x
        os.system(cmd)
    return (True, "")

def create_bootdisk_fs(bootdisk):

    cmd = "/sbin/mkfs -t ext3 %s" % bootdisk
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 1200)
    if not cmdstat:
        return (False, "Mkfs bootdisk failed") #@@
    time.sleep(1)
    return (True, "Create bootdisk fs finished")

def makedir(instPath):

#    filepathlist = ["%s/boot" % instPath, "%s/dev/mapper" % instPath, "%s/dev/volgroup" % instPath, "%s/etc/lvm" % instPath, "%s/proc" % instPath, "%s/sys" % instPath]
    filepathlist = ["%s/boot" % instPath, "%s/dev/mapper" % instPath, "%s/etc/lvm" % instPath, "%s/proc" % instPath, "%s/sys" % instPath]
    for dir_name in filepathlist:
        (flag, stat) = DirOption(dir_name).create_dir()
        if not flag:
            return (False, stat)
    return (True, "Create dirs sucessed")

def get_rootdevice():

    # e.g means nouse loop dev
#    rootdev = "/dev/loop3"
#    return rootdev

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

def _getLiveSize(device):

#    return int(inclutesec)*512
    def parseField(output, field):
        for line in output:
            line = line.split("\n")[0]
            if line.startswith(field + ":"):
                return (True, line[len(field) + 1:].strip())
        return (False, "Not include this strs %s" % field)

    cmd = "/sbin/dumpe2fs -h %s" % device
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, rparams["stderr"])

    (flag, blkcnt) = parseField(rparams["stdout"], "Block count")
    if not flag:
        return (False, blkcnt)
    (flag, blksize) = parseField(rparams["stdout"], "Block size")
    if not flag:
        return (False, blksize)
    tsize = int(blkcnt) * int(blksize)
    return tsize

def doInstall(stt, ppc, rootdisk, event):

    rootdevice = get_rootdevice()
    percentage = stt
    trootsize = _getLiveSize(rootdevice)
    root_osimg = os.path.normpath(rootdevice)
    osfd_root = os.open(root_osimg, os.O_RDONLY)
    rootfd = os.open(rootdisk, os.O_WRONLY)

    os.lseek(osfd_root, 0, 0)
    os.lseek(rootfd, 0, 0)
    copied = 0
    percentage_s = "0"

    # set the rootdisk to have the right type.  this lets things work
    readamt = 1024*1024*8 # 8 megs at a time
    while copied < trootsize:
        time.sleep(0.1)
        try:
            buf = os.read(osfd_root, readamt)
            written = os.write(rootfd, buf)
        except:
            os.lseek(osfd_root, 0, 0)
            os.lseek(rootfd, 0, 0)
            copied = 0
            percentage_s = "0"
            syslog.syslog(syslog.LOG_ERR,'INSTALL TO HARDDISK ERROR,REWRITE HARDDISK DEVICE.')
            continue

        if (written < readamt) and (written < len(buf)):
            return (False, "Error copying filesystem!") #@@
        if (written < readamt) and (written == len(buf)):
            syslog.syslog(syslog.LOG_ERR,'INSTALL TO HARDDISK written %d' % written)
            syslog.syslog(syslog.LOG_ERR,'INSTALL TO HARDDISK copied %d' % copied)
#            return (False, "error copying filesystem!")

        copied += written
        try:
            pct = copied/float(trootsize)
            percentage_cur = int(pct*ppc)
            if (percentage_cur - int(percentage_s)) >= 1:
                percentage_s = "%d" % percentage_cur
                npercentage = percentage + int(percentage_s)
                updateinfo = {"uuid":event.uuid,"progress":npercentage}
                optevent_db_op.update_optevent(updateinfo)
        except:
            pass
    os.close(osfd_root)
    os.close(rootfd)
    return (True, "Install successed")

def _resizedevicefs(device):

    # we should also do a fsck afterwards
    cmd = ["e2fsck", "-f", "-y", device]
    out = os.open("/dev/tty5", os.O_WRONLY)
    proc = subprocess.Popen(cmd, stdout=out, stderr=out)
    rc = proc.poll()
    while rc is None:
        time.sleep(0.5)
        rc = proc.poll()
    time.sleep(15)

    cmd = ["resize2fs", device, "-p"]
    out = os.open("/dev/tty5", os.O_WRONLY)
    proc = subprocess.Popen(cmd, stdout=out, stderr=out)
    rc = proc.poll()
    while rc is None:
        time.sleep(0.5)
        rc = proc.poll()
    time.sleep(15)
    return (True, "")

def get_partition_fsuuid(device):

    cmd = "tune2fs -l " + device
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, "get deviceuuid failed " + device)
    lines = rparams["stdout"]
    for x in lines:
        if "Filesystem UUID:" in x:
            return (True, x.strip().split()[-1])
    return (False, "get deviceuuid failed " + device)

def remountfile(instPath, rootdisk, bootdisk):

    os.chdir("/")
    cmd = "/bin/rm -rf %s/*" % instPath
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 1200)
    if not cmdstat:
        return (False, "Delete tmp file failed") #@@

    cmd = "/bin/mount -t ext3 %s %s" % (rootdisk, instPath)
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, "Mount devroot failed") #@@

    mbp = "/mnt/sysimage/mnt/boot"
    (flag, stat) = DirOption(mbp).create_dir()
    if not flag:
        return (False, stat)

    cmd = "scp -l 24576 -r /mnt/sysimage/boot/* /mnt/sysimage/mnt/boot/"
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 1200)
    if not cmdstat:
        return (False, "Cp bootfile failed") #@@

    cmd = "/bin/rm -rf /mnt/sysimage/boot/*"
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 1200)
    if not cmdstat:
        return (False, "Rm boot tmp file failed") #@@

    cmd = "/bin/mount -t ext3  %s  /mnt/sysimage/boot" % bootdisk
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, "Mout boot dev failed") #@@

    cmd = "scp -l 24576 -r /mnt/sysimage/mnt/boot/* /mnt/sysimage/boot/"
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 1200)
    if not cmdstat:
        return (False, "Cp boot file failed") #@@

    cmd = "/bin/mount -t sysfs /sys  %s/sys" % instPath
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, "Mount sysfs failed") #@@

    cmd = "/bin/mount -t proc  /proc %s/proc" % instPath
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, "Mount proc failed") #@@

    cmd = "/bin/mount --bind /dev %s/dev" % instPath
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    if not cmdstat:
        return (False, "Mount bind failed") #@@
    return (True, "Remount successed")

def _get_fstab(rootuuid, bootuuid):

    strs = '''UUID=%s /                       ext3    defaults        1 1
UUID=%s /boot                   ext3    defaults        1 2
tmpfs                   /dev/shm                tmpfs   defaults        0 0
devpts                  /dev/pts                devpts  gid=5,mode=620  0 0
sysfs                   /sys                    sysfs   defaults        0 0
proc                    /proc                   proc    defaults        0 0
''' % (rootuuid, bootuuid)
    file_name = "/proc/swaps"
    lines = FileOption(file_name).read_file()
    if len(lines) > 1:
        swp = lines[1].split()[0]
        strs += "%s     swap    swap     defaults         0 0\n" % swp
    return strs

def _get_mtab(rootdisk, bootdisk):

    s = '''%s / ext3 rw 0 0
proc /proc proc rw 0 0
sysfs /sys sysfs rw 0 0
devpts /dev/pts devpts rw,gid=5,mode=620 0 0
tmpfs /dev/shm tmpfs rw 0 0
%s /boot ext3 rw 0 0
none /proc/sys/fs/binfmt_misc binfmt_misc rw 0 0
sunrpc /var/lib/nfs/rpc_pipefs rpc_pipefs rw 0 0
''' % (rootdisk, bootdisk)
    return s

def doPostInstall(instPath, rootdisk, bootdisk):

    (flag, stat) = _resizedevicefs(rootdisk)
    if not flag:
        return (False, stat)

    # e.g get rootdisk, bootdisk filesystem uuid
    # e.g tune2fs -l /dev/sda1
    (flag, rootuuid) = get_partition_fsuuid(rootdisk)
    if not flag:
        return (False, rootuuid)
    (flag, bootuuid) = get_partition_fsuuid(bootdisk)
    if not flag:
        return (False, bootuuid)

    # remount filesystems
    (flag, stat) = remountfile(instPath, rootdisk, bootdisk)
    if not flag:
        return (False, stat)

    # now write out the "real" fstab and mtab
    file_name = "/mnt/sysimage/etc/fstab"
    strs = _get_fstab(rootuuid, bootuuid)
    FileOption(file_name).write_file(strs)

    file_name = "/mnt/sysimage/etc/mtab"
    strs = _get_mtab(rootdisk, bootdisk)
    FileOption(file_name).write_file(strs)

    diskinfo = {"rootuuid":rootuuid, "bootuuid":bootuuid}
    return (True, diskinfo)

def _get_grub_conf(bootdnum, rootuuid):
    s = '''default=0
timeout=0
hiddenmenu
title Fronware (2.6.i386)
        root (hd0,%s)
        kernel /vmlinuz-2.6.18-164.6.1.el5 ro root=UUID=%s quiet splash=silent vga=791
        initrd /initrd-2.6.18-164.6.1.el5.img
''' % (bootdnum, rootuuid)
    return s

def syncDataToDisk(mntpt):

    cmd = "/bin/sync"
    support.cmd_pipe.run_and_read_cmd(cmd, 30)
    return (True, "")

def install_grub(harddisk, bootdisk, bootdnum):

    strs = "(hd0)   %s\n" % harddisk
    file_name = "/mnt/sysimage/boot/grub/device.map"
    FileOption(file_name).write_file(strs)

    syncDataToDisk("/mnt/sysimage/boot")

    # copy the stage files over into xxx/boot
    cmd = "/sbin/grub-install --just-copy --root-directory=/mnt/sysimage"
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 300)
    if not cmdstat:
        return (False, "Grub-install cmd failed")
    syncDataToDisk("/mnt/sysimage/boot")
    time.sleep(5)

    cmd = "root (hd0,%s)\ninstall /grub/stage1 d (hd0) /grub/stage2 p (hd0,%s)/grub/grub.conf" % (bootdnum, bootdnum)
    p = os.pipe()
    os.write(p[1], cmd + '\n')
    os.close(p[1])

    cmd = "/sbin/grub --batch --no-floppy --device-map=/mnt/sysimage/boot/grub/device.map"
    (cmdstat, rparams) = support.cmd_pipe.r_and_r_cmd_include_in(cmd, 600, p[0])
    os.close(p[0])
    if not cmdstat:
        return (False, "Grub batch failed") #@@
    # e.g change harddiskname in devicemapf for grub
    strs = "(hd0)   %s\n" % check_install_tohd.get_first_HD_name(harddisk)
    file_name = "/mnt/sysimage/boot/grub/device.map"
    FileOption(file_name).write_file(strs)
    return (True, "")

def setup_grub(bootdisk, harddisk, rootuuid):

    bootdnum = check_install_tohd.get_numof_device(bootdisk)
    bootdnum = str(int(bootdnum) - 1)

    file_name = "/mnt/sysimage/boot/grub/grub.conf"
    strs = _get_grub_conf(bootdnum, rootuuid)
    FileOption(file_name).write_file(strs)

    os.chdir("/mnt/sysimage/boot/grub/")
    cmd = "/bin/ln -s ./grub.conf ./menu.lst"
    (cmdstat, rparams) = support.cmd_pipe.run_and_read_cmd(cmd, 30)
    os.chdir("/usr/vmd")
    if not cmdstat:
        return (False, "Create ln grub.conf failed") #@@

    (flag, stat) = install_grub(harddisk, bootdisk, bootdnum)
    if not flag:
        return (False, stat)
    return (True, "Create Cfg successed")

def umount_tmp_mount():

    umlist = ["/mnt/sysimage/boot", "/mnt/sysimage/dev", "/mnt/sysimage/proc", "/mnt/sysimage/sys"]
    for ump in umlist:
        cmd = "umount -f %s" % ump
        os.system(cmd)
    cmd = "umount -f /mnt/sysimage"
    os.system(cmd)
    return (True, "")

def installvcenter(event):

    instPath = "/mnt/sysimage"
    harddisk = event.param["harddisk"]

    (flag, params) = check_create_parttion(event)
    if not flag:
        return (False, params)

    bootdisk = params["bootdisk"]
    rootdisk = params["rootdisk"]
    bootsize = params["bootsize"]
    rootsize = params["rootsize"]

    clear_tmp_dir()

    (flag, stat) = create_bootdisk_fs(bootdisk)
    if not flag:
        return (False, stat)

    (flag, stat) = makedir(instPath)
    if not flag:
        return (False, stat)

    ppc = 80 - 20
    stt = 20
    (flag, stat) = doInstall(stt, ppc, rootdisk, event)
    if not flag:
        return (False, stat)

    # e.g diskinfo = {"rootuuid":rootuuid, "bootuuid":bootuuid}
    (flag, diskinfo) = doPostInstall(instPath, rootdisk, bootdisk)
    if not flag:
        return (False, diskinfo)
    rootuuid = diskinfo["rootuuid"]
    bootuuid = diskinfo["bootuuid"]

    updateinfo = {"uuid":event.uuid,"progress":85}
    optevent_db_op.update_optevent(updateinfo)
    
    updateinfo = {"uuid":event.uuid,"progress":90}
    optevent_db_op.update_optevent(updateinfo)

    os.system("/bin/sync")
    time.sleep(20)
    # e.g install for vcenter kernel install
    os.system("/usr/bin/python /usr/vmd/installvckernel.pyc")
    os.system("/bin/sync")
    time.sleep(20)
    
    (flag, stat) = setup_grub(bootdisk, harddisk, rootuuid)
    if not flag:
        return (False, stat)
    
    file_name = "/mnt/sysimage/etc/installtype.txt"
    FileOption(file_name).write_file("HardDisk")
    
    updateinfo = {"uuid":event.uuid,"progress":95}
    optevent_db_op.update_optevent(updateinfo)
    
    umount_tmp_mount()

    return (True, "Successed")


