#!/bin/bash

function test()
{
    echo 'haha'

}

function start_celery()
{
    nohup celery -A tasks worker --loglevel=info > nohup_celery.log &2>1 &
}

function stop()
{
    local pids=`ps aux | egrep 'bin/celery' |egrep -v grep|awk '{print $2}'|egrep -v ^$|egrep -v grep`
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
    start_celery

}
function restart_rabbit()
{
    rabbitmqctl stop_app
    rabbitmqctl reset
    rabbitmqctl start_app

}

if [ $# == 1 ] ; then
    if [ $1 == 'start' ] ; then
        start_celery
    elif [ $1 == 'stop' ] ; then
        stop
    elif [ $1 == 'restart' ] ; then
        restart
    elif [ $1 == 'restart_rabbit' ] ; then
        restart_rattbit
    fi
fi
