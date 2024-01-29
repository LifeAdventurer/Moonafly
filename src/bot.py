import responses
import terminal_mode
import develop_mode
import split_message


import discord
import json
from datetime import datetime
import textwrap


# constants
TAB_SIZE = 4


# token should be encrypted
token = ""


# open token JSON file
def load_token():
    global token
    with open('../config.json') as file:
        token = json.load(file)['token']


# check whether there is maintenance and the duration
def load_maintenance():
    global in_maintenance, estimated_end_time, developer
    try:
        with open('../data/txt/init_files/maintenance.txt') as file:
            in_maintenance = file.readline().strip() == 'True'
            estimated_end_time = file.readline().strip()
            developer = file.readline().strip()
    except FileNotFoundError:
        in_maintenance = 'False'
        estimated_end_time = '1970-01-01 00:00:00'
        developer = 'Moonafly'
        with open('../data/txt/init_files/maintenance.txt', 'w') as file:
            file.write('\n'.join([in_maintenance, estimated_end_time, developer]))

async def send_message(message):
    try:
        # get response from `responses.py`
        response = responses.get_response(message)
        if response != None and len(response) > 0:
            # large output split
            # discord limits each message to a maximum of 2000 characters
            if len(response) > 2000:
                split_response = split_message.split_message(response)
                for item in split_response:
                    await message.channel.send(item)

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
    load_maintenance()
    
    responses.load_user_identity_list()
    
    terminal_mode.load_terminal_mode_directory_structure()
    terminal_mode.load_Moonafly_structure()

    develop_mode.load_develop_mode_directory_structure()
    develop_mode.load_Moonafly_structure()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def stop_Moonafly():
    await client.close()


def run_Moonafly():
    init_files()

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
        
        # commands only author can trigger
        if username == responses.author:
            if user_message == 'Moonafly --stop':
                print('Moonafly stopped by command')
                await stop_Moonafly()
                return
            
            elif user_message == 'exit --force':
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
        if (
            in_maintenance
            and username != responses.author
            and username != developer
            and len(user_message) > 0
            and (
                any(user_message.startswith(cmd) for cmd in responses.enter_terminal_mode_cmd)
                or any(user_message.startswith(cmd) for cmd in responses.enter_develop_mode_cmd)
            )
        ):
            
            current_time = datetime.now()
            end_time = datetime.strptime(estimated_end_time, '%Y-%m-%d %H:%M:%S')

            seconds = int((end_time - current_time).total_seconds())
            announce = ''
            if seconds > 0:
                # get remaining maintenance time
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                # days, hours = divmod(hours, 24)
                announce = f"```Developer {developer} is still developing and maintaining Moonafly! It will end in {hours}h {minutes}m {seconds}s```"

            else:
                announce = f"```Developer {developer} is still developing and maintaining Moonafly!```"

            message.content = announce
            await send_message_without_response(message)

        # when someone else wants to use terminal
        # send private message to notice the user
        if responses.is_terminal_mode and username != responses.terminal_mode_current_using_user:
            if any(user_message.startswith(cmd) for cmd in responses.enter_terminal_mode_cmd):
                if username == responses.author:
                    message.content = f"```{responses.terminal_mode_current_using_user} is using the terminal```"
                else:
                    message.content = '```someone is using the terminal```'
                await send_message_in_private(message)
            return
        
        if responses.is_develop_mode and username != responses.develop_mode_current_using_user:
            if any(user_message.startswith(cmd) for cmd in responses.enter_develop_mode_cmd):
                if username == responses.author:
                    message.content = f"```{responses.develop_mode_current_using_user} is using develop mode```"
                else:
                    message.content = '```someone is using develop mode```'
                await send_message_in_private(message)
            return

        if channel[:14] == 'Direct Message' and username != responses.author:
            print(f"WARNING: {username} using bot in Direct Message\n")

        # avoid endless loops
        if not user_message:
            return

        # uncomment this line only for debug
        # print(f"user: {username} \nmessage: '{user_message}'\nchannel: {channel}")

        await send_message(message)

    # start discord client
    client.run(token)