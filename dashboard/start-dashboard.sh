#!/bin/bash
echo "Starting dashboard..."
cd /opt
nohup python3 /opt/dashboard.py > /opt/dashboard.log 2>&1 &
echo "dashboard-01 started."