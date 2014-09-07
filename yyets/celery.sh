#!/bin/bash

function test()
{
    echo 'haha'

}
function start()
{
    nohup celery -A tasks worker --loglevel=info &
}

function stop()
{
    local pids=`ps aux | egrep 'celery' |egrep -v grep|awk '{print $2}'|egrep -v ^$|egrep -v grep`
    echo $pids
    for pid in `echo $pids`
    do
        kill -9 $pid
    done
}

function restart()
{
    stop
    stop
    rabbitmqctl stop_app
    rabbitmqctl reset
    rabbitmqctl start_app
    start

}

if [ $# == 1 ] ; then
    if [ $1 == 'start' ] ; then
        start
    elif [ $1 == 'stop' ] ; then
        stop
    elif [ $1 == 'restart' ] ; then
        restart
    elif [ $1 == 'test' ] ; then
        test
    fi
fi
