#!/bin/bash
. /etc/sysconfig/heat-params

echo "Start to configure iperf as a server"

apt-get update
apt-get install iperf

iperf -s 2> /var/log/iperf.log &
