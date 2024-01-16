import responses


from cmd import apply


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

    if msg == 'help':
        return textwrap.dedent(f"""\
            ```
            Moonafly {responses.Moonafly_version}
            
            - normal mode (default) (current)
            - terminal mode 
            - develop mode

            commands to switch mode
              -t        switch to terminal mode, `Moonafly -t`
                        and `moonafly -t` is also fine
              -d        switch to develop mode, `Moonafly -d`
                        and `moonafly -d` is also fine
              exit      leaving current mode and switch to normal
                        mode
              status    show in which mode and the server battery
                        percentage
            ```
        """)
    
    if msg[:5] == 'apply':
        msg = msg[6:].strip()

        return apply.apply_for_role(msg, username)
