import os
import subprocess
import time

EXEC_PATH = ["python", "bot.py"]

subprocess_args = {
    "stderr": subprocess.PIPE,
    "encoding": "utf-8",
    "bufsize": 0,
}

pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)

while True:
    stderr = pipe.stderr.readline().strip()
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
