#!/usr/bin/env python
# -*- coding: utf8 -*-

import os, sys, re
import copy
import time
import commands

import locale
locale.setlocale(locale.LC_ALL, '')

try:
    import urwid
except ImportError, e:
    print e
    sys.exit(1)

import urwid.raw_display

import Interface

class Base(object):
    """Global variable and function"""
    def __init__(self):
        # Color resolution for the window
        self.palette = (
            ('header', 'white', 'black'),
            ('reveal focus', 'black', 'dark cyan', 'standout'),
            ('banner', 'black', 'light gray', 'standout,underline'),
            ('streak', 'black', 'dark red', 'standout'),
            ('bg', 'black', 'brown'),
            ('standard', 'white', 'black'),
        )

        # Main configuration file
        self.mainConfDict   = self.GetConfiguration('./TerminalUI.conf')
        self.maxLoginFailCounter = 3

        # Divider string to seperate main menu
        self.dividerStr     = " "
        self.buttonWidth    = 20

        # Temporary file or state file
        self.temporaryFile = {'rootDir': '/tmp/TerminalUI'}
        self.temporaryFile['loginState'] = os.path.join(self.temporaryFile['rootDir'], "LoginState")

    def GetConfiguration(self, confFile):
        """To take all main configuration from configure file"""
        
        if not os.path.isfile(confFile):
            raise RuntimeError, u"设置文件 '%s' 不存在" % confFile

        mainConfDict = {}

        fp = open(confFile, 'r')
        commentPattern = re.compile(r'\s*#')
        splitPattern = re.compile(r'=')
        for line in fp:
            # Skip comment line
            if re.match(commentPattern, line):
                continue

            # Split and get pair of keyword and value
            m = re.split(splitPattern, line)
            if len(m) != 2:
                continue

            keyword = m[0].strip()
            value   = m[1].strip()

            mainConfDict[keyword] = value

        return mainConfDict

    def AlignButtonText(self, tips, mode = 'center'):
        """To align text in button"""

        tipsLen = len(tips)
        if tipsLen > self.buttonWidth:
            return tips

        # decrease 4 characters for button left/right <> character
        if mode == 'center':
            blankLen = ((self.buttonWidth - 4) / 2) - (tipsLen)
            tips = " " * blankLen + tips
        else:
            pass

        return tips

    def FileReadLines(self, filename, newLine = "yes"):
        """Return a list which contain all lines for given file.
        Parameter:
        filename        The path of a text file
        """

        try:
            fileId = open(filename, 'r')
        except IOError, e:
            print('Could not open file: %s' % e)
            return []

        lines = fileId.readlines()
        fileId.close()

        if newLine == 'no':
            newLines = []
            for line in lines:
                newLines.append(line.rstrip())
            lines = newLines

        return lines

    def FileWriteLines(self, filename, lines, newline = 'yes'):
        """Write given lines into a file, it will erase given file if exists.
        Two parameter must be set:
        filename        The path of file which will be write.
        lines           The contain list which will be writing to.
        Extra parameter:
        newline         <yes|no> Add '\n' in every line if set to 'yes'
        return:
        No return.
        """

        writeLineList = []

        if newline == 'yes':
            for line in lines:
                writeLineList.append("%s\n" % line)
        else:
            writeLineList = lines

        try:
            fd = open(filename, 'w')
        except IOError, e:
            print('Could not open file: %s' % e)
            return None

        fd.writelines(writeLineList)
        fd.close()

    def FileAddLines(self, filename, lines, newline = 'yes'):
        """Add given lines into a file.
        Two parameter must be set:
        filename        The path of file which will be write.
        lines           The contain list which will be writing to.
        Extra parameter:
        newline         <yes|no> Add '\n' in every line if set to 'yes'
        return:
        No return.
        """

        writeLineList = []
        if newline == 'yes':
            for line in lines:
                writeLineList.append("%s\n" % line)
        else:
            writeLineList = lines

        try:
            fd = open(filename, 'a')
        except IOError, e:
            print('Could not open file: %s' % e)
            return None

        fd.writelines(writeLineList)
        fd.close()


class TipsBox(object):
    """Create a LineBox and insert it to a simpleListWalker, and you can put some 
    tips into this LineBox. This is a simple way to notices customer persently 
    processing.
    """

    def __init__(self, simpleListWalker):
        """Create/Initial an empty LineBox
        simpleListWalker must be a urwid.SimpleListBox widget
        """
        self.simpleListWalker = simpleListWalker

        self.Create()

    def Create(self):
        """Just create a empty tips box"""

        self.tipsText = urwid.Text(u"")
        self.tipsLineBox = urwid.LineBox(self.tipsText)

        # Insert to simpleListWalker
        widget, position = self.simpleListWalker.get_focus()
        #raise RuntimeError, (widget, position)

        # Uncomment below statement to make TipsBox bottom
        # self.simpleListWalker.append(tipsLineBox)

        # Insert TipsBox above focus widget. (Default)
        self.simpleListWalker.insert(position, self.tipsLineBox)

        # Uncomment below statement to insert TipsBox below focus widget
        # self.simpleListWalker.insert(position + 1, self.tipsLineBox)

    def AddTips(self, str):
        """Add new tips, previous tips still exists, new string will 
        insert to new line"""

        previousString = self.tipsText.get_text()[0]
        self.tipsText.set_text(previousString + str)

    def SetTips(self, str):
        """Set new tips, it means previous tips will be deleted"""

        self.tipsText.set_text(str)


    def DeleteTips(self):
        """Delete tips box"""

        self.simpleListWalker.remove(self.tipsLineBox)
 
