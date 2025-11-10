#!/bin/bash

# Ready services
sudo cp flask.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now redis6
sudo systemctl enable --now flask