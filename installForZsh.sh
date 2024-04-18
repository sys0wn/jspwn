#!/bin/zsh

sudo mkdir /opt/jspwn/
sudo cp requirements.txt /opt/jspwn/requirements.txt
sudo cp jspwn.py /opt/jspwn/
cd /opt/jspwn
sudo python3 -m venv venv
source /opt/jspwn/venv/bin/activate
sudo pip install -r requirements.txt
echo 'alias jspwn="source /opt/jspwn/venv/bin/activate && python3 /opt/jspwn/jspwn.py"' >> ~/.zshrc
source ~/.zshrc
echo "Please open up a new shell for the jspwn command to become available"
