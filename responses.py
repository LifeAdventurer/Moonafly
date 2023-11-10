from math import *
import random
import requests

list = ['underprivileged', 'predominate']

def get_response(message) -> str:
  username = str(message.author)
  user_message = str(message.content)
  msg = user_message.lower()

  if msg[0] == '!':
    msg = msg[1:]
    if msg[:4] == 'help':
      return 
      """
      !math\n
      !gen\n
      !search
      """

    if msg[:4] == 'math':
      msg = msg[5:]
      if username == 'life_adventurer':
        return eval(msg)

      if 'shutdown' in msg or 'dir' in msg or 'c:\\' in msg:
        return f'{username} 別搞事情阿 老哥'

      elif 'os' in msg or 'local' in msg or 'global' in msg:
        return f'{username} 想做什麼 別把我當 CTF 靶機'

      return eval(msg)

    elif msg[:3] == 'gen':
      msg = msg[4:]
      if msg[:4] == 'help':
        return 
        """
        vocabulary or (vocab) in instead\n
        fortune
        """

      elif 'vocabulary' in msg or 'vocab' in msg:
        return list[random.randint(0, len(list))]

      elif msg[:7] == 'fortune':
        return 'https://lifeadventurer.github.io/generators/fortune_generator/index.html' 

      else:
        return 'no such command' 
    
    elif msg[:6] == 'search':
      msg = msg[7:]
      if msg[:6] == 'github':
        msg = user_message[15:]
        github_url = "https://github.com/" + msg
        response = requests.get(github_url)
        if response.status_code == 404:
          return f'The url {github_url} is not found (404 Not Found).'
        else:
          return github_url
      
      else:
        return 'no such command'

    else:
      return 'no such command' 
  
  if '睡覺' in msg:
    return f'{username} 晚安 祝好夢'

  if '機率' in msg:
    return f'{random.randint(1, 100)}%'

  if '危險' in msg:
    return f'發生危險了嗎 需要幫您撥打119嗎'

  if '好' in msg and '不好' not in msg:
    return '那麼好'
  
  if msg == '笑死' or '哈哈' in msg:
    ha_str = '哈' * random.randint(1, 10)
    return f'{ha_str} :rofl:'

  if 'wtf' in msg:
    return f'{username} stop saying wtf :rage:'