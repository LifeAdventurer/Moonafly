#!/bin/bash

if [ -e "config.json" ]; then
    echo "Starting Moonafly..."
    cd src || exit
    python main.py
else
    echo "Please setup Moonafly first using init_Moonafly script"
fi