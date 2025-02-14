# dependencies
# Update the package list
sudo apt update && sudo apt upgrade -y

# Install libcamera and dependencies
sudo apt install -y libcamera-apps python3-websockets python3-pip lsof fuser

# Install additional Python dependencies
pip3 install websockets


# create services
sudo touch /etc/systemd/system/sockets.service

Add the following content to the file:

```
[Unit]
Description=Socket Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/sergienko/aibox/sockets.py
Restart=always
User=sergienko
WorkingDirectory=/home/sergienko/aibox
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=sockets
Environment=PYTHONUNBUFFERED=

[Install]
WantedBy=multi-user.target
```

sudo touch /etc/systemd/system/newton.service

Add the following content to the file:

```
[Unit]
Description=App Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/sergienko/aibox/app.py
Restart=always
User=root
WorkingDirectory=/home/sergienko/aibox
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=aibox
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

# Service Management

##service reload
sudo systemctl daemon-reload

##Enable the services to start on boot:
```
sudo systemctl enable sockets.service
sudo systemctl enable aibox.service
```

##Start the services
```
sudo systemctl start sockets.service
sudo systemctl start aibox.service
```

##Check the Status
```sudo systemctl status sockets.service
sudo systemctl status aibox.service
```

##You can view the logs for your services using journalctl
```sudo journalctl -u sockets.service
sudo journalctl -u aibox.service
```
