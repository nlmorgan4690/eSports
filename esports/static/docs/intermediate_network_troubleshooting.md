# 🧠 Intermediate Troubleshooting Steps  
*For users with moderate comfort using system tools*

---

## 🔹 1. View Network Status & IP Info

**Windows:**
- Open **Command Prompt**, type:
  ```bash
  ipconfig /all
  ```
- Look for:
  - **IPv4 Address**
  - **Default Gateway**
  - **DNS Servers**

**Mac/Linux:**
```bash
ifconfig        # or `ip a` on Linux
```

✅ **Why this helps:**  
Shows whether the device has a valid IP address, can help IT diagnose DHCP/DNS issues.

---

## 🔹 2. Check Gateway/Router Reachability

**How to do it:**
- First, find your **Default Gateway** (see previous step).
- Then, run:

```bash
ping [default_gateway_ip]
```

✅ **Why this helps:**  
Verifies if your local router/gateway is responsive — helpful for isolating LAN vs. WAN issues.

---

## 🔹 3. Perform a DNS Lookup Test

**How to do it:**
```bash
nslookup google.com
```

**What to check:**
- The **DNS server** IP used
- Whether it resolves to valid IPs

✅ **Why this helps:**  
Helps determine if **DNS resolution** is failing, which can cause slow or broken web access.

---

## 🔹 4. Save and Share a Traceroute Log

**Windows:**
```bash
tracert google.com > trace_log.txt
```

**Mac/Linux:**
```bash
traceroute google.com > trace_log.txt
```

✅ **Why this helps:**  
Helps IT trace where along the internet path the slowness or failure is occurring.  
Users can send the `trace_log.txt` file to the IT team.

---

## 🔹 5. Capture Local System Events

**Windows:**
- Press `Windows + R`, type: `eventvwr`
- Look under **Windows Logs → System** or **Applications**
- Look for recent **red errors or yellow warnings**

✅ **Why this helps:**  
Sometimes, device issues show up as event logs (e.g., failing network services, hardware errors).

---

## 🔹 6. Identify Background Applications Using Network

**Windows:**
- Open **Task Manager → Processes Tab**
- Sort by **Network column**

**Mac:**
- Open **Activity Monitor → Network Tab**
- Sort by **Sent Bytes / Received Bytes**

✅ **Why this helps:**  
Background apps (e.g., OneDrive, Dropbox, updates) may be hogging bandwidth.

---

## 🔹 7. Try a Wired Connection (if normally on Wi-Fi)

**How to do it:**
- Connect an Ethernet cable directly to the device (if available)
- Test the same websites or tools again

✅ **Why this helps:**  
Rules out Wi-Fi interference or weak signal as the cause of perceived slowness.