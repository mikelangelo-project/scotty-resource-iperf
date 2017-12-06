#!/bin/bash
. /etc/sysconfig/heat-params

echo "Start to configure iperf as a client"

apt-get update
apt-get install iperf

