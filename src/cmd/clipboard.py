import terminal_mode 


import textwrap
import json


def load_clipboard_data() -> dict:
    # clipboard_data
    with open('../data/json/clipboard.json', 'r') as file:
        clipboard_data = json.load(file)

    return clipboard_data


def get_clipboard_data(keyword: str) -> str:
    clipboard_data = load_clipboard_data()

    if keyword in clipboard_data:
        if clipboard_data[keyword]['type'] == 'link':
            return textwrap.dedent(f"""
                {clipboard_data[keyword]['data']}
                ```
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