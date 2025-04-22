# 🧪 Advanced Network & Device Troubleshooting Steps  
*For IT staff or experienced users to isolate deeper problems*

---

## 🔹 1. Use `netstat` to Check Active Connections and Listening Ports

**Windows:**
```bash
netstat -ano
```

**Mac/Linux:**
```bash
netstat -an | grep ESTABLISHED
```

✅ **Why this helps:**  
Shows all active connections, listening ports, and process IDs — useful to detect unauthorized services or chatty applications.

---

## 🔹 2. Check for Duplex Mismatches or NIC Errors

**Windows:**
- Open **Device Manager** → **Network Adapters**
- Right-click adapter → **Properties → Advanced**
- Look for **Speed & Duplex**, confirm it's set to `Auto Negotiation`

**Linux:**
```bash
ethtool eth0
```

✅ **Why this helps:**  
Mismatched duplex settings (half vs full) can cause dropped packets, retries, or poor throughput.

---

## 🔹 3. Review System Logs for Network Stack or Driver Errors

**Windows:**
- Open **Event Viewer → Windows Logs → System**
- Filter by **Event Source = Tcpip, Dhcp, DNS Client, NDIS**

**Linux/Mac:**
```bash
dmesg | grep -i network
journalctl -xe | grep -i network
```

✅ **Why this helps:**  
Driver or stack errors will often log here, giving clues to failing hardware or software modules.

---

## 🔹 3. Capture Packets with Wireshark or TCPDump

**Windows/Mac/Linux:**
- Use **Wireshark** GUI to capture traffic on interface (filter with `ip.addr == YOUR_IP`)
- Or use `tcpdump`:

```bash
sudo tcpdump -i eth0 -nn -w output.pcap
```

✅ **Why this helps:**  
Allows detailed analysis of network behavior (retransmits, handshake failures, DNS issues). Share `.pcap` files with IT for full inspection.

---

## 🔹 4. Check for Routing Issues or Overlapping Subnets

**How to do it:**
```bash
route print           # Windows
ip route              # Linux
netstat -rn           # macOS
```

✅ **Why this helps:**  
Verifies that traffic is being routed correctly. Misconfigured routes can cause local reachability issues or unexpected drops.

---

## 🔹 5. Look at DNS Cache and Flush if Needed

**Windows:**
```bash
ipconfig /displaydns
ipconfig /flushdns
```

**Mac:**
```bash
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

✅ **Why this helps:**  
Sometimes DNS cache contains outdated or incorrect entries. Clearing it can fix name resolution issues.

---

## 🔹 6. Examine Interface Statistics

**Windows:**
```powershell
Get-NetAdapterStatistics
```

**Linux:**
```bash
cat /proc/net/dev
```

✅ **Why this helps:**  
Shows dropped packets, errors, collisions, etc., per interface — helpful for spotting low-level NIC problems.

---

## 🔹 7. Test External DNS Services

```bash
nslookup google.com 8.8.8.8
nslookup google.com 1.1.1.1
```

✅ **Why this helps:**  
Rules out internal DNS issues by testing against known public resolvers (Google, Cloudflare).