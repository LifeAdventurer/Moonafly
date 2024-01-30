import terminal_mode


from command import command_help


import textwrap
import re
import requests


# constants
TAB_SIZE = 4
HELP_FLAG = '--help'

urls = {
    "atcoder": "https://atcoder.jp/users/",
    "codechef": "https://www.codechef.com/users/",
    "codeforces": "https://codeforces.com/profile/",
    "csacademy": "https://csacademy.com/user/",
    "dmoj": "https://dmoj.ca/user/",
    "leetcode": "https://leetcode.com/",
    "topcoder": "https://profiles.topcoder.com/"
}


def show_online_judge_list() -> str:
    
    # max_oj_len = max(len(key) for key in urls)

    online_judge_list = []

    for index, key in enumerate(urls):
        online_judge_list.append(f"{key}{' ' * (20 - len(key) - len(str(index + 1)) - 1)}-{str(index + 1)}")

    space = ('\n' + ' ' * TAB_SIZE * 2)
    return textwrap.dedent(f"""
        ```
        {space.join(online_judge_list)}
        {terminal_mode.current_path()}
        ```
    """)


def get_profile_from_online_judge(number: int, handle: str) -> str:
    if not 1 <= number <= len(urls):
        return textwrap.dedent(f"""
            ```
            please enter a valid number between 1 and {len(urls)}
            {terminal_mode.current_path()}
            ```
        """)
    
    for index, (key, value) in enumerate(urls.items()):
        if index == number - 1:
            oj_url = value
            break

    url = oj_url + handle
    response = requests.get(url) 
    if response.status_code == 404:
        return textwrap.dedent(f"""
            ```
            The handle {handle} is not found
            {terminal_mode.current_path()}
            ```
        """)
    else:
        return textwrap.dedent(f"""
            <{url}>
            ```
            {terminal_mode.current_path()}
            ```
        """)


def get_online_judge_info(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('online_judge')
    
    if msg[:4] == 'show':
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('online_judge_show')

        return show_online_judge_list()

    # -{number} {handle}
    pattern = r'^-(\d+)\s+(\w+)$'
    match = re.search(pattern, msg)

    if match:
        number = int(match.group(1))
        handle = match.group(2)
        return get_profile_from_online_judge(number, handle)
    else:
        return command_help.load_help_cmd_info('online_judge_handle')