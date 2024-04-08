import json
import os
import random
import re
import textwrap

import requests

import responses
from command import apply

Chinese_pattern = re.compile('[\u4e00-\u9fff]')


def get_response_in_normal_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    if msg == 'help':
        return textwrap.dedent(
            f"""
            ```
            Moonafly {responses.Moonafly_version}
            
            - normal mode (default) (current)
            - terminal mode 
            - develop mode

            commands to switch mode
              -t        switch to terminal mode, `Moonafly -t` and `moonafly -t` is also fine
              -d        switch to develop mode, `Moonafly -d` and `moonafly -d` is also fine
              --ic      use it after `-t` or `-d` to lower first character of your command
                        `--ignore-capitalization` is also fine
              exit      leaving current mode and switch to normal mode
              status    show in which mode and the server battery percentage
              apply     apply for roles to use terminal mode and develop mode
            ```
            """
        )

    if msg.startswith('apply'):
        msg = msg[6:].strip()

        return apply.apply_for_role(msg, username)
