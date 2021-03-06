#!/bin/bash

set -e

while fuser /var/lib/dpkg/lock >/dev/null 2>&1 ; do
    echo "Wait for apt-get"
    sleep 2
done

while fuser /var/lib/apt/lists/lock >/dev/null 2>&1 ; do
    echo "Wait for apt-get"
    sleep 2
done

. /etc/sysconfig/heat-params

apt-get update | tee /root/output.txt -a
apt-get -y install iperf | tee /root/output.txt -a

iperf -s 2> /var/log/iperf.log &

