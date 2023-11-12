from math import *
import json
import random
import requests
from search_dict import search_dict
import os
import re

vocab_file = open('vocabulary_items.json')
list = json.load(vocab_file)['vocabularies']
vocab_file.close()

def get_response(message) -> str:
  username = str(message.author)
  msg = str(message.content)

  if msg[0] == '!':
    msg = msg[1:]
    if msg[:4] == 'help':
      return "!math\n!gen\n!search\n!dict\n!weather\n"

    if msg[:4] == 'math':
      msg = msg[5:]
      return '此功能暫時關閉'

    elif msg[:3] == 'gen':
      msg = msg[4:]
      if msg[:4] == 'help':
        return "vocabulary or (vocab) instead\nfortune"

      elif 'vocabulary' in msg or 'vocab' in msg:
        return "still developing"
        return list[random.randint(0, len(list))]

      elif msg[:7] == 'fortune':
        return 'https://lifeadventurer.github.io/generators/fortune_generator/index.html' 

      else:
        return 'no such command' 
    
    elif msg[:6] == 'search':
      msg = msg[7:]
      if msg[:4] == 'help':
        return "git\ngithub"

      

      elif msg[:6] == 'github':
        msg = msg[15:]
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
          return 'sorry this function is still developing'
        # TO-DO
        # elif msg == 'setup':

      elif msg[:7] == 'weather':
        return 'still developing'

      else:
        return 'no such command'

    elif msg[:4] == 'dict':
      msg = msg[5:]

      match = re.search(r'(\w+)\s+LIMIT\s+(\d+)', msg)
      if match:
        return search_dict(match.group(1), int(match.group(2)))
      elif 'LIMIT' in msg:
        return 'please type a number after the command LIMIT'
      else:
        return search_dict(msg, 100)

    else:
      return 'no such command' 
  
  if '睡覺' in msg:
    return f"{username} 晚安 祝好夢"

  if '晚安' in msg:
    return msg

  if '機率' in msg:
    return f"{((random.randint(1, len(msg)) ^ len(msg)) << len(msg)) % 100}%"

  if '危險' in msg:
    return '發生危險了嗎 需要幫您撥打119嗎'

  if '好' in msg:
    words = ['不好', '好痛', '好難', '好苦', '', '',]
    for word in words:
      if word in msg:
        return;    
    if username == 'tobiichi3227':
      return '那麼好'
  
  if msg == '笑死' or '哈哈' in msg:
    ha_str = '哈' * random.randint(1, 10)
    return f"{ha_str} :rofl:"

  if 'wtf' in msg:
    return f"{username} stop saying wtf :rage:"