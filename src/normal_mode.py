import re
import textwrap

import responses
from command import apply


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
              -t        switch to terminal mode, `Moonafly -t` and
                        `moonafly -t` is also fine
              -d        switch to develop mode, `Moonafly -d` and
                        `moonafly -d` is also fine
              --ic      use after `-t` or `-d` to lower first character
                        of your command `--ignore-capitalization` is
                        also fine
              apply     apply for roles to use terminal mode or develop
                        mode
              status    show using mode and server battery percentage
            ```
            """
        )

    if msg.startswith('apply'):
        msg = msg[6:].strip()

        return apply.apply_for_role(msg, username)
