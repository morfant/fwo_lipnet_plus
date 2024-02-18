#!/bin/bash
sleep 5.0
cd /Users && open .
sleep 3.0
mount_smbfs //roads22:rx782rx782@MyCloud-0AU6T9._smb._tcp.local/Public/ /Users/NetworkFolder
sleep 5.0
/Applications/Max.app/Contents/MacOS/Max /Users/baggeunsu/fwo_lipnet_plus/max_patch/OSC_manager.maxpat &
/Applications/Resolume\ Arena\ 6/Arena.app/Contents/MacOS/Arena &
cd /Users/baggeunsu/fwo_lipnet_plus && /Users/baggeunsu/.pyenv/versions/3.11.7/bin/python liveCam.py

