import terminal_mode


import textwrap
import re
import requests


urls = {
    "atcoder": "https://atcoder.jp/users/",
    "codechef": "https://www.codechef.com/users/",
    "codeforces": "https://codeforces.com/profile/",
    "csacademy": "https://csacademy.com/user/",
    "dmoj": "https://dmoj.ca/user/",
    "leetcode": "https://leetcode.com/",
    "topcoder": "https://profiles.topcoder.com/"
}


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
    # -{number} {handle}
    pattern = r'^-(\d+)\s+(\w+)$'
    match = re.search(pattern, msg)

    if match:
        number = int(match.group(1))
        handle = match.group(2)
        return get_profile_from_online_judge(number, handle)
    else:
        return textwrap.dedent(f"""
            ```
            please type the right command format, using help to see what are the available options
            {terminal_mode.current_path()}
            ```
        """)