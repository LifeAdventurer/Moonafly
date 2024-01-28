import terminal_mode


import textwrap
import re
import requests


def get_online_judge_info(msg: str) -> str:
    # -{number} {handle}
    pattern = r'^-(\d+)\s+(\w+)$'
    match = re.search(pattern, msg)

    if match:
        number = int(match.group(1))
        handle = match.group(2)
        url = ""
        # TODO: make this as a file or at least a list
        if number == 1:
            url = "https://atcoder.jp/users/"
        elif number == 2:
            url = "https://www.codechef.com/users/"
        elif number == 3:
            url = "https://codeforces.com/profile/"
        elif number == 4:
            url = "https://csacademy.com/user/"
        elif number == 5:
            url = "https://dmoj.ca/user/"
        elif number == 6:
            url = "https://leetcode.com/"
        elif number == 7:
            url = "https://profiles.topcoder.com/"
        else:
            return textwrap.dedent(f"""
                ```
                please enter a valid number
                {terminal_mode.current_path()}
                ```
            """)

        url += handle
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

    else:
        return textwrap.dedent(f"""
            ```
            please type the right command format, using help to see what are the available options
            {terminal_mode.current_path()}
            ```
        """)