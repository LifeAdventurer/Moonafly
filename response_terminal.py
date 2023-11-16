from math import *
import json
import random
import requests
from search_dict import search_dict
import os
import re
import textwrap

vocab_file = open('vocabulary_items.json')
list = json.load(vocab_file)['vocabularies']
vocab_file.close()

path_stack = []

def current_directory() -> str:
  global path_stack
  path = "Moonafly:"
  for folder in path_stack:
    if folder != '~':
      path += '\\'
    path += f"{folder}"
  return path + "$"

def get_response_in_terminal_mode(message) -> str:
  username = str(message.author)
  msg = str(message.content)

  global path_stack

  if msg[:2] == 'cd':
    path_to_directory = msg[2:].lstrip()
    if not path_to_directory:
      path_stack = ['~']
      return f"```{current_directory()}```"
    
    elif path_to_directory == '.':
      return f"```{current_directory()}```"

    path_to_directory = path_to_directory.replace('\\', '').split('/')
    for folder in path_to_directory:
      if folder == '.':
        continue
      elif folder == '..':
        path_stack.pop()
      else:
        path_stack.append(folder)
    return f"```{current_directory()}```"

  if msg[:2] == 'ls':
    return textwrap.dedent(f"""\
      ```
      dict  gen     math
      roll  search  weather
      {current_directory}
      ```
    """)

  if msg[:3] == 'gen':
    msg = msg[4:]
    if msg[:2] == 'ls':
      return textwrap.dedent(f"""\
        ```
        fortune vocab
        {current_directory}
        ```
      """)
    elif 'vocabulary' in msg or 'vocab' in msg:
      return "sorry, still developing"
      return list[random.randint(0, len(list))]
    elif msg[:7] == 'fortune':
      return 'https://lifeadventurer.github.io/generators/fortune_generator/index.html' 
    else:
      return 'no such command' 
  
  elif msg[:6] == 'search':
    msg = msg[7:]
    if msg[:2] == 'ls':
      return textwrap.dedent(f"""\
        ```
        git github google oj
        {current_directory}
        ```
      """)
      return "git   github   google   oj"

    elif msg[:2] == 'oj':
      msg = msg[3:]
      if msg[:2] == 'ls':
        return textwrap.dedent(f"""\
          ```
          atcoder     -1
          codechef    -2
          codeforces  -3  
          csacademy   -4
          dmoj        -5
          leetcode    -6
          topcoder    -7
          {current_directory}
          ```
        """)
      
      pattern = r'-(\d+)\s+(\w+)'
      match = re.search(pattern, msg)
      if match:
        number = int(match.group(1))
        handle = match.group(2)
        url = ""
        if number == 1:
          url = "https://atcoder.jp/users/"
        elif number == 2:
          url = "https://www.codechef.com/users/"
        elif number == 3:
          url = "https://codeforces.com/profile/"
        elif number == 4:
          url = "https://csacademy.com/user/"
        elif number == 5:
          url = "https://dmoj.ca/user/"
        elif number == 6:
          url = "https://leetcode.com/"
        elif number == 7:
          url = "https://profiles.topcoder.com/"
        else:
          return 'please enter a valid number'

        url += handle
        response = requests.get(url)
        if response.status_code == 404:
          return f"The handle {handle} is not found"
        else:
          return url
      
      else:
        return 'please type the right command format, using help to see what are the available options'

    elif msg[:6] == 'google':
      return "https://www.google.com/search?q=" + msg[7:]

    elif msg[:6] == 'github':
      msg = msg[7:]
      github_url = "https://github.com/" + msg
      response = requests.get(github_url)
      if response.status_code == 404:
        return f"The url {github_url} is not found (404 Not Found)."
      else:
        return github_url
        
    elif msg[:3] == 'git':
      msg = msg[4:]
      if msg[:2] == 'ls':
        return textwrap.dedent(f"""\
          ```
          setup              -1
          init               -2
          stage & snapshot   -3  
          branch & merge     -4
          inspect & compare  -5
          share & update     -6
          {current_directory}
          ```
        """)
      
      # pattern = r'-(\d+)\s+(\w+)'
      # match = re.search(pattern, msg)
      # if match:
      #   number = int(match.group(1))
      #   command = match.group(2)

      msg = msg[1:]
      if msg > '6' or msg < '1':
        return 'no such command'
      else:
        return 'sorry, this function is still developing'
      # TO-DO
      # elif msg == 'setup':
    else:
      return 'no such command'
  
  elif msg[:7] == 'weather':
    return 'sorry, still developing'

  elif msg[:4] == 'roll':
    msg = msg[5:]
    if not all(char.isdigit() for char in msg):
      return 'please enter a valid number'
    else:
      return random.randint(1, int(msg))

  elif msg[:4] == 'dict':
    msg = msg[5:]
    match = re.search(r'(\w+)\s+LIMIT\s+(\d+)', msg)
    if match:
      return search_dict(match.group(1), int(match.group(2)))
    elif 'LIMIT' in msg:
      return 'please type a number after the command LIMIT'
    else:
      return search_dict(msg, 3)

  else:
    return 'no such command'