import discord
import responses 
import response_terminal
import json

token = ""

# open token JSON file
def load_token():
    global token
    with open('./config.json') as token_file:
        token = json.load(token_file)['token']

async def send_message(message):
    try:
        # get response from responses.py
        response = responses.get_response(message)
        if response != None:
            await message.channel.send(response)
    except Exception as e:
        print(e)

async def send_message_in_private(message):
    try:
        await message.author.send(message.content)
    except Exception as e:
        print(e)

def init_files():
    load_token()
    responses.special_guest_list()
    responses.load_password_for_terminal()
    response_terminal.get_directory_structure()

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
        
        if username == responses.special_guests[0] and user_message == 'exit --force':
            message.content = 'exit'
            print(message.content)
            await send_message(message)
            return
        
        if not responses.is_public_mode and username != responses.current_using_user:
            if user_message[:2] == '-t' or user_message[:11] == 'Moonafly -t' or user_message[:11] == 'moonafly -t':
                message.content = 'someone is using the terminal'
                await send_message_in_private(message)
            return
        
        
        if channel[:14] == 'Direct Message':
            print('WARNING: people using bot in Direct Message\n')

        # avoid endless loops
        if not user_message:
            return

        # uncomment this line only for debug
        # print(f"user: {username} \nmessage: '{user_message}'\nchannel: {channel}")

        await send_message(message)

    client.run(token)