#!/bin/bash

# Check if "config.json" exists
if [ -e "config.json" ]; then
    echo "config.json found."
else
    echo "config.json not found."
    read -p "Enter your Discord bot token: " botToken
    echo "{ \"token\": \"$botToken\" }" > config.json
    echo "config.json created with the provided bot token."
fi

# Check if "user_identity.json" exists in the "data/json" directory
if [ -e "data/json/user_identity.json" ]; then
    echo "user_identity.json found."
else
    echo "user_identity.json not found."
    read -p "Enter your Discord username: " discordUsername
    echo "{ \"author\": \"$discordUsername\", \"developers\": [ \"$discordUsername\" ], \"guests\": [ \"$discordUsername\" ] }" > data/json/user_identity.json
    echo "user_identity.json created with the provided Discord username."
fi

echo "Initialization completed."
