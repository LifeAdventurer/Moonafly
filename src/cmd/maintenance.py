import bot
import responses
import develop_mode


from cmd import command_help


from datetime import datetime
import textwrap
import re
import json


def set_maintenance(msg: str) -> str:

    # r_time = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')

    if msg[:6] == '--help':
        return command_help.load_help_cmd_info('set')

    try:
        time = datetime.strptime(msg, '%Y-%m-%d %H:%M:%S')

        if time <= datetime.now():
            return textwrap.dedent(f"""
                ```
                the time you entered needs to be later than now
                {develop_mode.current_path()}
                ```
            """)

        with open('../data/txt/init_files/maintenance.txt', 'w') as file:
            file.write('True\n' + str(time) + '\n' + responses.develop_mode_current_using_user)

        bot.load_maintenance()

        return textwrap.dedent(f"""
            ```
            maintenance set up successfully
            {develop_mode.current_path()}
            ```
        """)

    except ValueError:
        return textwrap.dedent(f"""
            ```
            you should follow this format
            YYYY:MM:DD hh:mm:ss
            {develop_mode.current_path()}
            ```
        """)


def end_maintenance(msg: str) -> str:

    with open('../data/txt/init_files/maintenance.txt', 'w') as file:
        file.write('False\n' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' + responses.develop_mode_current_using_user)

    bot.load_maintenance()

    return textwrap.dedent(f"""
        ```
        maintenance ended
        {develop_mode.current_path()}
        ```
    """)