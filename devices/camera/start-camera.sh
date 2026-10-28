#!/bin/bash
echo "Starting heartbeat..."
nohup python3 -u /opt/heartbeat.py > /opt/heartbeat.log 2>&1 &
echo "camera-01 heartbeat started."