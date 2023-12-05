import json
import random
import requests
from search_dict import search_dict
from search_weather import get_weather_info
from math_calc import safe_eval
import os
import re

chinese_pattern = re.compile('[\u4e00-\u9fff]')

playing_game = False

def get_response_in_public_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    if '機率' in msg:
        return f"{((random.randint(1, len(msg)) ^ len(msg)) << len(msg)) % 100}%"

    if msg == '笑' or '哈哈' in msg:
        ha_str = '哈' * random.randint(1, 10)
        return f"{ha_str} :rofl:"

    pattern = r'^!search google (.+)$'
    if chinese_pattern.search(msg) and not re.match(pattern, msg):  
        return

    if msg[0] == '!':
        msg = msg[1:]
        if msg[:4] == 'help':
            return "!math\n!gen\n!search\n!dict\n!weather\n!roll\n!greek\n"

        if msg[:4] == 'math':
            msg = msg[5:]
            return safe_eval(msg)

        elif msg[:3] == 'gen':
            msg = msg[4:]
            if msg[:4] == 'help':
                return "fortune\nquote\n"

            elif msg[:7] == 'fortune':
                return 'https://lifeadventurer.github.io/generators/fortune_generator/' 

            elif msg[:5] == 'quote':
                return 'https://lifeadventurer.github.io/generators/quote_generator/'

            else:
                return 'no such command' 

        elif msg[:6] == 'search':
            msg = msg[7:]
            if msg[:4] == 'help':
                return "git\ngithub\ngoogle\noj\nyoutube\n"

            elif msg[:2] == 'oj':
                msg = msg[3:]
                if msg[:4] == 'help':
                    return 'codeforces -1\natcoder -2\ncodechef -3\ntopcoder -4\nleetcode -5\ncsacademy -6\ndmoj  -7\n'

                pattern = r'^-(\d+)\s+(.*?)$'
                match = re.search(pattern, msg)
                if match:
                    number = int(match.group(1))
                    handle = match.group(2)
                    url = ""
                    if number == 1:
                        url = "https://codeforces.com/profile/"
                    elif number == 2:
                        url = "https://atcoder.jp/users/"
                    elif number == 3:
                        url = "https://www.codechef.com/users/"
                    elif number == 4:
                        url = "https://profiles.topcoder.com/"
                    elif number == 5:
                        url = "https://leetcode.com/"
                    elif number == 6:
                        url = "https://csacademy.com/user/"
                    elif number == 7:
                        url = "https://dmoj.ca/user/"
                    else:
                        return 'please enter a valid number'

                    url += handle
                    response = requests.get(url)
                    if response.status_code == 404:
                        return f"The handle {handle} is not found"
                    else:
                        return url

                else:
                    return 'please type the right command format, using help to see what are the available options'


            elif msg[:6] == 'google':
                return "https://www.google.com/search?q=" + msg[7:].replace(' ', '+')

            elif msg[:7] == 'youtube':
                return "https://www.youtube.com/results?search_query=" + msg[8:]

            elif msg[:6] == 'github':
                msg = msg[7:]
                github_url = "https://github.com/" + msg
                response = requests.get(github_url)
                if response.status_code == 404:
                    return f"The url {github_url} is not found (404 Not Found)."
                else:
                    return github_url

            elif msg[:3] == 'git':
                msg = msg[4:]
                if msg[:4] == 'help':
                    return "setup -1\ninit -2\nstage & snapshot -3\nbranch & merge -4\ninspect & compare  -5\nshare & update -6\n"

                msg = msg[1:]
                if msg > '6' or msg < '1':
                    return 'no such command'

                else:
                    return 'sorry, this function is still developing'
                # TO-DO
                # elif msg == 'setup':

            else:
                return 'no such command'

        elif msg[:5] == 'greek':
            return 'Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω\nα β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω\n'

        elif msg[:7] == 'weather':
            return get_weather_info(0, 0);

        elif msg[:4] == 'roll':
            msg = msg[5:]
            if not all(char.isdigit() for char in msg):
                return 'please enter a valid number'
            else:
                return random.randint(1, int(msg))

        elif msg[:4] == 'dict':
            msg = msg[5:]

            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return search_dict(match.group(1), int(match.group(2), 0, 0))
            elif 'LIMIT' in msg:
                return 'please type a number after the command LIMIT'
            else:
                return search_dict(msg, 3, 0, 0)

        elif msg[:5] == 'count':
            msg = msg[6:]
            words = msg.split()
            return str(len(words))

        elif msg[:4] == 'game':
            msg = msg[5:]
            if msg[:4] == '1A2B':
                return 'For your better experience, this game can only be played in terminal mode.'
            else:
                return 'no such command'

        else:
            return 'no such command' 