#!/usr/bin/env bash

current_datetime=$(date +"%Y-%m-%d %H:%M:%S")
echo "----"
echo "Running post-installation script..." >> /home/admin/hook.log
echo "Current date and time: $current_datetime" >> /home/admin/hook.log
echo "----"

# /home/admin/.local/bin/hatch run production:init_data &>> /home/admin/hook.log
