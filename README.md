# 🖥️ Minecraft Server Discord Bot

A Discord bot that monitors a Minecraft server in real-time and updates its status directly on your server. Perfect for server admins who want live server info and player activity updates.

---

## 🚀 Features

- **Server Status Monitoring**  
  Tracks if the Minecraft server is **Online**, **Offline**, or under **Maintenance**.

- **Player Information**  
  Shows the number of players online, maximum capacity, and up to 10 player names.

- **Maintenance Mode**  
  Toggle maintenance mode with `!maintenance on/off`.

- **Ping Command**  
  Test bot latency, server latency, and Minecraft server ping.

- **Dynamic Channel Renaming**  
  Automatically updates a Discord channel name to show the server status.

- **Admin Configuration Commands**  
  - `!setip <ip>` – Change Minecraft server IP  
  - `!setport <port>` – Change Minecraft server port  
  - `!setUpdateChannel <channel_id>` – Set channel for status updates  
  - `!setChannelToRename <channel_id>` – Set channel to rename with status  
  - `!updateInterval <seconds>` – Set update interval (25–300s)  

- **Manual Status Command**  
  `!status` shows the current server status in an embedded message.

- **Custom Font**  
  Status messages and channel names use Unicode Math Bold for a unique look.

---

## ⚙️ Requirements

- Python 3.10+  
- `discord.py`  
- `mcstatus`  
- A Discord bot token  
- A Minecraft server to monitor  

---

## 📦 Installation

1. **Clone the repository**  

```bash
git clone [https://github.com/your-username/your-bot-repo.git](https://github.com/Wolfy3870/Discord-bot-for-Minercraft-server-status.git)
cd Discord-bot-for-Minercraft-server-status
