import textwrap

import requests

import develop_mode
import responses
import terminal_mode
from command import command_help

# constants
TAB_SIZE = 4
HELP_FLAG = '--help'


def get_issues_on_github(github_repo: str = 'Lifeadventurer/Moonafly') -> str:
    current_path = ''
    if responses.is_terminal_mode == True:
        current_path = terminal_mode.current_path()
    elif responses.is_develop_mode == True:
        current_path = develop_mode.current_path()

    url = f"https://api.github.com/repos/{github_repo}/issues"

    response = requests.get(url)

    if response.status_code == 200:
        issues = response.json()

        # issue number is sorted in descending order
        max_issue_len = len(str(issues[0]['number']))

        issue_list = []
        for issue in issues:
            issue_title = (
                f"#{str(issue['number']).rjust(max_issue_len)} {issue['title']}"
            )
            if len(issue_title) > 80:
                issue_title = issue_title[:79] + '>'

            issue_list.append(issue_title)

        issue_list = ('\n' + ' ' * TAB_SIZE * 3).join(issue_list)

        return textwrap.dedent(
            f"""
            ```
            {issue_list}
            
            {current_path}
            ```
            """
        )

    else:
        return textwrap.dedent(
            f"""
            ```
            failed to fetch GitHub issues. Status code: {response.status_code}
            {current_path}
            ```
            """
        )


def get_issues(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('issues')

    if msg.startswith('list'):
        msg = msg[4:].strip()

        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('issues_list')

        if len(msg) > 0:
            return get_issues_on_github(msg)

        return get_issues_on_github()

    else:
        if responses.is_terminal_mode == True:
            return terminal.command_not_found(msg)
        elif responses.is_develop_mode == True:
            return develop_mode.command_not_found(msg)
