import discord
import json
from datetime import datetime

import responses 
import response_terminal

# token should be encrypted
token = ""

# open token JSON file
def load_token():
    global token
    with open('../config.json') as token_file:
        token = json.load(token_file)['token']

# check whether there is maintenance and the duration
def check_maintenance():
    global in_maintenance, estimated_end_time
    with open('../data/txt/init_files/maintenance.txt') as maintenance_file:
        in_maintenance = maintenance_file.readline().strip() == 'True'
        estimated_end_time = maintenance_file.readline().strip()

async def send_message(message):
    try:
        # get response from `responses.py`
        response = responses.get_response(message)
        if response != None:
            # large output split
            # discord limits each message to a maximum of 2000 characters
            if len(response) > 2000:
                # current message group total word count
                word_count = 0 
                # calculate the count of '\n' it takes 1 space
                line_count = 0 
                response = response.splitlines()
                # the filename bar
                output_prefix = '\n'.join(response[:3])
                await message.channel.send(output_prefix)
                # the current path bar
                output_suffix = '\n'.join(response[-3:])
                # cut the prefix and suffix
                response = response[4:-4]
                lines = []
                for line in response:
                    # prevent backticks breaking the code block 
                    # TODO: find a escape backticks method
                    line = line.replace('```', '` ` `')

                    # 50 is just a free space for avoiding unpredictable error
                    if word_count + len(line) + line_count + 50 > 2000:
                        word_count = len(line)
                        line_count = 1
                        content = '\n'.join(lines)
                        lines = [line]
                        content = f"```{response_terminal.file_language}\n{content}\n```\n"
                        await message.channel.send(content)
                    
                    else:
                        word_count += len(line)
                        line_count += 1
                        lines.append(line)
                # last part of message
                content = '\n'.join(lines)
                content = f"```{response_terminal.file_language}\n{content}\n```\n"
                await message.channel.send(content)
                # the current path bar
                await message.channel.send(output_suffix)

            else:
                await message.channel.send(response)

    except Exception as e:
        print(e)

# send message directly without `responses.py`
async def send_message_without_response(message):
    try:
        await message.channel.send(message.content)
    except Exception as e:
        print(e)

# send message in private
async def send_message_in_private(message):
    try:
        await message.author.send(message.content)
    except Exception as e:
        print(e)

def init_files():
    load_token()
    check_maintenance()
    responses.load_user_identity_list()
    responses.load_password_for_terminal()
    response_terminal.load_directory_structure()
    response_terminal.load_Moonafly_structure()

def run_Moonafly():
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
        
        if username == responses.author:
            if user_message == 'exit --force':
                message.content = 'exit'
                await send_message(message)
                return
            
            elif user_message == 'init --hard':
                init_files()
                message.content = '```init files success```'
                await send_message_without_response(message)
                return
        
        # if in maintenance and user using command
        # announce the maintenance time 
        if (in_maintenance               and
            username != responses.author and 
            len(user_message) > 0        and
           (user_message[0]   == '!'           or
            user_message[:2]  == '-t'          or
            user_message[:11] == 'moonafly -t' or
            user_message[:11] == 'Moonafly -t')):
            
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
            await send_message_without_response(message)
        
        # when someone else wants to use terminal 
        # send private message to notice the user
        if not responses.is_public_mode and username != responses.current_using_user:
            if user_message[:2] == '-t' or user_message[:11] == 'moonafly -t' or user_message[:11] == 'Moonafly -t':
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

    # start discord client