class ConfigAndView(Base):
    def __init__(self):
        Base.__init__(self)

        # Here is the main menu in windows left.
        # Notice the last itme of the menu list must be u'退出程序'

        self.mainMenuList = (

            # Blank element will create a dividual line (must be blank character)
            u"密码设置", 
            #u'锁定模式设置', 
            '',

            u'设置管理网络', 
            u'重启管理网络',
            u'测试管理网络', 
            #u'网络设置恢复', 
            '',

            #u"键盘设置", 
            #u"故障检测设置", 
            #'',

            #u"查看系统日志", 
            #u"查看支持信息", 
            #'',

            #u"查看已修改的设置", 
            #u"恢复系统设置",
            #'',

            u"系统重启", 
            u"系统关闭", 
            '',

            # The last element must be "Quit the program"
            u'退出设置界面',
        )



        self.describe = u"系统设置..."

        # Consider may have more configuration files need to handle,
        # create a variable 'self.wholeConfDict' to store all configuration.
        self.wholeConfDict = {}
        self.wholeConfDict.update(self.mainConfDict)

        # self.modifiedConfDict is a mirror variable from self.wholeConfDict.
        # All user changed configure will store at here temporarily.
        # This temporary variable will be merged into wholeConfDict by user
        # action 'save' happened.
        self.modifiedConfDict = copy.deepcopy(self.wholeConfDict)

        # Edit widget used to let user change there configuration.
        # So we store all Edit widget in below variable and go over these 
        # widgets to see the new configuration.
        self.allEditWidget = {}

        # Default width with configuration window. The window is which press 
        # has into 
        self.paneWidth = 30

        # Action for real work
        self.action = Interface.Action()

    def PaneButtonHandler(self, widget, index):
        """Create sub window according to pane window"""

        #self.statusBar.set_text(u"进入功能: %s | 功能标记: %d" % (self.mainMenuList[index], index))

        if index == 0:
            # Password configuration
            self.CreatePasswordConfWindow()
            
        #elif index == 1:
        #    # Lock mode configuration
        #    self.CreateLockdownWindow()

        elif index == 1:
            # Managerment network configuration
            self.CreateManagementNetworkWindow()

        elif index == 2:
            # Restart managerment network
            self.CreateRestartNetworkWindow()

        elif index == 3:
            # Test managerment network
            self.CreateTestManagementNetworkWindow()

        #elif index == 4:
        #    # Restore network configuration
        #    self.CreateRestoreNetworkSettingWindow()

        #elif index == 5:
        #    # Keyboard configuration
        #    self.CreateKeyboardSettingWindow()

        #elif index == 6:
        #    # Troubleshooting checkout configuration
        #    self.CreateTroubleshootingWindow()

        #elif index == 7:
        #    # View system log
        #    self.CreateViewSystemLogWindow()

        #elif index == 8:
        #    # View support information
        #    self.CreateViewSupportInformationWindow()

        #elif index == 4:
        #    # View modified configuration
        #    self.CreateDiffWindow()

        #elif index == 5:
        #    # Restore system configuration
        #    self.CreateResetSystemConfigurationWindow()

        elif index == 4:
            # Restart system
            self.CreateResetSystemWindow()

        elif index == 5:
            # Poweroff system
            self.CreatePoweroffSystemWindow()

        else:
            # The last entry of self.mainMenuList always be Quit
            i = 0
            for item in self.mainMenuList:
                if len(item) != 0: i += 1
            i -= 1
            
            if index == i:
                # Uncomment below line will Quit program directly 
                raise urwid.ExitMainLoop()

            raise RuntimeError, (u"功能未完成", index)

    def _EraseSubWindow(self):
        """Take all value from editable widgets and then remove sub window"""

        # Before remove the window, we must get all user configure
        # The user configure will be stored at self.modifiedConfDict temporarily
        try:
            for key in self.modifiedConfDict:
                self.modifiedConfDict[key] = self.allEditWidget[key].get_edit_text()
        except KeyError, e:
            pass
        
        if len(self.bodyArea.widget_list) >= 2:
            eraseableWidgetList = self.bodyArea.widget_list[1:]
            for widget in eraseableWidgetList:
                self.bodyArea.widget_list.remove(widget)

        return None

    def _GoToMainMenu(self, widget):
        """Move cursor back to main menu, and will focus on previous position"""
        
        focusWidget, position = self.mainMenuListWalker.get_focus()
        self.bodyArea.move_cursor_to_coords((self.paneWidth,), 1, position)

    def _AlignLabels(self, labelList):
        """Get give label list and return a list that all label have same width"""

        newLabelList = []

        # Get max label width
        length = 0
        for label in labelList:
            labelLen = len(label)
            if labelLen > length: length = labelLen

        for label in labelList:
            newLabelList.append(label + " " * (length - len(label)) * 2)

        return newLabelList

    def CreatePasswordConfWindow(self, widget=None):
        """Create a sub window to configure user password"""

        def ChangePassword(widget, userData = None):
            """To change user password here"""

            #self.statusBar.set_text(u"开始用户密码设置")
            param = {
                "crpwd":crwidget.get_edit_text(),
                "nwpwd":nwwidget.get_edit_text(),
                "rppwd":rpwidget.get_edit_text(),
            }
            if self.action.ChangePassword(self.simpleListWalker, param):
                describeText.set_text(u"设置用户密码...成功")
            else:
                describeText.set_text(u"设置用户密码...失败")
        
        self._EraseSubWindow()

        content = []
        labelList = self._AlignLabels((u'先前的密码： ', u'新密码： ', u"重复新密码： ",))

        # Describe box
        describeText = urwid.Text(u"用户密码的设置有助于保护未经授权的用户访问主机\n\n\n")
        describeLineBox = urwid.LineBox(describeText)
        content.append(describeLineBox)
        
        # Create widgets for password configure
        content.append(urwid.Divider(self.dividerStr))

        #for label in labelList:
        #    # ride two times 
        #    #widget = urwid.Edit(caption = label, mask = "*")
        #    widget = urwid.Edit(caption = label)
        #    content.append(urwid.AttrMap(widget, None, "reveal focus"))

        crwidget = urwid.Edit(caption = self._AlignLabels((u'原密码： ', u'新密码： ', u"重复新密码： ",))[0], mask = "*")
        content.append(urwid.AttrMap(crwidget, None, "reveal focus"))

        nwwidget = urwid.Edit(caption = self._AlignLabels((u'原密码： ', u'新密码： ', u"重复新密码： ",))[1], mask = "*")
        content.append(urwid.AttrMap(nwwidget, None, "reveal focus"))

        rpwidget = urwid.Edit(caption = self._AlignLabels((u'原密码： ', u'新密码： ', u"重复新密码： ",))[2], mask = "*")
        content.append(urwid.AttrMap(rpwidget, None, "reveal focus"))

        # Button for cancel or confirm
        content.append(urwid.Divider(self.dividerStr))
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        okButton        = urwid.Button(self.AlignButtonText(u'修改密码'), on_press = ChangePassword,)
        cancelButton    = urwid.Button(self.AlignButtonText(u'重置输入'), on_press = self.CreatePasswordConfWindow)

        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        okAttrMap       = urwid.AttrMap(okButton, None, 'reveal focus')
        cancelAttrMap   = urwid.AttrMap(cancelButton, None, 'reveal focus')


        bottomColumn = urwid.GridFlow((returnAttrMap, okAttrMap, cancelAttrMap), 
            self.buttonWidth, 1, 1,align='center',
        )
        content.append(bottomColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateLockdownWindow(self):
        """Create a sub window to show LockDown configure"""

        def StateChange(widget, userData = None):
            self.action.LockDownStateChange(self.simpleListWalker)

        self._EraseSubWindow()

        # Initial lockdown state
        lockdownMode = False

        content = []

        # Describe box
        describeText = urwid.Text(u"锁定模式一旦开启，用户将无法直接访问这台主机\n\n\n")
        describeLineBox = urwid.LineBox(describeText)
        content.append(describeLineBox)
        
        # Create widgets for password configure
        content.append(urwid.Divider(self.dividerStr))
        checkBox = urwid.CheckBox(u"开启锁定模式", state = lockdownMode, on_state_change=StateChange)
        checkBoxAttrMap = urwid.AttrMap(checkBox, None, "reveal focus")
        content.append(checkBoxAttrMap)
        
        content.append(urwid.Divider(self.dividerStr))
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        buttonColumn = urwid.Columns([('fixed', self.buttonWidth, returnAttrMap),])
        content.append(buttonColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateManagementNetworkWindow(self):
        """Create a sub window to show main configure"""

        self._EraseSubWindow()

        def AdapterHandler(widget, state):

            # netdevname = widget.get_label()
            # state = True / False
            # e.g 通过此接口可更新networkAdapterList数组，更新是否选中信息，方便之后配置使用。

            netdevname = widget.get_label()
            for x in networkAdapterList:
                if x[0][1] == netdevname:
                    x[0] = (state, x[0][1])

            #self.action.ManagementNetworkAdapter(self.simpleListWalker, widget, state)

            #import pdb;pdb.set_trace()
            #ChosenDevIP = self.action.GetChosenDevIP(networkAdapterList)
            #if ChosenDevIP:
            #    ip = u"%s" % ChosenDevIP["ip"]
            #    subnet = u"%s" % ChosenDevIP["subnet"]
            #    gateway = u"%s" % ChosenDevIP["gateway"]
            #else:
            #    ip = u""
            #    subnet = u""
            #    gateway = u""
            #dynamicIPAddrEdit.set_edit_text(ip)
            #dynamicSubnetEdit.set_edit_text(subnet)
            #dynamicGatewayEdit.set_edit_text(gateway)


        # Network adapter status list
        # Every element in networkAdapter must be a sub list, and list as below:
        #   [(Device state, DeviceName), Hardware, Label, MAC Address, Status]
        #networkAdapterList = [
        #    [(True, 'vmnic0'), 'Embeded', u'物理网卡', '00:00:00:00:00:00', 'Connected'],
        #    [(False, 'vmnic1'), 'Embeded', u'物理网卡', '11:11:11:11:11:11', 'Connected'],
        #]
        #import pdb;pdb.set_trace()
        networkAdapterList = self.action.GetNetworkAdapterList()

        content = []
        self.managementNetworkWidget = {}
        
        # Network adapter
        networkAdapterDescribeText = urwid.Text(u"网络适配器配置\n\n这里列出设备中所有已被安装的网络适配器，选中的适配器将会在提交配置时加入默认虚拟交换机。\n如果同时选中多个适配器，那么所有适配器将运行于容错模式，并且负载均衡功能将被应用在所有向外发送的网络报文上。")
        networkAdapterDescribeLineBox = urwid.LineBox(networkAdapterDescribeText)
        content.append(networkAdapterDescribeLineBox)

        content.append(urwid.Divider(self.dividerStr))
        # Network adapter table title
        titleStrList = (u'名称', u'模式', u"类型", u"MAC地址", u"状态", u"从属")
        columnWidgetList = []
        for titleStr in titleStrList:
            columnWidgetList.append(urwid.Text(titleStr, align = 'center'))
        column = urwid.Columns(columnWidgetList)
        content.append(column)

        # Network adapter table content
        networkAdapterGroup = []
        for adapter in networkAdapterList:
            i = 0
            columnWidgetList = []
            for item in adapter:
                if i == 0:
                    columnWidgetList.append(urwid.CheckBox(item[1], state = item[0], on_state_change = AdapterHandler))
                    #columnWidgetList.append(urwid.RadioButton(networkAdapterGroup, item[1], state = item[0], on_state_change = AdapterHandler))
                else:
                    columnWidgetList.append(urwid.Text(item, align = 'center'))
                i += 1

            column = urwid.AttrMap(urwid.Columns(columnWidgetList), None, "reveal focus")
            content.append(column)

        content.append(urwid.Divider(self.dividerStr))


        # Vlan configure
        #vlanDescribeText = urwid.Text(u"VLAN配置（可选项）\n\nVLAN是一种在物理网络接口上创建虚拟网络的技术，每个VLAN都相当于一个独立的网络，将网络接口划分到不同的VLAN是一种比物理隔离更灵活、独立、并且低价的选择\n如果您不确定如何配置一个VLAN，请不要在这里做任何配置")
        #vlanDescribeLineBox = urwid.LineBox(vlanDescribeText)

        #def SubmitVlanConf(buttonWidget, userData = None):
        #    if userData is None:
        #        return None

        #    vlanNumber = userData.get_edit_text()
        #    self.action.SetVLANNumber(self.simpleListWalker, vlanNumber)

        #vlanEditWidget = urwid.IntEdit(caption = u"VLAN ID (1-4094, 或者4095将访问所有Vlan): ", default = 4095)
        #vlanEditWidgetAttrMap = urwid.AttrMap(vlanEditWidget, None, "reveal focus")
        #vlanSubmitButton = urwid.Button(self.AlignButtonText(u"    提交设置"), 
        #    on_press = SubmitVlanConf,
        #    user_data = (vlanEditWidget),
        #)
        #vlanSubmitButtonAttrMap = urwid.AttrMap(vlanSubmitButton, None, 'reveal focus')
        #vlanSubmitColumn = urwid.Columns([('fixed', self.buttonWidth, vlanSubmitButtonAttrMap),],)
        
        #content.append(vlanDescribeLineBox)
        #content.append(urwid.Divider(self.dividerStr))
        #content.append(vlanEditWidgetAttrMap)
        #content.append(vlanSubmitColumn)
        #content.append(urwid.Divider(self.dividerStr))

        # IP configure
        ipConfDescribeText = urwid.Text(u"配置虚拟交换机vswitch0，成员修改和IPv4地址修改.修改后请重新进入该页面刷新")
        ipConfDescribeLineBox = urwid.LineBox(ipConfDescribeText)
        content.append(ipConfDescribeLineBox)

        def StaticAddress(widget, state, userData = None):

            if userData is None:
                return None

            simpleListWalker, position = self.simpleListWalker.get_focus()
            widgetList = userData
            position += 1

            if state:
                for widget in widgetList:
                    if widget in self.simpleListWalker.contents:
                        continue
                    else:
                        self.simpleListWalker.insert(position, widget)
                        position += 1
            else:
                for widget in widgetList:
                    if widget in self.simpleListWalker.contents:
                        self.simpleListWalker.contents.remove(widget)

        def InitStaticDefaultVswitchIP():

            DefaultVswitchIP = self.action.GetDefaultVswitchIP()
            if DefaultVswitchIP:
                ip = u"%s" % DefaultVswitchIP["ip"]
                subnet = u"%s" % DefaultVswitchIP["subnet"]
                gateway = u"%s" % DefaultVswitchIP["gateway"]
            else:
                ip = u""
                subnet = u""
                gateway = u""
            dynamicIPAddrEdit.set_edit_text(ip)
            dynamicSubnetEdit.set_edit_text(subnet)
            #dynamicGatewayEdit.set_edit_text(gateway)

        def SubmitIPv4StaticAddressConf(widget, userData=None):
            if userData is None:
                return None

            #ipaddrWidget, subnetWidget, gatewayWidget = userData
            ipaddrWidget, subnetWidget = userData

            ipaddr = ipaddrWidget.get_edit_text()
            netmask = subnetWidget.get_edit_text()
            #gateway = gatewayWidget.get_edit_text()
            gateway = ""

            output = self.action.SetIPv4StaticAddress(self.simpleListWalker, ipaddr, netmask, gateway, networkAdapterList)
            if not output[0]:
                ipConfDescribeText.set_text(u"虚拟交换机设置失败:" + output[1])
            else:
                ipConfDescribeText.set_text(u"虚拟交换机设置成功")
            InitStaticDefaultVswitchIP()

        # IP Static Address configure
        dynamicIPAddrEdit = urwid.Edit(u"    IPv4地址: ")
        dynamicIPAddrAttrMap = urwid.AttrMap(dynamicIPAddrEdit, None, "reveal focus")
        dynamicSubnetEdit = urwid.Edit(u"    子网掩码: ")
        dynamicSubnetAttrMap = urwid.AttrMap(dynamicSubnetEdit, None, "reveal focus")
        #dynamicGatewayEdit = urwid.Edit(u"    默认网关: ")
        #dynamicGatewayAttrMap = urwid.AttrMap(dynamicGatewayEdit, None, "reveal focus")

        InitStaticDefaultVswitchIP()

        #dynamic_state = True
        #static_state = False
        #if dynamicIPAddrEdit.get_edit_text():
        #    static_state = True
        #    dynamic_state = False

        dynamicConfSubmitButton = urwid.Button(self.AlignButtonText(u"    提交设置"), 
            on_press = SubmitIPv4StaticAddressConf,
            #user_data = (dynamicIPAddrEdit, dynamicSubnetEdit, dynamicGatewayEdit),
            user_data = (dynamicIPAddrEdit, dynamicSubnetEdit),
        )
        dynamicConfSubmitButtonAttrMap = urwid.AttrMap(dynamicConfSubmitButton, None, 'reveal focus')
        dynamicConfSubmitColumn = urwid.Columns([('fixed', self.buttonWidth, dynamicConfSubmitButtonAttrMap),],)

        ipConfGroup = []
        #dynamicButton = urwid.RadioButton(ipConfGroup, u"使用动态IP地址和网络配置",
        #    state = dynamic_state, 
        #    user_data = (dynamicIPAddrAttrMap, dynamicSubnetAttrMap, 
        #        dynamicGatewayAttrMap, dynamicConfSubmitColumn,),
        #)
        #dynamicButtonAttrMap = urwid.AttrMap(dynamicButton, None, 'reveal focus')
        staticButton = urwid.RadioButton(ipConfGroup, u"设置静态IP地址和网络配置", 
            state = True,
            on_state_change = StaticAddress,
            user_data = (dynamicIPAddrAttrMap, dynamicSubnetAttrMap, 
        #        dynamicGatewayAttrMap, dynamicConfSubmitColumn,),
                dynamicConfSubmitColumn,),
        )
        staticButtonAttrMap = urwid.AttrMap(staticButton, None, 'reveal focus')

        content.append(urwid.Divider(self.dividerStr))
        #content.append(dynamicButtonAttrMap)
        content.append(staticButtonAttrMap)

        #if dynamicIPAddrEdit.get_edit_text():
        content.append(dynamicIPAddrAttrMap)
        content.append(dynamicSubnetAttrMap)
        #content.append(dynamicGatewayAttrMap)
        content.append(dynamicConfSubmitColumn)

        content.append(urwid.Divider(self.dividerStr))

        # IPv6 configure
        #ipv6ConfDescribeText = urwid.Text(u"IPv6地址配置\n\n如果网络中存在DHCPv6服务器或者存在支持Router Advertisement（路由器通告）的路由器，主机将根据他们的设置自动配置相关参数。\n如果没有这类服务器，则必须手工配置下面的参数")
        #ipv6ConfDescribeLineBox = urwid.LineBox(ipv6ConfDescribeText)
        #content.append(ipv6ConfDescribeLineBox)
        #content.append(urwid.Divider(self.dividerStr))

        #def ChangeIPv6State(widget, state, userData = None):
        #    """If state is True, all sub widgets into listbox. otherwise delete them"""

        #    visibleWidgetList = self.managementNetworkWidget['ipv6']
        #    if state:
        #        visibleWidgetList.reverse()
        #        widget, position = self.simpleListWalker.get_focus()
        #        for visibleWidget in visibleWidgetList:
        #            self.simpleListWalker.insert(position + 1, visibleWidget)

        #        visibleWidgetList.reverse()
        #    else:
        #        for visibleWidget in visibleWidgetList:
        #            self.simpleListWalker.remove(visibleWidget)
                
        #def ChangeDHCPv6State(widget, userData = None):
        #    raise RuntimeError, "Obtain configuration from DHCPv6 server"

        #def ChangeICMPState(widget, userData = None):
        #    raise RuntimeError, "Obtain configuration from ICMP stateless"

        #enableState = False
        #ipv6ConfGroup = []
        ## Some ipv6 configuration widget that visable in different situation
        #self.managementNetworkWidget['ipv6'] = []

        #ipv6EnableButton = urwid.CheckBox(u'开启IPv6功能（需要重新启动）', state = enableState, 
        #    on_state_change = ChangeIPv6State, user_data = None, 
        #)
        #ipv6EnableButtonAttrMap = urwid.AttrMap(ipv6EnableButton, None, 'reveal focus')

        #ipv6FromAutoRadioButton = urwid.RadioButton(ipv6ConfGroup, u"不使用自动配置", )
        #ipv6FromAutoRadioButtonAttrMap = urwid.AttrMap(ipv6FromAutoRadioButton, None, 'reveal focus')
        #ipv6FromServerRadioButton = urwid.RadioButton(ipv6ConfGroup, u"从DHCPv6服务器获取配置", on_state_change = ChangeDHCPv6State)
        #ipv6FromServerRadioButtonAttrMap = urwid.AttrMap(ipv6FromServerRadioButton, None, 'reveal focus')
        #ipv6FromIcmpRadioButton = urwid.RadioButton(ipv6ConfGroup, u"使用ICMP Stateless （ICMP无状态）配置", 
        #    on_state_change = ChangeICMPState,
        #)
        #ipv6FromIcmpRadioButtonAttrMap = urwid.AttrMap(ipv6FromIcmpRadioButton, None, 'reveal focus')

        ## IPv6 Static Address configure
        #ipv6AddrEdit1 = urwid.Edit(u"    IPv6静态地址 1: ")
        #ipv6AddrAttrMap1 = urwid.AttrMap(ipv6AddrEdit1, None, "reveal focus")
        #ipv6AddrEdit2 = urwid.Edit(u"    IPv6静态地址 2: ")
        #ipv6AddrAttrMap2 = urwid.AttrMap(ipv6AddrEdit2, None, "reveal focus")
        #ipv6AddrEdit3 = urwid.Edit(u"    IPv6静态地址 3: ")
        #ipv6AddrAttrMap3 = urwid.AttrMap(ipv6AddrEdit3, None, "reveal focus")
        #ipv6DefaultGatewayEdit = urwid.Edit(u"    默认网关      : ")
        #ipv6DefaultGatewayAttrMap = urwid.AttrMap(ipv6DefaultGatewayEdit, None, "reveal focus")

        #def SubmitIPv6StaticAddressConf(widget, userData=None):
        #   if userData is None:
        #       return None

        #   ipaddrWidget1, ipaddrWidget2, ipaddrWidget3, gatewayWidget = userData

        #   ipaddr1 = ipaddrWidget1.get_edit_text()
        #   ipaddr2 = ipaddrWidget2.get_edit_text()
        #   ipaddr3 = ipaddrWidget3.get_edit_text()
        #   gateway = gatewayWidget.get_edit_text()

        #   self.action.SetIPv6StaticAddress(self.simpleListWalker, ipaddr1, ipaddr2, ipaddr3, gateway)

       
        #ipv6ConfSubmitButton = urwid.Button(self.AlignButtonText(u"    提交设置"), 
        #    on_press = SubmitIPv6StaticAddressConf,
        #    user_data = (ipv6AddrEdit1, ipv6AddrEdit2, ipv6AddrEdit3, ipv6DefaultGatewayEdit),
        #)
        #ipv6ConfSubmitButtonAttrMap = urwid.AttrMap(ipv6ConfSubmitButton, None, 'reveal focus')
        #ipv6ConfSubmitColumn = urwid.Columns([('fixed', self.buttonWidth, ipv6ConfSubmitButtonAttrMap),],)


        ## Get current focus in listbox
        #self.managementNetworkWidget['ipv6'] = [
        #    ipv6FromAutoRadioButtonAttrMap, ipv6FromServerRadioButtonAttrMap, ipv6FromIcmpRadioButtonAttrMap,
        #    ipv6AddrAttrMap1, ipv6AddrAttrMap2, ipv6AddrAttrMap3, ipv6DefaultGatewayAttrMap, ipv6ConfSubmitColumn,
        #]

        #content.append(ipv6EnableButtonAttrMap)
        #if enableState:
        #    for visibleWidget in self.managementNetworkWidget['ipv6']:
        #        content.append(visibleWidget)

        content.append(urwid.Divider(self.dividerStr))


        # DNS configuration
        dnsConfDescribeText = urwid.Text(u"DNS配置\n\n配置DNS，主机名，网关等信息")
        dnsConfDescribeLineBox = urwid.LineBox(dnsConfDescribeText)

        def SetDNSSetting(widget, state, userData = None):
        
            return None    
            if not state:
                widget.set_label(u"手工配置DNS服务器的主机名和IP地址")

                simpleListWalkerWidget, position = self.simpleListWalker.get_focus()
                self.managementNetworkWidget['dns'].reverse()

                for visibleWidget in self.managementNetworkWidget['dns']:
                    self.simpleListWalker.insert(position + 1, visibleWidget)
                    
                self.managementNetworkWidget['dns'].reverse()
            else:
                widget.set_label(u"自动获取DNS服务器的主机名和IP地址")

                for visibleWidget in self.managementNetworkWidget['dns']:
                    if visibleWidget in self.simpleListWalker.contents:
                        self.simpleListWalker.remove(visibleWidget)
                

        # True for DNS Automatically configure, otherwise for manually
        dnsAutoState = True
        #if dnsAutoState:
        #    tips = u"自动获取DNS服务器的主机名和IP地址"
        #else:
        #    tips = u"手工配置DNS服务器的主机名和IP地址"
        tips = u"手工配置DNS服务器的主机名和IP地址"

        self.managementNetworkWidget['dns'] = []
        dnsConfGroup = []
        self.dnsAutoConfCheckBox = urwid.RadioButton(dnsConfGroup, tips, 
            on_state_change = SetDNSSetting, user_data = None,
        )
        dnsAutoConfCheckBoxAttrMap = urwid.AttrMap(self.dnsAutoConfCheckBox, None, 'reveal focus')

        #self.dnsManualConfCheckBox = urwid.CheckBox(u"手工配置DNS服务器的主机名和IP地址", 
        #    state = False, on_state_change = SetDNSSetting, user_data = None,
        #)
        #dnsManualConfCheckBoxAttrMap = urwid.AttrMap(self.dnsManualConfCheckBox, None, 'reveal focus')

        # DNS manually configure
        dnsPrimaryServerAddressEdit = urwid.Edit(u"    主DNS服务器地址: ")
        dnsPrimaryServerAddressAttrMap = urwid.AttrMap(dnsPrimaryServerAddressEdit, None, "reveal focus")
        dnsSecondServerAddressEdit = urwid.Edit(u"    辅DNS服务器地址: ")
        dnsSecondServerAddressAttrMap = urwid.AttrMap(dnsSecondServerAddressEdit, None, "reveal focus")
        dnsHostnameEdit = urwid.Edit(u"    主机名         : ")
        dnsHostnameAttrMap = urwid.AttrMap(dnsHostnameEdit, None, "reveal focus")
        dnsGatewayEdit = urwid.Edit(u"    网关           : ")
        dnsGatewayAttrMap = urwid.AttrMap(dnsGatewayEdit, None, "reveal focus")

        def InitDnsText():

            netbasic = self.action.GetDnsHostnameGateway()
            dnsPrimaryServerAddressEdit.set_edit_text(u"%s" % netbasic["main"])
            dnsSecondServerAddressEdit.set_edit_text(u"%s" % netbasic["sub"])
            dnsHostnameEdit.set_edit_text(u"%s" % netbasic["hostname"])
            dnsGatewayEdit.set_edit_text(u"%s" % netbasic["gateway"])

        def SubmitIPv4DNSConf(widget, userData=None):
           if userData is None:
               return None

           dnsWidget1, dnsWidget2, dnsWidget3, dnsWidget4 = userData

           #import pdb;pdb.set_trace()
           dnsAddr1 = dnsWidget1.get_edit_text()
           dnsAddr2 = dnsWidget2.get_edit_text()
           dnsAddr3 = dnsWidget3.get_edit_text()
           dnsAddr4 = dnsWidget4.get_edit_text()
           if not dnsAddr3:
               dnsConfDescribeText.set_text(u"设置dns失败")
               return
           if not self.action.SetIPv4DNSAddress(self.simpleListWalker, dnsAddr1, dnsAddr2, dnsAddr3, dnsAddr4):
               dnsConfDescribeText.set_text(u"设置dns失败")
               InitDnsText()
           else:
               dnsConfDescribeText.set_text(u"设置dns成功")
               dnsWidget1.set_edit_text(u"%s" % dnsAddr1)
               dnsWidget2.set_edit_text(u"%s" % dnsAddr2)
               dnsWidget3.set_edit_text(u"%s" % dnsAddr3)
               dnsWidget4.set_edit_text(u"%s" % dnsAddr4)

        InitDnsText()

        dnsConfSubmitButton = urwid.Button(self.AlignButtonText(u"    提交设置"), 
            on_press = SubmitIPv4DNSConf,
            user_data = (dnsPrimaryServerAddressEdit, dnsSecondServerAddressEdit, dnsHostnameEdit, dnsGatewayEdit),
        )
        dnsConfSubmitButtonAttrMap = urwid.AttrMap(dnsConfSubmitButton, None, 'reveal focus')
        dnsConfSubmitColumn = urwid.Columns([('fixed', self.buttonWidth, dnsConfSubmitButtonAttrMap),],)


        self.managementNetworkWidget['dns'] = [
             dnsPrimaryServerAddressAttrMap, dnsSecondServerAddressAttrMap, 
             dnsHostnameAttrMap, dnsGatewayAttrMap, dnsConfSubmitColumn
        ]

        content.append(dnsConfDescribeLineBox)
        content.append(urwid.Divider(self.dividerStr))
        content.append(dnsAutoConfCheckBoxAttrMap)

        #if not dnsAutoState:
        for visibleWidget in self.managementNetworkWidget['dns']:
            content.append(visibleWidget)

        content.append(urwid.Divider(self.dividerStr))

        # Custom DNS suffix
        #customDNSDescribeText = urwid.Text(u"自定义DNS后缀\n\n（详细定义申请）")
        #customDNSDescribeLineBox = urwid.LineBox(customDNSDescribeText)
        #content.append(customDNSDescribeLineBox)
        #content.append(urwid.Divider(self.dividerStr))

        #dnsSuffixEdit = urwid.Edit(caption = u"地址后缀: ", edit_text = u'')
        #dnsSuffixEditAttrMap = urwid.AttrMap(dnsSuffixEdit, None, "reveal focus")
        #content.append(dnsSuffixEditAttrMap)
        #content.append(urwid.Divider(self.dividerStr))
        
        # Last step to create listbot to show all widgets
        def SubmitAllSetting(widget, userData = None):
        
            managementNetworkConf = {
                #'vlanId':               vlanEditWidget.get_edit_text(),
                'networkAdapterList':   networkAdapterList,
                'ipv4StaticState':      staticButton.get_state(),
                #'ipv4DynamicState':     dynamicButton.get_state(),
                'ipv4DynamicAddress':   dynamicIPAddrEdit.get_edit_text(),
                'ipv4DynamicNetmask':   dynamicSubnetEdit.get_edit_text(),
                #'ipv4DynamicGateway':   dynamicGatewayEdit.get_edit_text(),
                #'ipv6EnableState':      ipv6EnableButton.get_state(),
                #'ipv6FromAuto':         ipv6FromAutoRadioButton.get_state(),
                #'ipv6FromDHCPServer':   ipv6FromServerRadioButton.get_state(),
                #'ipv6FromIcmp':         ipv6FromIcmpRadioButton.get_state(),
                #'ipv6Address1':         ipv6AddrEdit1.get_edit_text(),
                #'ipv6Address2':         ipv6AddrEdit2.get_edit_text(),
                #'ipv6Address3':         ipv6AddrEdit3.get_edit_text(),
                #'ipv6Gateway':          ipv6DefaultGatewayEdit.get_edit_text(),
                'dnsFromAuto':          self.dnsAutoConfCheckBox.get_state(),
                'dnsPrimaryAddress':    dnsPrimaryServerAddressEdit.get_edit_text(),
                'dnsSecondAddress':     dnsSecondServerAddressEdit.get_edit_text(),
                'dnsHostname':          dnsHostnameEdit.get_edit_text(),
            }
            
            self.action.SubmitAllManagementNetworkSetting(self.simpleListWalker, managementNetworkConf)
           
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        #submitAllConfButton    = urwid.Button(self.AlignButtonText(u'提交所有配置'), 
        #    on_press = SubmitAllSetting,
        #    user_data = (),
        #)
        #submitAllConfAttrMap   = urwid.AttrMap(submitAllConfButton, None, 'reveal focus')
        buttonColumn = urwid.Columns([
            ('fixed', self.buttonWidth, returnAttrMap),
#            ('fixed', self.buttonWidth, submitAllConfAttrMap),
        ])
        content.append(buttonColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

                
    def CreateRestartNetworkWindow(self):
        """Create a sub window to show main configure"""

        self._EraseSubWindow()

        def RestartNetwork(widget):
            if not self.action.RestartManagementNetwork(self.simpleListWalker):
                describeText.set_text(u"重启网络失败")
            else:
                describeText.set_text(u"重启网络成功")

        content = []

        # Describe box
        describeText = urwid.Text(u"重启管理网络将会短暂中断网络连接，并且断开所有远程管理连接，这有可能影响到虚拟机的运行\n\n\n")
        describeLineBox = urwid.LineBox(describeText)
        content.append(describeLineBox)
        
        # Create widgets for restart managerment network
        content.append(urwid.Divider(self.dividerStr))
        restartButton   = urwid.Button(self.AlignButtonText(u"重启管理网络"), on_press = RestartNetwork)
        restartAttrMap  = urwid.AttrMap(restartButton, None, 'reveal focus')
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        buttonColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
                ('fixed', self.buttonWidth, restartAttrMap),
            ),
        )
        content.append(buttonColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateTestManagementNetworkWindow(self):
        self._EraseSubWindow()

        content = []

        # Describe box
        describeText = urwid.Text(u"执行简短的网络测试\n\n\n")
        describeLineBox = urwid.LineBox(describeText)
        content.append(describeLineBox)

        # Ping #0 widgets
        def PingAddress(widget, userData = None):
            ipAddr = userData.get_edit_text()
            if not self.action.TestManagementNetworkPing(self.simpleListWalker, ipAddr):
                describeText.set_text(u"执行Ping %s命令失败" % ipAddr)
            else:
                describeText.set_text(u"执行Ping %s命令成功" % ipAddr)

        pingText0 = urwid.Edit(caption = u"Ping 地址 #0: ")
        pingTextAttrMap0 = urwid.AttrMap(pingText0, None, 'reveal focus')
        pingButton0 = urwid.Button(self.AlignButtonText(u"执行Ping #0"), on_press = PingAddress, user_data = pingText0)
        pingButtonAttrMap0 = urwid.AttrMap(pingButton0, None, 'reveal focus')
        pingColumn0 = urwid.Columns(
            (pingTextAttrMap0, ('fixed', self.buttonWidth, pingButtonAttrMap0))
        )

        # Ping #1 widgets
        #pingText1 = urwid.Edit(caption = u"Ping 地址 #1: ")
        #pingTextAttrMap1 = urwid.AttrMap(pingText1, None, 'reveal focus')
        #pingButton1 = urwid.Button(self.AlignButtonText(u"执行Ping #1"), on_press = PingAddress, user_data = pingText1)
        #pingButtonAttrMap1 = urwid.AttrMap(pingButton1, None, 'reveal focus')
        #pingColumn1 = urwid.Columns(
        #    (pingTextAttrMap1, ('fixed', self.buttonWidth, pingButtonAttrMap1))
        #)

        # Ping #2 widgets
        #pingText2 = urwid.Edit(caption = u"Ping 地址 #2: ")
        #pingTextAttrMap2 = urwid.AttrMap(pingText2, None, 'reveal focus')
        #pingButton2 = urwid.Button(self.AlignButtonText(u"执行Ping #2"), on_press = PingAddress, user_data = pingText2)
        #pingButtonAttrMap2 = urwid.AttrMap(pingButton2, None, 'reveal focus')
        #pingColumn2 = urwid.Columns(
        #    (pingTextAttrMap2, ('fixed', self.buttonWidth, pingButtonAttrMap2))
        #)

        # Resolve hostname widgets
        def ResolveHostname(widget, userData = None):
            ipAddr = userData.get_edit_text()
            self.action.TestManagementNetworkResolveHostname(self.simpleListWalker, ipAddr)
        
        #hostnameResolveText = urwid.Edit(caption = u"获取主机名: ")
        #hostnameResolveTextAttrMap = urwid.AttrMap(hostnameResolveText, None, 'reveal focus')
        #hostnameResolveButton = urwid.Button(u"开始获取主机名", on_press = ResolveHostname, user_data = hostnameResolveText)
        #hostnameResolveButtonAttrMap = urwid.AttrMap(hostnameResolveButton, None, 'reveal focus')
        #hostnameColumn = urwid.Columns(
        #    (hostnameResolveTextAttrMap, ('fixed', self.buttonWidth, hostnameResolveButtonAttrMap))
        #)

        # Bottom buttons
        def SubmitAllActions(widget, userData = None):
            confDict = {
                'pingAddress1':     pingText0.get_edit_text(),
            #    'pingAddress2':     pingText1.get_edit_text(),
            #    'pingAddress3':     pingText2.get_edit_text(),
            #    'resolveHostname':  hostnameResolveText.get_edit_text(),
            }
            self.action.TestManagementNetworkSubmitAllActions(self.simpleListWalker, confDict)

        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        #submitAllButton   = urwid.Button(self.AlignButtonText(u"执行所有操作"), on_press = SubmitAllActions, 
        ##    user_data = (pingText0, pingText1, pingText2, hostnameResolveText,)
        #    user_data = (pingText0, )
        #)
        #submitAllAttrMap  = urwid.AttrMap(submitAllButton, None, 'reveal focus')
        buttonColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
        #        ('fixed', self.buttonWidth, submitAllAttrMap),
            ),
        )
 
        # Display visable widgets
        content.append(urwid.Divider(self.dividerStr))
        content.append(pingColumn0)
        #content.append(pingColumn1)
        #content.append(pingColumn2)
        #content.append(hostnameColumn)
        content.append(urwid.Divider(self.dividerStr))
        content.append(buttonColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateRestoreNetworkSettingWindow(self):

        self._EraseSubWindow()

        content = []
        # Describe box
        describeText = urwid.Text(u"恢复网络的出厂设置\n\n\n将网络的设置恢复到默认状态\n注意：本操作会将本机正在运行的虚拟机全部停止")
        describeLineBox = urwid.LineBox(describeText)
        content.append(describeLineBox)

        # Create widgets for restore network
        def RestoreNetwork(widget):
            self.action.RestoreNetworkFactorySetting(self.simpleListWalker)

        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        restoreButton   = urwid.Button(self.AlignButtonText(u"恢复出厂设置"), on_press = RestoreNetwork)
        restoreAttrMap  = urwid.AttrMap(restoreButton, None, 'reveal focus')
        buttonColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
                ('fixed', self.buttonWidth, restoreAttrMap),
            ),
        )

        content.append(urwid.Divider(self.dividerStr))
        content.append(buttonColumn)
        content.append(urwid.Divider(self.dividerStr))
       
        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateKeyboardSettingWindow(self):

        self._EraseSubWindow()

        content = []
        # Describe box
        describeText = urwid.Text(u"键盘配置\n\n\n设置本机键盘的布局方式")
        describeLineBox = urwid.LineBox(describeText)
        content.append(describeLineBox)

        # Create widgets for restore network
        def SetKeyboardLayout(widget):
            keyboardLayout = widget.get_label()
            self.action.KeyboardLayoutSetting(self.simpleListWalker, keyboardLayout)

        keyboardLayoutList = (
            u"U.S.",
            u"Chs",
        )

        content.append(urwid.Divider(self.dividerStr))

        for keyboardLayout in keyboardLayoutList:
            layoutButton = urwid.Button(keyboardLayout, on_press = SetKeyboardLayout)
            layoutAttrMap = urwid.AttrMap(layoutButton, None, "reveal focus")
            content.append(layoutAttrMap)

        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        buttonColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
            ),
        )

        content.append(urwid.Divider(self.dividerStr))
        content.append(buttonColumn)
       
        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateTroubleshootingWindow(self):
        self._EraseSubWindow()

        content = []
        # ESXi widgets 
        def OpenESXi(widget, currentState):
            self.action.TroubleShootingOpenESXi(self.simpleListWalker, currentState)

        def CloseESXi(widget, currentState):
            self.action.TroubleShootingCloseESXi(self.simpleListWalker, currentState)

        ESXiState = True
        
        esxiGroup = []
        esxiDescribeText = urwid.Text(u"修改当前的ESXi Shell设置")
        esxiDescribeLineBox = urwid.LineBox(esxiDescribeText)
        esxiOpenRadioButton = urwid.RadioButton(esxiGroup, u"开启ESXi Shell", on_state_change = OpenESXi)
        esxiOpenRadioButtonAttrMap = urwid.AttrMap(esxiOpenRadioButton, None, 'reveal focus')
        esxiCloseRadioButton = urwid.RadioButton(esxiGroup, u"关闭ESXi Shell", on_state_change = CloseESXi)
        esxiCloseRadioButtonAttrMap = urwid.AttrMap(esxiCloseRadioButton, None, 'reveal focus')
        if ESXiState:
            esxiOpenRadioButton.toggle_state()
        else:
            esxiCloseRadioButton.toggle_state()

        # SSH widgets
        def OpenSSH(widget, currentState):
            self.action.TroubleShootingOpenSSH(self.simpleListWalker, currentState)

        def CloseSSH(widget, currentState):
            self.action.TroubleShootingCloseSSH(self.simpleListWalker, currentState)

        SSHState = True
        sshGroup = []
        sshDescribeText = urwid.Text(u"修改当前的SSH设置")
        sshDescribeLineBox = urwid.LineBox(sshDescribeText)

        sshOpenRadioButton = urwid.RadioButton(sshGroup, u"开启SSH服务", on_state_change = OpenSSH)
        sshOpenRadioButtonAttrMap = urwid.AttrMap(sshOpenRadioButton, None, 'reveal focus')
        sshCloseRadioButton = urwid.RadioButton(sshGroup, u"关闭SSH服务", on_state_change = CloseSSH)
        sshCloseRadioButtonAttrMap = urwid.AttrMap(sshCloseRadioButton, None, 'reveal focus')
        if SSHState:
            sshOpenRadioButton.toggle_state()
        else:
            sshCloseRadioButton.toggle_state()

        # Bottom widgets
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
            ),
        )

        # Add all widgets
        content.append(esxiDescribeLineBox)
        content.append(esxiOpenRadioButtonAttrMap)
        content.append(esxiCloseRadioButtonAttrMap)
        content.append(urwid.Divider(self.dividerStr))
        content.append(sshDescribeLineBox)
        content.append(sshOpenRadioButtonAttrMap)
        content.append(sshCloseRadioButtonAttrMap)
        content.append(urwid.Divider(self.dividerStr))
        content.append(bottomColumn)
 
        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateViewSystemLogWindow(self):
        self._EraseSubWindow()

        content = []

        def ViewSystemLog(widget, textWidget):
            systemLogString = self.action.ViewSystemLog(self.simpleListWalker)
            textWidget.set_text(systemLogString)

        def ViewVMKernelLog(widget, textWidget):
            vmkernelString = self.action.ViewVMKernelLog(self.simpleListWalker)
            textWidget.set_text(vmkernelString)

        def ViewConfigLog(widget, textWidget):
            configString = self.action.ViewConfigLog(self.simpleListWalker)
            textWidget.set_text(configString)

        def ViewManagementAgentLog(widget, textWidget):
            agentString = self.action.ViewManagementAgentLog(self.simpleListWalker)
            textWidget.set_text(agentString)

        def ViewVirtualCenterAgentLog(widget, textWidget):
            virtualCenterString = self.action.ViewVirtualCenterAgentLog(self.simpleListWalker)
            textWidget.set_text(virtualCenterString)

        def ViewESXiObservationLog(widget, textWidget):
            esxiObserveString = self.action.ViewESXiObservationLog(self.simpleListWalker)
            textWidget.set_text(esxiObserveString)

        displayText = urwid.Text(u'请选择日志类型')

        syslogButton = urwid.Button(u"查看系统日志", on_press = ViewSystemLog, user_data = displayText)
        syslogButtonAttrMap = urwid.AttrMap(syslogButton, None, 'reveal focus')

        vmkernelButton = urwid.Button(u"查看虚拟机内核日志", on_press = ViewVMKernelLog, user_data = displayText)
        vmkernelButtonAttrMap = urwid.AttrMap(vmkernelButton, None, 'reveal focus')

        configButton = urwid.Button(u"查看系统配置", on_press = ViewConfigLog, user_data = displayText)
        configButtonAttrMap = urwid.AttrMap(configButton, None, 'reveal focus')

        managementAgentButton = urwid.Button(u"查看主机的管理平台配置", on_press = ViewManagementAgentLog, user_data = displayText)
        managementAgentButtonAttrMap = urwid.AttrMap(managementAgentButton, None, 'reveal focus')

        virtualCenterAgentButton = urwid.Button(u"查看虚拟中心平台 (vpxa)", on_press = ViewVirtualCenterAgentLog, user_data = displayText)
        virtualCenterAgentButtonAttrMap = urwid.AttrMap(virtualCenterAgentButton, None, 'reveal focus')
        
        vmESXiObservationButton = urwid.Button(u"查看ESXi观察日志", on_press = ViewESXiObservationLog, user_data = displayText)
        vmESXiObservationButtonAttrMap = urwid.AttrMap(vmESXiObservationButton, None, 'reveal focus')
 
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
            ),
        )

        content.append(syslogButtonAttrMap)
        content.append(vmkernelButtonAttrMap)
        content.append(configButtonAttrMap)
        content.append(managementAgentButtonAttrMap)
        content.append(virtualCenterAgentButtonAttrMap)
        content.append(vmESXiObservationButtonAttrMap)
        content.append(urwid.Divider(self.dividerStr))
        content.append(bottomColumn)
        content.append(urwid.Divider(self.dividerStr))
        content.append(displayText)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateViewSupportInformationWindow(self):
        
        self._EraseSubWindow()
        content = []

        text = urwid.Text(u"", align = 'left')
        textLineBox = urwid.LineBox(text)
        information = self.action.ViewSupportInformation(self.simpleListWalker)
        text.set_text(information)

        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
            ),
        )

        content.append(textLineBox)
        content.append(urwid.Divider(self.dividerStr))
        content.append(bottomColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateDiffWindow(self):
        """Create a sub window to show which configuration have been modified"""

        # _EraseSubWindow will get all user configure and remove previous sub window
        self._EraseSubWindow()

        
        # Now we have two configurations, one is basic/backup configuration which
        # created by start, and other modified/changed configuration by user.
        # Compare them to know which configuration have been modified.
        confDict = {}
        tmpWidgetStrList = [
            (u'设置名称', u'源设置', u'修改后的设置',),
        ]
        for key in self.modifiedConfDict:
            # Only display different configuration
            if self.modifiedConfDict[key] == self.wholeConfDict[key]:
                continue

            tmpWidgetStrList.append((key, self.wholeConfDict[key], self.modifiedConfDict[key],))

        # Create widget to display
        listBoxContent = []
        for strList in tmpWidgetStrList:
            widgetList = []
            for str in strList:
                widgetList.append(urwid.Text(str, align = 'left'))

            # Make all widget into grid flow frame and align by 'left'
            gridFlowWidget = urwid.GridFlow(widgetList, 16, 4, 2, align = 'left')
            # one grid flow make shows a line in listbox
            listBoxContent.append(urwid.AttrMap(gridFlowWidget, None, 'reveal focus'))
            listBoxContent.append(urwid.Divider(" "))


        self.simpleListWalker = urwid.SimpleListWalker(listBoxContent)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)

        return None

    def CreateResetSystemConfigurationWindow(self):
        
        self._EraseSubWindow()
        content = []

        describeText = urwid.Text("重置系统配置\n\n\n特别注意：重置系统配置将会把所有配置恢复到默认状态！")
        describeTextLineBox = urwid.LineBox(describeText)

        def ResetSystemConfiguration(widget):
            self.action.ResetSystemConfiguration(self.simpleListWalker)
        
        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        resetButton     = urwid.Button(self.AlignButtonText(u"重置系统配置"), on_press = ResetSystemConfiguration)
        resetButtonAttrMap = urwid.AttrMap(resetButton, None, 'reveal focus')
        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap), 
                ('fixed', self.buttonWidth, resetButtonAttrMap), 
            ),
        )

        content.append(describeTextLineBox)
        content.append(urwid.Divider(self.dividerStr))
        content.append(bottomColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)



    def CreateResetSystemWindow(self):

        self._EraseSubWindow()
        content = []

        describeText = urwid.Text("重启系统\n\n\n特别注意：重启系统将会把所有虚拟机都关闭！")
        describeTextLineBox = urwid.LineBox(describeText)

        def ResetSystem(widget):
            describeText.set_text(u"系统即将重启...")
            self.action.ResetSystem(self.simpleListWalker)

        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        resetButton     = urwid.Button(self.AlignButtonText(u"重启系统"), on_press = ResetSystem)
        resetButtonAttrMap = urwid.AttrMap(resetButton, None, 'reveal focus')
        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap),
                ('fixed', self.buttonWidth, resetButtonAttrMap),
            ),
        )

        content.append(describeTextLineBox)
        content.append(urwid.Divider(self.dividerStr))
        content.append(bottomColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreatePoweroffSystemWindow(self):

        self._EraseSubWindow()
        content = []

        describeText = urwid.Text("关闭系统\n\n\n特别注意：关闭系统将会把所有虚拟机都关闭！")
        describeTextLineBox = urwid.LineBox(describeText)

        def PoweroffSystem(widget):
            describeText.set_text(u"系统即将关闭...")
            self.action.PoweroffSystem(self.simpleListWalker)

        returnButton    = urwid.Button(self.AlignButtonText(u'返回主菜单'), on_press = self._GoToMainMenu)
        returnAttrMap   = urwid.AttrMap(returnButton, None, 'reveal focus')
        resetButton     = urwid.Button(self.AlignButtonText(u"关闭系统"), on_press = PoweroffSystem)
        resetButtonAttrMap = urwid.AttrMap(resetButton, None, 'reveal focus')
        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, returnAttrMap),
                ('fixed', self.buttonWidth, resetButtonAttrMap),
            ),
        )

        content.append(describeTextLineBox)
        content.append(urwid.Divider(self.dividerStr))
        content.append(bottomColumn)

        # Create list box
        self.simpleListWalker = urwid.SimpleListWalker(content)
        listBox = urwid.AttrMap(urwid.ListBox(self.simpleListWalker), 'standard')
        self.bodyArea.widget_list.insert(1, listBox)
        self.bodyArea.set_focus(1)

    def CreateMainWindow(self):
        # Create status bar
        self.statusBar = urwid.Text(u"", wrap = 'clip')

        # Create main area
        listBoxContent = []
        extrConfListBox = []

        i = 0
        for mainMenu in self.mainMenuList:
            if len(mainMenu) == 0:
                listBoxContent.append(urwid.Divider(self.dividerStr))
                continue 

            #widget = urwid.Edit(mainMenu)
            widget = urwid.Button(mainMenu, on_press=self.PaneButtonHandler, user_data = i)
            listBoxContent.append(urwid.AttrMap(widget, None, 'reveal focus'))
            i += 1

        self.mainMenuListWalker = urwid.SimpleListWalker(listBoxContent)
        self.mainMenuListBox = urwid.ListBox(self.mainMenuListWalker)
        decoratedMainMenuListBox = urwid.AttrMap(self.mainMenuListBox, 'bg')

        
        describeWidgets = []
        describeAttrMap = urwid.AttrMap(urwid.Text(self.describe), None, 'reveal focus')
        describeWidgets.append(describeAttrMap)
        describeBox = urwid.SimpleListWalker(describeWidgets)
        describeBox = urwid.AttrMap(urwid.ListBox(describeBox), 'standard')

        widgetList = (
            ('fixed', self.paneWidth, decoratedMainMenuListBox),
            describeBox,
        )
        self.bodyArea = urwid.Columns(widgetList,)

        # Align all area
        self.mainWindow = urwid.Frame(self.bodyArea, footer = self.statusBar)

        #mainFrame = urwid.AttrMap(self.mainWindow, None, 'bg')
        mainFrame = urwid.AttrMap(self.mainWindow, None, None)
        mainFrame = urwid.LineBox(mainFrame)
        
        #raise RuntimeError, self.mainMenuListBox.get_focus()

        self.loop = urwid.MainLoop(mainFrame, 
            palette = self.palette,
        )
        self.loop.run()

