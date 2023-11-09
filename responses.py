def get_response(message) -> str:
  username = str(message.author)
  user_message = str(message.content)
  msg = user_message.lower()

  if username == 'tobiichi3227':
    return '那麼好'
  
  if '睡覺' in msg:
    return f'{username} 晚安 祝好夢'

  if msg == 'hello':
    return 'hello'
  
  if '好' in msg:
    return '那麼好'
  
  if msg == '笑死':
    return '哇哈哈哈哈真的是笑死我了'