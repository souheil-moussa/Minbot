# Minbot
![Logo](images/minbot.png?raw=true)
## An AI powered meeting Assitant

# MinBot Setup Guide

## Controller Setup (Do Once)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-directory>
```

### 2. Install NPM Packages

Navigate to the `controller/wss/` directory and install dependencies:

```bash
cd controller/wss/
npm install
```

### 3. Set Script Permissions

Ensure the server scripts are executable:

```bash
sudo chmod +x start_server.sh stream_start.sh stream_stop.sh
```

### 4. Create systemd Service

Create a service file for the WebSocket server:

```bash
sudo nano /lib/systemd/system/wss.service
```

Paste the following configuration (replace `/path/to/start_server.sh` with the actual path):

```ini
[Unit]
Description=MinBot Control Server
After=multi-user.target

[Service]
Type=idle
ExecStart=/path/to/start_server.sh

[Install]
WantedBy=multi-user.target
```

Save the file, then set the correct permissions:

```bash
sudo chmod 644 /lib/systemd/system/wss.service
```

### Usage Instructions

- Enable the service to start on boot:
  ```bash
  sudo systemctl enable wss.service
  ```

- Disable the service:
  ```bash
  sudo systemctl disable wss.service
  ```

- Start the service manually:
  ```bash
  sudo systemctl start wss.service
  ```

- Stop the service manually:
  ```bash
  sudo systemctl stop wss.service
  ```

- Restart the service:
  ```bash
  sudo systemctl restart wss.service
  ```

- View logs:
  ```bash
  journalctl -u wss.service -f
  ```

---

## Main Machine Setup

### 1. Install Docker

Follow Docker installation instructions for your system:  
👉 https://docs.docker.com/get-docker/

### 2. Start the Container

Run the following command (replace placeholders with actual values):

```bash
docker run -d -v <path/to/segment/output>:/usr/local/apache2/out \
  -p 8080:80 --rm --name <container-name> souheilmoussa/minbot
```

- This will pull the image from Docker Hub and start the server.
- The website will be accessible at:  
  **http://localhost:8080**

### 3. Stop the Container

```bash
docker stop <container-name>
```
## Fixing Microphone Device Number

If the stream fails with a "device not found" error, follow these steps:

1. Run the following command to list audio capture devices:
   ```bash
   arecord -l
   ```

2. Look for your microphone in the output.

3. Open the `stream_start.sh` script in a text editor:
   ```bash
   nano stream_start.sh
   ```

4. Replace the device string (e.g., `plughw:0,0`) with the correct numbers based on the output.

### Notes:
- The format is: `plughw:<card>,<device>`
- The **first number** is the **card** number.
- The **second number** is the **device** number.

### Example:

If `arecord -l` outputs:
```
card 1: Microphone [USB Microphone], device 0: USB Audio [USB Audio]
```

Then the correct device string is:
```
plughw:1,0
```

Update this value in your `stream_start.sh` script accordingly.

This number my change with restarts or when repluging the microphone
