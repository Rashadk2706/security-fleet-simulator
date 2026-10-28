# Cloud Managed Security Fleet Simulator

A self hosted Proxmox lab that simulates a segmented, cloud managed IoT device fleet including cameras, access control, and environmental sensors that phone home to a central monitoring dashboard over an outbound only connection. Built to explore how hybrid cloud physical security platforms (cameras and sensors with no port forwarding, no VPN) actually work under the hood, by building a working miniature version of that architecture from scratch.

## How it's built

**Isolated network, fully separate from my home network.** The entire lab runs on its own VLAN aware Linux bridge (`vmbr1`) inside Proxmox, with no physical NIC attached to it. That means this bridge has no path to my home router or home LAN at all. It is a closed virtual network that only exists inside the Proxmox host. A dedicated pfSense VM sits at the edge of it, with one NIC on my actual home network for WAN (internet access and updates only) and a second NIC on the isolated bridge for LAN. pfSense is the only thing bridging the two, and it is configured to accept zero inbound connections from the WAN side. No port forwards, ever.

**Four VLANs, each its own segment.** On top of that isolated bridge, pfSense creates four tagged VLANs: CAMERAS, ACCESS CONTROL, SENSORS, and MGMT, each with its own subnet and its own DHCP pool. Every device VLAN is restricted by firewall rule to talk to exactly one destination, the MGMT dashboard, on port 443, and nothing else. No internet access, and no reaching other device VLANs. A camera container has no network path to a door controller container even though they sit on the same physical server. This is enforced entirely at the firewall layer.

**Devices are lightweight Debian LXC containers, not full VMs.** Each simulated device, camera, door controller, and sensor, is a Proxmox LXC container running a minimal Debian image rather than a full virtual machine. LXC containers share the host's kernel instead of virtualizing their own hardware, which makes them cheap to spin up, tear down, and run in parallel. This is ideal for simulating a whole device fleet on one physical server without the overhead a full VM per device would carry. Each container is tagged onto its matching VLAN at the network device level in Proxmox, which is what actually determines which VLAN it lands on. The subnet naming is just a human readable label, the VLAN tag is the real mechanism.

**Every device phones home. Nothing is polled.** Instead of a central system reaching out to check on each device, every device runs a small Python heartbeat script that independently pushes its own status to the dashboard every 30 seconds over HTTPS. The dashboard just listens and records what arrives. This mirrors how real managed device fleets avoid needing any inbound access to the devices at all, since the device always initiates the connection outward.


## What each script actually does

**`dashboard.py`** is the core of the project. A small Flask web app with two jobs. It exposes `POST /api/heartbeat`, which every device calls every 30 seconds to report `{device_id, type, status, timestamp}`. It also exposes `GET /`, which renders a live HTML table of every known device, marked online (green) or offline (red) depending on whether its last heartbeat arrived within the last 90 seconds. All device state is stored in a local SQLite database file (`dashboard.db`), with one row per device that gets overwritten on every new heartbeat rather than growing a history log.

**`heartbeat.py`** (one version per device type) is a small loop. Build a JSON payload identifying the device, POST it to the dashboard's `/api/heartbeat` endpoint, wait 30 seconds, repeat, forever. Each device's copy only differs by its `DEVICE_ID` and `DEVICE_TYPE` values. This is the only thing that makes a container "a device" from the dashboard's point of view. Nothing else about the container matters to the simulation.

**`sensor.py`** generates randomized but realistic looking temperature and air quality readings on a timer, standing in for a real environmental sensor's data feed.

**`start-*.sh` scripts** condense each device's startup into one script so relaunching everything after a reboot does not mean retyping commands from memory. Every script backgrounds its process with `nohup`, so it survives the console session ending, though not a full container reboot. These still need to be rerun manually after a restart unless they are later converted to systemd services.

## Running it

Each container needs its script run once per session or after each reboot.

**Dashboard** (on the MGMT VLAN container):
```bash
cd dashboard
pip3 install -r requirements.txt --break-system-packages
chmod +x start-dashboard.sh
./start-dashboard.sh
```

**Each device** (on its respective container):
```bash
chmod +x start-camera.sh
./start-camera.sh
```

**To confirm it's working**, on the dashboard container:
```bash
sqlite3 dashboard/dashboard.db "SELECT * FROM devices;"
```
Each row shows a device ID, type, status, and the timestamp of its last heartbeat.
