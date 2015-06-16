#!/bin/sh
#
# chkconfig: - 99 01
# description: fviweb
#
. /etc/init.d/functions

start () {
    cd /etc/FVIweb/ && python TerminalUI.py &
}

stop () {

    for pid in `ps ax |grep TerminalUI.py |sed -e 's/ *//' -e 's/ .*//'`
        do
        kill -9 $pid
        done

}


case "$1" in
    start)
        start
        exit $?
        ;;

    stop)
        stop
        exit $?
        ;;

    *)
        echo "Unknown command: $command" >&2
        echo 'Valid commands are: start, stop' >&2
        exit 1
esac

