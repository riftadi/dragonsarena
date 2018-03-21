#!/bin/bash

sudo pkill Python -m server.Server
sudo pkill Python -m client.run_client

sudo kill -9 $(ps aux | grep client.Observer | grep -v grep | awk '{print $2}')
# sudo kill -9 $(ps aux | grep client.run_client | grep -v grep | awk '{print $2}')
# sudo kill -9 $(ps aux | grep server.run_server | grep -v grep | awk '{print $2}')
