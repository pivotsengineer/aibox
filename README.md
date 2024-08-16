# Service Management

##service reload
sudo systemctl daemon-reload

##Enable the services to start on boot:
sudo systemctl enable sockets.service
sudo systemctl enable app.service

##Start the services
sudo systemctl start sockets.service
sudo systemctl start app.service

##Check the Status
sudo systemctl status sockets.service
sudo systemctl status app.service

##You can view the logs for your services using journalctl
sudo journalctl -u sockets.service
sudo journalctl -u app.service