class LoginScreen(Base):
    def __init__(self):
        Base.__init__(self)
        self.action = Interface.Action()
        self.tmpLoginCounter = 1

    def CreatePasswordDialog(self):
        """Create a dialogy to let user to login"""

        def SubmitLogin(widget, userData = None):
            username = self.usernameEdit.get_edit_text()
            password = self.passwordEdit.get_edit_text()
            state = self.action.UserLogin(username, password)

            if state:
                self.FileWriteLines(self.temporaryFile['loginState'], ["1",])
                raise urwid.ExitMainLoop

            if self.tmpLoginCounter < self.maxLoginFailCounter:
                self.tipsText.set_text(
                    u"第 %d 次登陆失败，还有 %d 次机会" % (self.tmpLoginCounter, self.maxLoginFailCounter - self.tmpLoginCounter)
                )
                self.tmpLoginCounter += 1
            else:
                raise urwid.ExitMainLoop

        def ResetInput(widget):
            self.usernameEdit.set_edit_text(u"")
            self.passwordEdit.set_edit_text(u"")
            self.lb.set_focus(1)

        def ReturnMainWindow(widget):
            raise urwid.ExitMainLoop

        content = []
        self.tipsText = urwid.Text(u"请输入用户名和密码登陆设备")
        tipsTextLineBox = urwid.LineBox(self.tipsText)
        
        self.usernameEdit = urwid.Edit(caption = u'用户名：  ')
        usernameEditAttrMap = urwid.AttrMap(self.usernameEdit, None, 'reveal focus')
        self.passwordEdit = urwid.Edit(caption = u"用户密码：", mask = "*")
        #passwordEdit = urwid.Edit(caption = u"用户密码：")
        passwordEditAttrMap = urwid.AttrMap(self.passwordEdit, None, 'reveal focus')

        submitButton = urwid.Button(self.AlignButtonText(u"登陆"), on_press = SubmitLogin,
            user_data = (self.usernameEdit.get_edit_text(), self.passwordEdit.get_edit_text())
        )
        submitButtonAttrMap = urwid.AttrMap(submitButton, None, 'reveal focus')
        resetButton = urwid.Button(self.AlignButtonText(u"重置"), on_press = ResetInput)
        resetButtonAttrMap = urwid.AttrMap(resetButton, None, 'reveal focus')
        returnButton = urwid.Button(self.AlignButtonText(u"返回主界面"), on_press = ReturnMainWindow)
        returnButtonAttrMap = urwid.AttrMap(returnButton, None, 'reveal focus')

        bottomColumn = urwid.Columns(
            (
                ('fixed', self.buttonWidth, submitButtonAttrMap),
                ('fixed', self.buttonWidth, resetButtonAttrMap),
                ('fixed', self.buttonWidth, returnButtonAttrMap),
            ),
        )

        content.append(tipsTextLineBox)
        content.append(usernameEditAttrMap)
        content.append(passwordEditAttrMap)
        content.append(bottomColumn)

        simpleListWalker = urwid.SimpleListWalker(content)
        self.lb=urwid.ListBox(simpleListWalker)

        listBox = urwid.AttrMap(self.lb, 'standard')
        return listBox

    def BodyArea(self):

        passwordWidget = self.CreatePasswordDialog()

        buttomText = urwid.Text(u"")
        buttomTextFiller = urwid.Filler(buttomText, valign = 'top')
        buttomTextAttrMap = urwid.AttrMap(buttomTextFiller, 'bg')

        self.widgetList = (
            passwordWidget,
            buttomTextAttrMap,
        )

        pile = urwid.Pile(self.widgetList, focus_item = 0)
        return pile
    def Key_Press(self,input):
        if input in ('enter',):
            ww,po=self.lb.get_focus()
            if po==2:
                username=self.usernameEdit.get_edit_text()
                password=self.passwordEdit.get_edit_text()
                state=self.action.UserLogin(username,password)
                if state:
                    self.FileWriteLines(self.temporaryFile['loginState'],["1",])
                    raise urwid.ExitMainLoop

                if self.tmpLoginCounter<self.maxLoginFailCounter:
                    self.tipsText.set_text(u"第 %d 次登陆失败，还有 %d 次机会" % (self.tmpLoginCounter, self.maxLoginFailCounter - self.tmpLoginCounter))
                    self.tmpLoginCounter +=1
                else:
                    raise urwid.ExitMainLoop
                 

    def CreateMainWindow(self):
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)

        mainFrame = urwid.Frame(self.BodyArea())
        self.mainFrame = urwid.LineBox(mainFrame)

        self.loop = urwid.MainLoop(self.mainFrame, palette = self.palette,
            input_filter = None, unhandled_input = self.Key_Press,
        )
        self.loop.run()

