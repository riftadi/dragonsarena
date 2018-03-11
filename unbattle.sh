#!/bin/bash
sudo pkill Python -m server.Server
sudo pkill Python -m client.run_client
sudo pkill Python -m client.Observer
