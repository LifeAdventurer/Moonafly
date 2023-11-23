import discord
import responses
import json

token = ""

# open token JSON file
def load_token():
  global token
  with open('./json/config.json') as token_file:
    token = json.load(token_file)['token']

async def send_message(message, user_message):
  try:
    # get response from responses.py
    response = responses.get_response(message)
    await message.channel.send(response)
  except Exception as e:
    print(e)

def init_files():
  load_token()
  responses.special_guest_list()
  responses.load_password_for_terminal()

def run_discord_bot():
  init_files()
  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Client(intents=intents)

  @client.event
  async def on_ready():
    print(f'Moonafly is now running!')

  @client.event
  async def on_message(message):
    if message.author == client.user:
      return
    
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    # avoid endless loops
    if not user_message:
      return
    
    # uncomment this line only for debug
    # print(f"user: {username} \nmessage: '{user_message}'\nchannel: {channel}")

    await send_message(message, user_message)

  client.run(token)