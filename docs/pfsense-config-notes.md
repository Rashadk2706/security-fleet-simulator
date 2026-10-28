# pfSense Configuration Notes

#configured a linux bridge without any physcial port connections, Network is fully isolated. 

## VLANs (on vmbr1, LAN NIC)

| VLAN Name | Tag | Subnet         | Gateway IP   |
|-----------|-----|----------------|--------------|
| CAMERAS   | 110 | 10.10.110.0/24 | 10.10.110.1  |
| ACCESS    | 120 | 10.10.120.0/24 | 10.10.120.1  |
| SENSORS   | 130 | 10.10.130.0/24 | 10.10.130.1  |
| MGMT      | 99  | 10.10.99.0/24  | 10.10.99.1   |

## DHCP

Each device VLAN (CAMERAS/ACCESS/SENSORS) hands out .100-.200.
MGMT hands out a smaller range.


## Firewall rules (per interface)

**WAN**: no rules. Block bogon networks enabled. No port forwards.

**CAMERAS**: Pass / TCP / Source: CAMERAS net / Destination: 10.10.99.10 (dashboard) / Port: 443. Nothing else passes.

**ACCESS**: same pattern, Source: ACCESS net.

**SENSORS**: same pattern, Source: SENSORS net.

**MGMT**: reachable only from an internal jump host, in this case we are using a container with the isoalted network bridge, and the MGMT VLAN.

**LAN**: default allow any rules removed anti lockout rule retained just in case of lockout.

## Design principle

Every device VLAN can reach the MGMT dashboard on 443 and nothing
else  no internet access, no inter VLAN traffic between device
types. Devices phone home outbound only the network never accepts
unsolicited inbound connections.