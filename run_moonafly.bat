@echo off

if exist "config.json" (
    echo Starting Moonafly...
    cd src
    python main.py
) else (
    echo Please setup Moonafly first using init_Moonafly script
)