# create services
sudo touch /etc/systemd/system/sockets.service

Add the following content to the file:

```
[Unit]
Description=Socket Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/sergienko/newton/sockets.py
Restart=always
User=sergienko
WorkingDirectory=/home/sergienko/newton
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
ExecStart=/usr/bin/python3 /home/sergienko/newton/app.py
Restart=always
User=sergienko
WorkingDirectory=/home/sergienko/newton
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=app
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
sudo systemctl enable app.service
```

##Start the services
```
sudo systemctl start sockets.service
sudo systemctl start app.service
```

##Check the Status
```sudo systemctl status sockets.service
sudo systemctl status app.service
```

##You can view the logs for your services using journalctl
```sudo journalctl -u sockets.service
sudo journalctl -u app.service
```
