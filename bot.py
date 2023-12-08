import discord
import responses 
import response_terminal
import json
from datetime import datetime

# token should be encrypted
token = ""

# open token JSON file
def load_token():
    global token
    with open('./config.json') as token_file:
        token = json.load(token_file)['token']

# check whether there is maintenance and the duration
def check_maintenance():
    global in_maintenance, estimated_end_time
    with open('./data/txt/init_files/maintenance.txt') as maintenance_file:
        in_maintenance = maintenance_file.readline().strip() == 'True'
        estimated_end_time = maintenance_file.readline().strip()

async def send_message(message):
    try:
        # get response from `responses.py`
        response = responses.get_response(message)
        if response != None:
            await message.channel.send(response)
    except Exception as e:
        print(e)

# send message directly without `responses.py`
async def send_message_direct(message):
    try:
        await message.channel.send(message.content)
    except Exception as e:
        print(e)

async def send_message_in_private(message):
    try:
        await message.author.send(message.content)
    except Exception as e:
        print(e)

def init_files():
    load_token()
    check_maintenance()
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
        
        if username == responses.author and user_message == 'exit --force':
            message.content = 'exit'
            print(message.content)
            await send_message(message)
            return
        
        # if in maintenance and user using command
        # announce the maintenance time 
        if in_maintenance and username != responses.author and (user_message[0] == '!' or user_message[:2] == '-t' or user_message[:11] == 'Moonafly -t' or user_message[:11] == 'moonafly -t'):
            current_time = datetime.now()
            end_time = datetime.strptime(estimated_end_time, '%Y-%m-%d %H:%M:%S')

            seconds = int((end_time - current_time).total_seconds())
            announce = ''
            if seconds > 0:
                # get remaining maintenance time 
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                # days, hours = divmod(hours, 24)
                announce = f"Maintenance is over in {hours}h {minutes}m {seconds}s" 

            else:
                announce = 'Still under maintenance'

            message.content = announce
            await send_message_direct(message)

        
        # when someone else wants to use terminal 
        # send private message to notice the user
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