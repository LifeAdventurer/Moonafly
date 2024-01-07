import terminal_mode 


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


def save_data_to_clipboard(msg: str) -> str:
    lines = msg.splitlines()

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

    if msg[:3] == 'get':
        msg = msg[3:].strip()
        return get_clipboard_data(msg)

    elif msg[:4] == 'save':
        msg = msg[4:].strip()
        return save_data_to_clipboard(msg)

    else: 
        return terminal_mode.command_not_found(msg)