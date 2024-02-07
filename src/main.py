import subprocess
import os


exec_path = ["python", "bot.py"]


pipe = subprocess.Popen(exec_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
while True:
    command = pipe.stdout.read()
    if command.find("Restarting Moonafly...") != -1:
        pipe.kill()
        pipe = subprocess.Popen(exec_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    
    elif command.find("Moonafly stopped by command") != -1:
        print("Moonafly stopped by command")
        os._exit(0)