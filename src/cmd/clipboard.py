import terminal_mode 


from cmd.command_help import load_help_cmd_info


import textwrap
import json
import re


def load_clipboard_data() -> dict:
    # clipboard_data
    with open('../data/json/clipboard.json', 'r', encoding='utf-8') as file:
        clipboard_data = json.load(file)

    return clipboard_data


def save_clipboard_data(clipboard_data):
    with open('../data/json/clipboard.json', 'w', encoding='utf-8') as file:
        json.dump(clipboard_data, file, indent=4)


def get_clipboard_data(keyword: str) -> str:
    clipboard_data = load_clipboard_data()

    if keyword in clipboard_data:
        data_type = clipboard_data[keyword]['type']
        
        if data_type == 'link':
            return textwrap.dedent(f"""
                {clipboard_data[keyword]['data']}
                ```
                {terminal_mode.current_path()}
                ```
            """)
        elif data_type == 'text':
            content = ('\n' + ' ' * 4 * 4).join(clipboard_data[keyword]['data'].splitlines())
            return textwrap.dedent(f"""
                ```
                {content}
                {terminal_mode.current_path()}
                ```
            """)

    else:
        return textwrap.dedent(f"""
            ```
            clipboard: no such keyword '{keyword}'
            {terminal_mode.current_path()}
            ```
        """)


data_types = ['link', 'text']

checking_clipboard_keyword_override = False
temp_keyword = ''
temp_data_type = ''
temp_data = ''

def save_data_to_clipboard(msg: str) -> str:
    lines = msg.splitlines()

    global checking_clipboard_keyword_override
    global temp_keyword, temp_data_type, temp_data

    if checking_clipboard_keyword_override == True:
        if msg.lower() == 'yes' or msg.lower() == 'y':
            checking_clipboard_keyword_override = False

            clipboard = load_clipboard_data()

            clipboard[temp_keyword] = {
                "data": temp_data,
                "type": data_type
            }

            return textwrap.dedent(f"""
                ```
                Keyword: {temp_keyword} overrode successfully
                {terminal_mode.current_path()}
                ```
            """)
        elif msg.lower() == 'no' or msg.lower() == 'n':
            checking_clipboard_keyword_override = False

            return textwrap.dedent(f"""
                ```
                if you still want to save your data, change your keyword and try again
                {terminal_mode.current_path()}
                ```
            """)
        
        else: 
            # do you want to override the original data by {keyword}? 
            
            return textwrap.dedent(f"""
                ```
                please type yes/no (y/n)
                {terminal_mode.current_path()}
                ```
            """)

    pattern = r'^(\w+)\s+(\w+)$'

    match = re.match(pattern, lines[0].strip())
    
    if match:
        data_type = match.group(1)
        keyword = match.group(2)
        lines.pop(0)
        data = '\n'.join(lines)
        
        if data_type in data_types:

            if len(data) > 0:
                clipboard_data = load_clipboard_data()
                if keyword in clipboard_data:
                    
                    checking_clipboard_keyword_override = True
                    temp_keyword = keyword
                    temp_data_type = data_type
                    temp_data = data

                    return textwrap.dedent(f"""
                        ```
                        keyword already in use, do you want to override it? (y/n)
                        {terminal_mode.current_path()}
                        ```
                    """)
                else:
                    clipboard_data[keyword] = {
                        "data": data,
                        "type": data_type
                    }

                save_clipboard_data(clipboard_data)

                return textwrap.dedent(f"""
                    ```
                    Saved successfully
                    {terminal_mode.current_path()}
                    ```
                """)

            else:
                return textwrap.dedent(f"""
                    ```
                    clipboard: save: data is empty
                    {terminal_mode.current_path()}
                    ```
                """)

        else:
            content = ('\n' + ' ' * 4 * 4).join(data_types)
            return textwrap.dedent(f"""
                ```
                clipboard: save: no such data type
                {content}
                {terminal_mode.current_path()}
                ```
            """)

    else:
        return textwrap.dedent(f"""
            ```
            clipboard: save: incorrect format
            follow the format below

            save [type] [keyword]
            [data]

            *data can have multiple lines
            {terminal_mode.current_path()}
            ```
        """)


def get_clipboard_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global checking_clipboard_keyword_override

    if msg[:6] == '--help':
        return load_help_cmd_info('clipboard')

    if checking_clipboard_keyword_override == True:
        return save_data_to_clipboard(msg)

    if msg[:3] == 'get':
        msg = msg[3:].strip()
        if msg[:6] == '--help':
            return load_help_cmd_info('clipboard_get')

        return get_clipboard_data(msg)

    elif msg[:4] == 'save':
        msg = msg[4:].strip()
        if msg[:6] == '--help':
            return load_help_cmd_info('clipboard_save')

        return save_data_to_clipboard(msg)

    else: 
        return terminal_mode.command_not_found(msg)