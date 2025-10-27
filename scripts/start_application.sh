#!/usr/bin/env bash

current_datetime=$(date +"%Y-%m-%d %H:%M:%S")
echo "----"
echo "Running start installation script..." >> /home/admin/hook.log
echo "Current date and time: $current_datetime" >> /home/admin/hook.log
echo "----"

# Copy service file
sudo cp "$APP_LOCATION/script/mange-ta-main.service" /etc/systemd/system/mange-ta-main.service

# Reload systemd
sudo systemctl enable mange-ta-main.service >> /home/admin/hook.log

sudo systemctl daemon-reload >> /home/admin/hook.log

sudo systemctl restart mange-ta-main.service
