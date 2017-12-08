#!/bin/bash
set -e

. /etc/sysconfig/heat-params

echo "Start to configure iperf as a client"

#echo cloud:secred | /usr/sbin/chpasswd

apt-get update
apt-get -y install iperf

