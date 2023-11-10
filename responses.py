from math import *
import random

list = ['underprivileged', 'predominate']

def get_response(message) -> str:
  username = str(message.author)
  user_message = str(message.content)
  msg = user_message.lower()

  if msg[0] == '!':
    msg = msg[1:]
    if msg[:4] == 'math':
      msg = msg[4:]
      return eval(msg)

    if msg[:3] == 'gen':
      msg = msg[3:]
      if 'vocabulary' in msg or 'vocab' in msg:
        return list[random.randint(0, len(list))]
    
  
  if '睡覺' in msg:
    return f'{username} 晚安 祝好夢'

  if '機率' in msg:
    return f'{random.randint(1, 100)}%'

  if msg == 'hello':
    return 'hello'
  
  if '好' in msg:
    return '那麼好'
  
  if msg == '笑死':
    return '哇哈哈哈哈真的是笑死我了'

  if 'wtf' in msg:
    return f'{username} stop saying wtf :rage:'