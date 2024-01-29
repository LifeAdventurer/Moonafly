@echo off
setlocal enabledelayedexpansion

rem Check if "config.json" exists
if exist config.json (
    echo "config.json" found.
) else (
    echo "config.json" not found.
    set /p botToken=Enter your Discord bot token: 
    echo { "token": "!botToken!" } > config.json
    echo "config.json" created with the provided bot token.
)

rem Check if "user_identity.json" exists in the "data\json" directory
if exist data\json\user_identity.json (
    echo "user_identity.json" found.
) else (
    echo "user_identity.json" not found.
    set /p discordUsername=Enter your Discord username: 
    echo { "author": "!discordUsername!", "developers": [ "!discordUsername!" ], "guests": [ "!discordUsername!" ] } > data\json\user_identity.json
    echo "user_identity.json" created with the provided Discord username.
)

echo Initialization completed.

endlocal
