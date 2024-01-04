import responses


import textwrap


def get_response_in_develop_mode(message) -> str:
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
            
            - normal mode
            - terminal mode 
            - develop mode (current)
            ```
        """)