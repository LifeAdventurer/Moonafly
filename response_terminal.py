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

# generating the current working directory
def current_directory() -> str:
  global path_stack
  path = "Moonafly:"
  for folder in path_stack:
    # don't need this right now because checked before appending to path_stack
    # if not folder:
    #   continue

    # ~ and / don't need a prefix '/'
    if folder != '~' and folder != '/':
      path += '/'
    path += f"{folder}"
  return path + "$"

def get_response_in_terminal_mode(message) -> str:
  username = str(message.author)
  msg = str(message.content)

  global path_stack

  if msg[:2] == 'cd':
    # 
    path = msg[2:].lstrip()
    
    # blank or ~ should go directly to ~
    if not path or path == '~':
      path_stack = ['~']
      print(f"{current_directory()}")
      return f"```{current_directory()}```"
    
    # go to the root directory
    elif path == '/':
      path_stack = ['/']
      print(f"{current_directory()}")
      return f"```{current_directory()}```"

    # if at root directory 
    elif path_stack == ['/']:
      print(textwrap.dedent(f"""\
        permission denied
        {current_directory()}
      """))
      return textwrap.dedent(f"""\
        ```
        permission denied
        {current_directory()}
        ```
      """)

    # skip all the '\' and split the path 
    path = path.replace('\\', '').split('/')
    
    for folder in path:
      # if the folder is empty or . then nothing happens with the 
      if folder == '' or folder == '.':
        continue

      # move up one directory 
      elif folder == '..':
        if len(path_stack) > 1:
          path_stack.pop()
        elif path_stack[0] == '~':
          path_stack[0] = 'home'
        elif path_stack[0] == 'home':
          path_stack[0] = '/'
      
      # make sure the path /home/Moonafly/ is right 
      elif folder == 'home':
        path_stack = ['home']
      elif folder == 'Moonafly':
        if path_stack == ['home']:
          path_stack = ['~']
        else:
          print(folder)
          print(textwrap.dedent(f"""\
            bash: cd: {msg[2:].lstrip()}: No such file or directory
            {current_directory()}
          """))
          return textwrap.dedent(f"""\
            ```
            bash: cd: {msg[2:].lstrip()}: No such file or directory
            {current_directory()}
            ```
          """)
      else:
        path_stack.append(folder)
    print(f"{current_directory()}")
    return f"```{current_directory()}```"

  elif msg[:2] == 'ls':
    print(textwrap.dedent(f"""\
      dict  gen     math
      roll  search  weather
      {current_directory()}
    """))
    return textwrap.dedent(f"""\
      ```
      dict  gen     math
      roll  search  weather
      {current_directory()}
      ```
    """)

  # return the full pathname of the current working directory
  elif msg[:3] == 'pwd':
    # delete the prefix 'Moonafly:' and the suffix '$'
    path = current_directory()[9:-1]
    # delete the prefix no matter it is '~' or '/' path_stack still has the data
    path = path[1:]
    
    if path_stack[0] == '~':
      path = 'home/Moonafly' + path 
    print(textwrap.dedent(f"""\
      /{path}
      {current_directory()}
    """))
    return textwrap.dedent(f"""\
      ```
      /{path}
      {current_directory()}
      ```
    """)
    

  elif msg[:3] == 'gen':
    msg = msg[4:]
    if msg[:2] == 'ls':
      print(textwrap.dedent(f"""\
        fortune vocab
        {current_directory()}
      """))
      return textwrap.dedent(f"""\
        ```
        fortune vocab
        {current_directory()}
        ```
      """)

    elif 'vocabulary' in msg or 'vocab' in msg:
      return "sorry, still developing"
      return list[random.randint(0, len(list))]

    # my generators repo on github.io
    elif msg[:7] == 'fortune':
      return 'https://lifeadventurer.github.io/generators/fortune_generator/index.html' 

    else:
      return 'no such command' 
  
  elif msg[:6] == 'search':
    msg = msg[7:]
    if msg[:2] == 'ls':
      print(textwrap.dedent(f"""\
        git  github  google  oj
        {current_directory()}
      """))
      return textwrap.dedent(f"""\
        ```
        git  github  google  oj
        {current_directory()}
        ```
      """)

    # search for a handle in different online judges
    elif msg[:2] == 'oj':
      msg = msg[3:]
      if msg[:2] == 'ls':
        print(textwrap.dedent(f"""\
          atcoder     -1
          codechef    -2
          codeforces  -3  
          csacademy   -4
          dmoj        -5
          leetcode    -6
          topcoder    -7
          {current_directory()}
        """))
        return textwrap.dedent(f"""\
          ```
          atcoder     -1
          codechef    -2
          codeforces  -3  
          csacademy   -4
          dmoj        -5
          leetcode    -6
          topcoder    -7
          {current_directory()}
          ```
        """)
      
      pattern = r'-(\d+)\s+(\w+)'
      match = re.search(pattern, msg)
      if match:
        number = int(match.group(1))
        handle = match.group(2)
        url = ""
        # TODO: make this as a file or at least a list
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

    # just a google search -> must improve this more
    elif msg[:6] == 'google':
      return "https://www.google.com/search?q=" + msg[7:]

    # search for github repos or profiles -> because url
    elif msg[:6] == 'github':
      msg = msg[7:]
      github_url = "https://github.com/" + msg
      response = requests.get(github_url)
      if response.status_code == 404:
        return f"The url {github_url} is not found (404 Not Found)."
      else:
        return github_url
    
    # search for git commands
    elif msg[:3] == 'git':
      msg = msg[4:]
      if msg[:2] == 'ls':
        print(textwrap.dedent(f"""\
          setup              -1
          init               -2
          stage & snapshot   -3  
          branch & merge     -4
          inspect & compare  -5
          share & update     -6
          {current_directory()}
        """))
        return textwrap.dedent(f"""\
          ```
          setup              -1
          init               -2
          stage & snapshot   -3  
          branch & merge     -4
          inspect & compare  -5
          share & update     -6
          {current_directory()}
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

  # roll a random number
  elif msg[:4] == 'roll':
    msg = msg[5:]
    if not all(char.isdigit() for char in msg):
      return 'please enter a valid number'
    else:
      return random.randint(1, int(msg))

  # return the definition and example of the enter word from a dictionary
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