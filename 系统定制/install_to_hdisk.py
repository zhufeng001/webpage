# -*- coding: utf-8 -*-



import support.log.edbglog
import support.log.vmd_log
import global_params
import eventlog_db_op
import system.timeadmin.public_long_time
import check_install_tohd
import clusterd_paramsreturn
import install_vserver_livecd
import install_vcenter_livecd


def web_install_to_harddisk(params):

    if "optionobject" not in params:
        params["optionobject"] = "localhost"

    diskobj = params["harddisk"]
    #e.g for install type check
    livecdflag = False
    (flag, stat) = (False, "not support install")
    if check_install_tohd.check_usb_system():
        livecdflag = True
    try:
        if livecdflag:
            if global_params.vsflag:
                (flag, stat) = install_vserver_livecd.installvserver({"param":params})
            else:
                (flag, stat) = install_vcenter_livecd.installvcenter({"param":params})
    except:
        support.log.edbglog.caught()
        try:
            evparams = {}
            evparams["usparam"] = params
            evparams["stparam"] = params
            stat = "Install to harddisk, Maybe info incomplete" #@@
            eventlog_db_op.whteventlog("host",diskobj,params,"error","False",diskobj,stat,diskobj)
            clusterd_paramsreturn.return_percentage_finish(evparams,100,stat,"False")
            support.log.vmd_log.log_others("host",diskobj,params,"error","False",diskobj,stat)
        except:
            pass
        return
    try:
        evparams = {}
        evparams["usparam"] = params
        evparams["stparam"] = params
        level = "error"
        if flag:
            level = "warn"
        eventlog_db_op.whteventlog("host",diskobj,params,"error","False",diskobj,stat,diskobj)
        clusterd_paramsreturn.return_percentage_finish(evparams,100,stat,flag)
        support.log.vmd_log.log_others("host",diskobj,params,level,str(flag),diskobj,stat)
    except:
        pass
    return

def do_web_install_to_harddisk(params):

    params["optimizationpct"] = 6
    params["opname"] = "Install to HD"
    params["interface_name"] = "do_web_install_to_harddisk"
    params['sub_name']='install_to_hdisk.web_install_to_harddisk'
    return system.timeadmin.public_long_time.public_do(params)
