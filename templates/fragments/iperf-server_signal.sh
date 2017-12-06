#!/bin/bash
. /etc/sysconfig/heat-params

sh -c "${WC_NOTIFY} --data-binary '{\"status\": \"SUCCESS\"}'"
