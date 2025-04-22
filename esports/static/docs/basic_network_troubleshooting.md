# 🖧 Basic Network Troubleshooting Instructions  
*For staff with limited networking experience*

Please follow the steps below to check your computer’s network connection. After completing these steps, share screenshots or results with your IT support team.

---

## 🔹 1. Check if You're Connected to the Network

**How to do it:**
- **Windows:**  
  - Look at the bottom-right system tray.  
  - Hover over the **Wi-Fi or Ethernet icon** — it should say “Connected” or show your network name.

- **Mac:**  
  - Top-right menu bar → **Wi-Fi symbol** or **Ethernet symbol**  
  - It should show a connected network.

✅ **Why this helps:**  
Confirms the device is physically or wirelessly connected to a network.

---

## 🔹 2. Run a Basic Internet Test (ping)

**How to do it:**
- Open the **Command Prompt** (Windows) or **Terminal** (Mac/Linux)
- Type the following and press Enter:

\`\`\`bash
ping 8.8.8.8 -n 10     # Windows
ping -c 10 8.8.8.8     # Mac/Linux
\`\`\`

**What to look for:**  
- You should see replies with **times in ms**
- Note the average time and any **packet loss**

✅ **Why this helps:**  
Measures if the internet is reachable and checks for **latency or packet loss**.

---

## 🔹 3. Test a Website (ping a URL)

**How to do it:**
Still in Command Prompt or Terminal:

\`\`\`bash
ping google.com -n 10      # Windows
ping -c 10 google.com      # Mac/Linux
\`\`\`

**What to look for:**  
- Again, check that replies come back and look for average time.

✅ **Why this helps:**  
Confirms **DNS is working** and whether common websites are reachable.

---

## 🔹 4. Run a Speed Test

**How to do it:**
- Visit [https://www.speedtest.net](https://www.speedtest.net) in your browser.
- Click **Go** and wait for the results.

**What to report:**
- **Download Speed**
- **Upload Speed**
- **Ping**

✅ **Why this helps:**  
Gives a snapshot of your **internet performance**. IT can use this to compare with expected speeds.

---

## 🔹 5. Check for High Network Usage on Your Device

**Windows:**
- Press \`Ctrl + Shift + Esc\` to open Task Manager  
- Go to the **Performance** tab → Click **Wi-Fi** or **Ethernet**  
- You’ll see a graph of usage

**Mac:**
- Open **Activity Monitor** → **Network tab**

✅ **Why this helps:**  
Reveals if your computer is using a lot of bandwidth (e.g., from backups, video calls, updates).

---

## 🔹 6. Run a Traceroute (optional, advanced)

**Windows:**
\`\`\`bash
tracert google.com
\`\`\`

**Mac/Linux:**
\`\`\`bash
traceroute google.com
\`\`\`

✅ **Why this helps:**  
Shows how your data travels across the internet. If it gets stuck or delays appear, IT can locate where the problem is.

---

## ✅ What to Send to IT:
Please email or message us:
- A screenshot or copy/paste of the **ping test**
- A screenshot of the **Speedtest results**
- A screenshot of the **Network usage** graph or task manager
- Any **error messages** you see