#!/usr/bin/env Python
# -*- coding: utf8 -*-

import os, sys, re
import locale
locale.setlocale(locale.LC_ALL, '')

from TerminalUI import Base, TipsBox

sys.path.append("/usr/vmd")
from FronOSUI_interface import *

def is_vs():

    file_name = "/etc/vcenter_uuid"
    if os.access(file_name, os.F_OK):
        fd = file(file_name)
        lines = fd.readlines()
        fd.close()
        if lines:
            if "127.0.0.1" == "".join(lines).strip():
                return False
    return True

class Action(Base):
    def __init__(self):
        Base.__init__(self)

    def _WalkToNextWidget(self, simpleListWalker):
        """Internal fuction that take focut to next widget in simpleListWalker"""

        widget, position = simpleListWalker.get_focus()
        simpleListWalker.set_focus(position + 1)

    def GetSystemVersionInformation(self):

        #return u"这里放置版本信息"
        if is_vs():
            prev = "vServer"
        else:
            prev = "vCenter"
        return u"%s %s" % (prev, get_version())

    def GetSystemTipsInformation(self):
        #return u"这里放置提示信息"

        return u"支持系统简单网络配置"

    def UserLogin(self, username, password):
        """userData is a list which contain username and password"""
        param = {}
        param["user"] = username
        param["password"] = password
        if login(param):
            # e.g successed
            return 1
        # e.g failed
        return 0

    def ChangePassword(self, simpleListWalker, param):
        """To change user password
        simpleListWalker is the widget which stored all password change widgets
        """

        #tips = u"设置用户密码..."
        #tipsBox = TipsBox(simpleListWalker)

        #tipsBox.SetTips(tips)

        #tipsBox.AddTips(tips)
        #tipsBox.DeleteTips()

        strs = u"成功"
        if not change_password(param):
            strs = u"失败"
            return False
        return True

        #tipsBox.AddTips(strs)

        #self._WalkToNextWidget(simpleListWalker)

    def GetNetworkAdapterList(self):

        return get_network_adapterlist()

    def GetChosenDevIP(self, networkAdapterList):

        return get_chosen_dev_IP(networkAdapterList)

    def LockDownStateChange(self, simpleListWalker):
        """Change LockDown state"""

        raise RuntimeError, "We are in LockDown State Change Function"

    def ManagementNetworkAdapter(self, simpleListWalker, adapterWidget, state):
        """Management Network Adapter Configuration
        adapterWidget       The widget for adapter information
        state               Changed state of given adapter
        Notics:
            From adapterWidget.get_state() to get initial state for given adapter
            And state is changed adapter state which the user want to set
        """

        #net_dev_name = adapterWidget.get_label()
        #print net_dev_name, state
        
        # e.g state 表示接口是否选中, True为选中，False为非选中。


        #tips = u"开始处理网络接口"
        #tipsBox = TipsBox(simpleListWalker)
    
        #tipsBox.SetTips(tips)
#        tipsBox.DeleteTips()
#        self._WalkToNextWidget(simpleListWalker)

    def SetVLANNumber(self, simpleListWalker, vlanNumber):
        """Setup VLAN number"""
        raise RuntimeError, (vlanNumber)

    def SetIPv4StaticAddress(self, simpleListWalker, ipaddr, netmask, gateway, networkAdapterList):
        """Setup IPv4 static address"""
        output = (False, "")
        try:
            # e.g vc db will be disconnnect, and then raise error
            output = set_IPv4(ipaddr, netmask, gateway, networkAdapterList)
        except:
            pass
        return output
