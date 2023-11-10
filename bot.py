import json
import discord
import responses

token = ""
# bot = discord.Bot()

# Open Token JSON file
def load_token():
  global token
  token_file = open('config.json')
  token = json.load(token_file)['token']
  token_file.close()

async def send_message(message, user_message, is_private):
  try:
    response = responses.get_response(message)
    await message.author.send(response) if is_private else await message.channel.send(response)
  except Exception as e:
    print(e)

def run_discord_bot():
  load_token()
  
  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Client(intents=intents)

  @client.event
  async def on_ready():
    print(f'{client.user} is now running!')

  @client.event
  async def on_message(message):
    if message.author == client.user:
      return
    
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)
  
    if not user_message:
      return
      
    print(f"{username} said: '{user_message}' ({channel})")

    if user_message[0] == '?':
      user_message = user_message[1:]
      await send_message(message, user_message, is_private = True)
    else:
      await send_message(message, user_message, is_private = False)

  client.run(token)