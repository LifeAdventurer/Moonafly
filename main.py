import json
import os
import subprocess
import time

EXEC_PATH = ["python", "bot.py"]

print("Starting Moonafly...")

init = False

# Check if "config.json" exists
if not os.path.isfile("config.json"):
    init = True
    print('"config.json" not found')
    bot_token = input("Enter your Discord bot token: ")
    with open("config.json", "w") as f:
        json.dump({"token": bot_token}, f, indent=4)
    print('"config.json" created with the provided bot token.')

# Check if "user_identity.json" exists in the "data/json" directory
if not os.path.isfile("./data/json/user_identity.json"):
    init = True
    print('"user_identity.json" not found.')
    discord_username = input("Enter your Discord username: ")
    user_identity_data = {
        "author": discord_username,
        "developers": [discord_username],
        "guests": [discord_username],
    }
    with open("./data/json/user_identity.json", "w") as f:
        json.dump(user_identity_data, f, indent=4)
    print('"user_identity.json" created with the provided Discord username.')

if init:
    print("Moonafly Initialization completed.")

os.chdir("src")

subprocess_args = {
    "stderr": subprocess.PIPE,
    "encoding": "utf-8",
    "bufsize": 0,
}

pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)

while True:
    try:
        stderr = pipe.stderr.readline().strip()
    except UnicodeDecodeError:
        stderr = "Unable to decode stderr"
    if stderr:
        print(stderr)
    if "Restarting Moonafly..." in stderr:
        pipe.kill()
        pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)
        continue
    elif "Moonafly stopped by command" in stderr:
        os._exit(0)
    # Introduce a short sleep to avoid busy-waiting
    time.sleep(0.1)
