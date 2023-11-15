import response_public
import response_terminal

is_public_mode = True

def get_response(message) -> str:
  username = str(message.author)
  msg = str(message.content)

  global is_public_mode

  if not is_public_mode and msg == 'moonafly -p':
    is_public_mode = True
    print("swap to public mode")
    return
  elif msg == 'moonafly -t':
    is_public_mode = False
    print("swap to terminal mode")
    return

  else:
    if msg == 'exit' and not is_public_mode:
      is_public_mode = True
      return
    elif msg == 'status':
      if is_public_mode:
        return 'public mode v1.0.0'
      else:
        return 'terminal mode v1.0.1'
    if is_public_mode:
      return response_public.get_response_in_public_mode(message)
    else:
      return response_terminal.get_response_in_terminal_mode(message)