import subprocess
import os


EXEC_PATH = ["python", "bot.py"]

subprocess_args = {
    "stdin": subprocess.PIPE,
    "stdout": subprocess.PIPE,
    "stderr": subprocess.PIPE,
    "encoding": "utf-8",
}

pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)

prev_stderr = ""

while True:
    stdout, stderr = pipe.communicate()

    if "Restarting Moonafly..." in stdout:
        pipe.kill()
        pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)

    elif "Moonafly stopped by command" in stdout:
        print("Moonafly stopped by command")
        os._exit(0)

    if stdout:
        print(stdout)

    if stderr and stderr != prev_stderr:
        print(stderr)
        prev_stderr = stderr
