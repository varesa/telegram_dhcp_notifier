#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
  exit 1
fi

install dhcp_notifier.service /etc/systemd/system/dhcp_notifier.service

systemctl daemon-reload

echo "Please copy this folder to /opt/telegram_dhcp_notifier/ and fill in \$dir/vars"
