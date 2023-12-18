import responses


import json
import random
import requests
import os
import re
import textwrap


Chinese_pattern = re.compile('[\u4e00-\u9fff]')


def get_response_in_normal_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    pattern = r'^!search google (.+)$'
    if Chinese_pattern.search(msg) and not re.match(pattern, msg):
        return ''

    if msg == 'help':
        return textwrap.dedent(f"""\
            ```
            Moonafly {responses.project_version}
            
            - normal mode (default)
            - terminal mode 

            commands to switch mode
              -t        switch to terminal mode, `Moonafly -t`
                        and `moonafly -t` is also fine
              exit      leaving terminal mode
            ```
        """)