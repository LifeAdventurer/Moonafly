import os
import select
import subprocess

EXEC_PATH = ["python", "bot.py"]

subprocess_args = {
    "stderr": subprocess.PIPE,
    "encoding": "utf-8",
    "bufsize": 0,
}

pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)

# code from https://juejin.cn/s/python%20popen%20communicate%20non%20blocking
while True:
    reads, _, _ = select.select([pipe.stderr], [], [])
    for fd in reads:
        if fd == pipe.stderr:
            stderr = pipe.stderr.readline().strip()
            if "Restarting Moonafly..." in stderr:
                pipe.kill()
                pipe = subprocess.Popen(EXEC_PATH, **subprocess_args)
                break

            elif "Moonafly stopped by command" in stderr:
                print("Moonafly stopped by command")
                os._exit(0)

            if stderr:
                print(stderr)