#        raise RuntimeError, (ipaddr, netmask, gateway, networkAdapterList)

    def SetIPv6StaticAddress(self, simpleListWalker, ipaddr1, ipaddr2, ipaddr3, gateway):
        """Setup IPv6 static address"""

        raise RuntimeError, (ipaddr1, ipaddr2, ipaddr3, gateway)


    def GetDnsHostnameGateway(self):

        return get_net_basic()

    def SetIPv4DNSAddress(self, simpleListWalker, dnsAddr1, dnsAddr2, hostname, gateway):
        """Setup IPv4 DNS server address"""
        
        #raise RuntimeError, (dnsAddr1, dnsAddr2, dnsAddr3, )
        params = {
            "hostname":hostname, 
            "main":dnsAddr1, 
            "sub":dnsAddr2, 
            "gateway":gateway
        }
        output = set_net_basic(params)
        if output[0]:
            return True
        return False

    def SubmitAllManagementNetworkSetting(self, simpleListWalker, confDict):
        raise RuntimeError, confDict

    def RestartManagementNetwork(self, simpleListWalker):

        return restart_network()

        #raise RuntimeError, "We are in Restart Management Network function"

    def TestManagementNetworkPing(self, simpleListWalker, ipAddr):
        """ipAddr is an IP address used to test"""

        return run_ping(ipAddr)

        #raise RuntimeError, "We are in Test Management Network function for ping %s" % ipAddr

    def TestManagementNetworkResolveHostname(self, simpleListWalker, addr):
        """addr is an hostname need to resolve"""

        raise RuntimeError, "We are in Test Management Network function for hostname resolve %s" % addr

    def TestManagementNetworkSubmitAllActions(self, simpleListWalker, confDict):

        raise RuntimeError, confDict

    def RestoreNetworkFactorySetting(self, simpleListWalker):
        
        raise RuntimeError, "We are in Restore Factory Setting function"

    def KeyboardLayoutSetting(self, simpleListWalker, keyboardLayout):
        """keyboardLayout is a layout string"""

        raise RuntimeError, "We are in Keyboard Layout Setting funtion"

    def TroubleShootingOpenESXi(self, simpleListWalker, currentState):
        
        raise RuntimeError, "We are in Trouble Shooting to open ESXi"

    def TroubleShootingCloseESXi(self, simpleListWalker, currentState):
        
        raise RuntimeError, "We are in Trouble Shooting to close ESXi"

    def TroubleShootingOpenSSH(self, simpleListWalker, currentState):
        
        raise RuntimeError, "We are in Trouble Shooting to open SSH"

    def TroubleShootingCloseSSH(self, simpleListWalker, currentState):
        
        raise RuntimeError, "We are in Trouble Shooting to close SSH"

    def ViewSystemLog(self, simpleListWalker):
        """This function must return a string which content all system log"""
        
        return "We are in View System Log"

    def ViewVMKernelLog(self, simpleListWalker):
        """This function must return a string which content all VM Kernel log"""
        
        return "We are in View VM Kernel Log"

    def ViewConfigLog(self, simpleListWalker):
        """This function must return a string which content all Config log"""
        
        return "We are in View Config Log"

    def ViewManagementAgentLog(self, simpleListWalker):
        """This function must return a string which content all Management Network Agent log"""
        
        return "We are in View Management Network Agent Log"

    def ViewVirtualCenterAgentLog(self, simpleListWalker):
        """This function must return a string which content all Virtual Center Agent log"""
        
        return "We are in View Virtual Center Agent Log"

    def ViewESXiObservationLog(self, simpleListWalker):
        """This function must return a string which content all ESXi Observation log"""
        
        return "We are in View ESXi Observation Log"

    def ViewSupportInformation(self, simpleListWalker):
        """Return Support Information string"""

        return "We are in View Support Information function"

    def ResetSystem(self, simpleListWalker):
        """Support system restart."""
        reboot()

    def PoweroffSystem(self, simpleListWalker):
        """Support system poweroff."""
        poweroff()

    def ResetSystemConfiguration(self, simpleListWalker):
        raise RuntimeError, "We are in Reset Whole System Configuration function"

    def ToShell(self):

        to_shell()
        raise RuntimeError, "To debug mod."

    def GetDefaultVswitchIP(self):

        return get_default_vswitch_ip()


