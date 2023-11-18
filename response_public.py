from math import *
import json
import random
import requests
import search_dict
import os
import re

vocab_file = open('vocabulary_items.json')
list = json.load(vocab_file)['vocabularies']
vocab_file.close()

chinese_pattern = re.compile('[\u4e00-\u9fff]')

def get_response_in_public_mode(message) -> str:
  username = str(message.author)
  msg = str(message.content)

  if '機率' in msg:
    return f"{((random.randint(1, len(msg)) ^ len(msg)) << len(msg)) % 100}%"
  
  if msg == '笑' or '哈哈' in msg:
    ha_str = '哈' * random.randint(1, 10)
    return f"{ha_str} :rofl:"

  match = chinese_pattern.search(msg)
  if match:
    return

  if msg[0] == '!':
    msg = msg[1:]
    if msg[:4] == 'help':
      return "!math\n!gen\n!search\n!dict\n!weather\n!roll\n"

    if msg[:4] == 'math':
      msg = msg[5:]
      return 'sorry, this command is now closed'

    elif msg[:3] == 'gen':
      msg = msg[4:]
      if msg[:4] == 'help':
        return "vocabulary or (vocab) instead\nfortune"

      elif 'vocabulary' in msg or 'vocab' in msg:
        return "sorry, still developing"
        return list[random.randint(0, len(list))]

      elif msg[:7] == 'fortune':
        return 'https://lifeadventurer.github.io/generators/fortune_generator/index.html' 

      else:
        return 'no such command' 
    
    elif msg[:6] == 'search':
      msg = msg[7:]
      if msg[:4] == 'help':
        return "git\ngithub\ngoogle\noj\nyoutube"

      elif msg[:2] == 'oj':
        msg = msg[3:]
        if msg[:4] == 'help':
          return 'codeforces -1\natcoder -2\ncodechef -3\ntopcoder -4\nleetcode -5\ncsacademy -6\ndmoj -7\n'
        
        pattern = r'-(\d+)\s+(\w+)'
        match = re.search(pattern, msg)
        if match:
          number = int(match.group(1))
          handle = match.group(2)
          url = ""
          if number == 1:
            url = "https://codeforces.com/profile/"
          elif number == 2:
            url = "https://atcoder.jp/users/"
          elif number == 3:
            url = "https://www.codechef.com/users/"
          elif number == 4:
            url = "https://profiles.topcoder.com/"
          elif number == 5:
            url = "https://leetcode.com/"
          elif number == 6:
            url = "https://csacademy.com/user/"
          elif number == 7:
            url = "https://dmoj.ca/user/"
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

      elif msg[:7] == 'youtube':
        return "https://www.youtube.com/results?search_query=" + msg[8:]

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
        if msg[:4] == 'help':
          return "setup -1\ninit -2\nstage & snapshot -3\nbranch & merge -4\ninspect & compare -5\nshare & update -6\n"
        
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
        return search_dict.search_dict(match.group(1), int(match.group(2)))
      elif 'LIMIT' in msg:
        return 'please type a number after the command LIMIT'
      else:
        return search_dict.search_dict(msg, 3)

    else:
      return 'no such command' 