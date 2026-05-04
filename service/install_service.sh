#!/bin/bash

USER_NAME=$(whoami)

sudo cp service/schoolbell.service /etc/systemd/system/schoolbell.service
sudo sed -i "s/%i/$USER_NAME/g" /etc/systemd/system/schoolbell.service

sudo systemctl daemon-reload
sudo systemctl enable schoolbell.service

echo "Service installed."
echo "Use:"
echo "sudo systemctl start schoolbell"
