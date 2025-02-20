#!/bin/sh
python3 app.py &  # Run the web server in the background
python3 sockets.py  # Run the socket server
