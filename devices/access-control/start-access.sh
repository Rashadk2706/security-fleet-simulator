#!/bin/bash
echo "Starting access..."
nohup python3 -u /opt/heartbeat.py > /opt/heartbeat.log 2>&1 &
echo "access-01 heartbeat started."