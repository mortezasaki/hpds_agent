#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Install the required Python packages
pip3 install -r requirements.txt


PROJECT_DIR=/usr/bin/hpds_agent
AGENT=$PROJECT_DIR/run.py

# Copy project files to the usr directory
cp -r src/agent $PROJECT_DIR

# Add the project to the crontab to run every minute
crontab -l > mycron
echo "* * * * * /usr/bin/python3 ${AGENT}" >> mycron
crontab mycron
rm mycron