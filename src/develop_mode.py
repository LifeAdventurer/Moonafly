import responses


from cmd.remote import load_remote_file


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

              remote [file]
            ```
        """)

    if msg[:6] == 'remote':
        msg = msg[6:].strip()

        if msg[:6] == '--help':
            return load_help_cmd_info('remote')

        if username not in responses.developers:
            return textwrap.dedent(f"""\
                ```
                permission denied
                * this command can only be used by developers
                {current_path()}
                ```
            """)
        
        return load_remote_file(msg, 'developer', username)