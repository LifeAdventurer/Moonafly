import textwrap
from datetime import datetime

import bot
import develop_mode
import responses
from command import command_help
from constants import HELP_FLAG


def set_maintenance(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('set')

    try:
        time = datetime.strptime(msg, '%Y-%m-%d %H:%M:%S')

        if time <= datetime.now():
            return textwrap.dedent(
                f"""
                ```
                the time you entered needs to be later than now
                {develop_mode.current_path()}
                ```
                """
            )

        with open('../data/txt/init_files/maintenance.txt', 'w') as file:
            file.write(
                'True\n'
                + str(time)
                + '\n'
                + responses.develop_mode_current_using_user
            )

        bot.load_maintenance()

        return textwrap.dedent(
            f"""
            ```
            maintenance set up successfully
            {develop_mode.current_path()}
            ```
            """
        )

    except ValueError:
        return textwrap.dedent(
            f"""
            ```
            you should follow this format
            YYYY:MM:DD hh:mm:ss
            {develop_mode.current_path()}
            ```
            """
        )


def end_maintenance(msg: str) -> str:

    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('end')

    if bot.in_maintenance != True:
        return textwrap.dedent(
            f"""
            ```
            Moonafly is not under maintenance
            {develop_mode.current_path()}
            ```
            """
        )

    with open('../data/txt/init_files/maintenance.txt', 'w') as file:
        file.write(
            'False\n'
            + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            + '\n'
            + responses.develop_mode_current_using_user
        )

    bot.load_maintenance()

    return textwrap.dedent(
        f"""
        ```
        maintenance ended
        {develop_mode.current_path()}
        ```
        """
    )
