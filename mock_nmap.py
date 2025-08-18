#!/usr/bin/env python3
"""
Mock Nmap for testing purposes
"""

import sys
import json

def mock_nmap_xml_output(target):
    """Generate mock nmap XML output"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV -sC {target}" start="1692345678" startstr="Fri Aug 18 07:34:38 2025" version="7.80" xmloutputversion="1.04">
<scaninfo type="syn" protocol="tcp" numservices="1000" services="1-1000"/>
<verbose level="0"/>
<debugging level="0"/>
<host starttime="1692345678" endtime="1692345680">
<status state="up" reason="echo-reply" reason_ttl="64"/>
<address addr="{target}" addrtype="ipv4"/>
<hostnames>
<hostname name="test-host.local" type="PTR"/>
</hostnames>
<ports>
<port protocol="tcp" portid="22">
<state state="open" reason="syn-ack" reason_ttl="64"/>
<service name="ssh" product="OpenSSH" version="8.2p1" method="probed" conf="10"/>
</port>
<port protocol="tcp" portid="80">
<state state="open" reason="syn-ack" reason_ttl="64"/>
<service name="http" product="Apache httpd" version="2.4.41" method="probed" conf="10"/>
</port>
<port protocol="tcp" portid="443">
<state state="open" reason="syn-ack" reason_ttl="64"/>
<service name="https" product="Apache httpd" version="2.4.41" method="probed" conf="10"/>
</port>
</ports>
<os>
<osmatch name="Linux 4.15 - 5.6" accuracy="95" line="54321"/>
</os>
</host>
<runstats>
<finished time="1692345680" timestr="Fri Aug 18 07:34:40 2025" elapsed="2.34" summary="Nmap done at Fri Aug 18 07:34:40 2025; 1 IP address (1 host up) scanned in 2.34 seconds" exit="success"/>
</runstats>
</nmaprun>"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: mock_nmap.py <target>")
        sys.exit(1)
    
    # Check for --version flag
    if "--version" in sys.argv:
        print("Nmap version 7.80 ( https://nmap.org )")
        print("Platform: linux")
        print("Compiled with: liblua-5.3.3 openssl-1.1.1 libssh2-1.8.0 libz-1.2.11 libpcre-8.39 libpcap-1.8.1 nmap-libdnet-1.12 ipv6")
        print("Compiled without:")
        print("Available nsock engines: epoll poll select")
        sys.exit(0)
    
    # Mock scan output
    target = sys.argv[-1]  # Last argument is usually the target
    
    # Check for XML output flag
    if "-oX" in sys.argv:
        print(mock_nmap_xml_output(target))
    else:
        print(f"Starting Nmap 7.80 ( https://nmap.org ) at {target}")
        print(f"Nmap scan report for {target}")
        print("Host is up (0.001s latency).")
        print("PORT   STATE SERVICE VERSION")
        print("22/tcp open  ssh     OpenSSH 8.2p1")
        print("80/tcp open  http    Apache httpd 2.4.41")
        print("443/tcp open https   Apache httpd 2.4.41")
        print("")
        print("Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds")