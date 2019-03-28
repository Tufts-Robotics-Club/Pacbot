#!/bin/bash

source ~/tfenvcopy/bin/activate
screen -dmS "screen-name-1" ./server.py
screen -dmS "screen-name-3" ./visualize.py -w -p
screen ./tfsim.py 
