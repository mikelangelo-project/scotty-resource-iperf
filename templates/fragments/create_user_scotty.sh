#!/bin/bash

. /etc/sysconfig/heat-params

echo "Creating $SCOTTY_USER user"
groupadd $SCOTTY_USER
useradd $SCOTTY_USER -g $SCOTTY_USER -G sudo --shell /bin/bash --create-home
echo "${SCOTTY_USER}:${SCOTTY_PASSWORD}" | chpasswd

echo "scotty ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/90-sudo-scotty-without-password
echo "" >> /etc/ssh/sshd_config
echo "AllowUsers scotty" >> /etc/ssh/sshd_config

systemctl restart sshd
