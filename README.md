# Minecraft Server Discord Bot

A Discord bot that monitors a Minecraft server and provides real-time updates about its status. This bot allows server administrators to manage server notifications, maintenance mode, and server configuration directly from Discord.

---

## Features

- **Server Status Monitoring**: Continuously checks if the Minecraft server is online, offline, or under maintenance.
- **Player Information**: Displays the number of online players, the maximum capacity, and up to 10 player names.
- **Maintenance Mode**: Toggle maintenance mode to indicate server downtime.
- **Ping Command**: Measure bot latency, server latency, and Minecraft server ping.
- **Dynamic Channel Renaming**: Automatically updates a Discord channel name to reflect server status.
- **Configuration Commands** (Admin-only):
  - `!setip <ip>` – Set a new Minecraft server IP.
  - `!setport <port>` – Set a new Minecraft server port.
  - `!setUpdateChannel <channel_id>` – Set the channel for status updates.
  - `!setChannelToRename <channel_id>` – Set the channel that will be renamed with the status.
  - `!updateInterval <seconds>` – Set the update interval for server checks.
- **Manual Status Command**: `!status` displays the current server status in an embedded message.
- **Custom Font Display**: Status messages and channel names use Unicode Math Bold characters for a unique look.

---

## Requirements

- Python 3.10+
- `discord.py`
- `mcstatus`
- A Discord bot token
- A Minecraft server to monitor

---