class FirstScreen(Base):
    def __init__(self):
        Base.__init__(self)

        self.action = Interface.Action()

    def KeypressHandler(self, input, raw):
        #import pdb;pdb.set_trace()
        if 'f2' in input:
            if not os.path.isdir(self.temporaryFile['rootDir']):
                os.makedirs(self.temporaryFile['rootDir'])

            del self.mainFrame

            self.FileWriteLines(self.temporaryFile['loginState'], ['0',], newline = 'no')

            loginScreen = LoginScreen()
            loginScreen.CreateMainWindow()

            state = self.FileReadLines(self.temporaryFile['loginState'])[0]
            # Into configuration/view screen if login success
            if int(state):
                subWindow = ConfigAndView()
                subWindow.CreateMainWindow()

            # Return to first main window if login failed
            self.CreateMainWindow()

        elif "ctrl _" in input:

            self.action.ToShell()

        #elif 'f12' in input:
        #    raise RuntimeError, u'关机或重启系统'

    def HandleOnCr(self, input):
        pass

    def LoginStateCheck(self):
        """Return current login state"""

        loginStateFile = self.temporaryFile['loginState']
        state = 0

        if os.path.isfile(loginStateFile):
            state = self.FileReadLines(loginStateFile)[0]
            if not state:
                state = 0
                try:
                    os.makedirs(os.path.dirname(loginStateFile))
                    self.FileWriteLines(loginStateFile, ["%s" % state, ], newline = 'no')
                except OSError, e:
                    pass
        else:
            os.makedirs(os.path.dirname(loginStateFile))
            self.FileWriteLines(loginStateFile, ["%s" % state, ], newline = 'no')

        return state

    def BodyArea(self):

        def SetSystemVersionInformation():
            return self.action.GetSystemVersionInformation()

        versionInformationText = urwid.Text(u"")
        textVersion = urwid.Filler(versionInformationText, valign = 'top')
        textVersionAttrMap = urwid.AttrMap(textVersion, 'header')

        tipsText = urwid.Text(u"")
        textTips = urwid.Filler(tipsText, valign = 'top')
        textTipsAttrMap = urwid.AttrMap(textTips, 'bg')

        versionString = self.action.GetSystemVersionInformation()
        versionInformationText.set_text(versionString)
        tipsString = self.action.GetSystemTipsInformation()
        tipsText.set_text(tipsString)

        self.widgetList = (
            textVersionAttrMap,
            textTipsAttrMap,
         )

        pile = urwid.Pile(self.widgetList, focus_item = 0)
        return pile

    def FooterArea(self):
        text1 = urwid.Text(u"<F2> 登陆设置系统")
        #text2 = urwid.Text(u"<F12> 关机或重启系统")
        
        #columnFrame = urwid.Columns([text1, text2], dividechars = 4)
        columnFrame = urwid.Columns([text1,], dividechars = 4)
        return columnFrame
        
    def CreateMainWindow(self):
        self.screen = urwid.raw_display.Screen()
        self.screen.set_terminal_properties(256)

        mainFrame = urwid.Frame(self.BodyArea(), footer = self.FooterArea())
        self.mainFrame = urwid.LineBox(mainFrame)

        self.loop = urwid.MainLoop(self.mainFrame, palette = self.palette,
            input_filter = self.KeypressHandler, unhandled_input = self.HandleOnCr,
        )
        self.loop.run()

def RedirectStdoutStdinStderr():

    # e.g to be start latest
    time.sleep(5)
    num = 0
    while True:
        time.sleep(3)
        num += 1
        if num > 20:
            break
        cmd = "ps ax |grep S99vmd"
        (flag, strs) = commands.getstatusoutput(cmd)
        if 0 != flag:
            continue
        if "/etc/rc3.d/S99vmd" in strs:
            continue
        time.sleep(3)
        break
        

    for f in sys.stdout, sys.stderr: f.flush( )
    si = file("/dev/tty0", 'r')
    so = file("/dev/tty0", 'a+')
    se = file("/dev/tty0", 'a+', 0)
    os.dup2(si.fileno( ), sys.stdin.fileno( ))
    os.dup2(so.fileno( ), sys.stdout.fileno( ))
    os.dup2(se.fileno( ), sys.stderr.fileno( ))

if __name__ == '__main__':

    RedirectStdoutStdinStderr()

    try:
        obj = FirstScreen()
        mainFrame = obj.CreateMainWindow()
    except KeyboardInterrupt, e:
        os.system("clear")
        print u"用户终止"
    except RuntimeError, e:
        os.system("clear")
        urwid.ExitMainLoop()
        print u'%s' % e
