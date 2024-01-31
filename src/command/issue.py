import develop_mode


from command import command_help


import textwrap
import requests


# constants
TAB_SIZE = 4
HELP_FLAG = '--help'


github_api_url = 'https://api.github.com'
github_repo = 'lifeadventurer/Moonafly'


def get_issues_on_github() -> str:
    url = f"{github_api_url}/repos/{github_repo}/issues"

    response = requests.get(url)

    if response.status_code == 200:
        issues = response.json()

        issue_list = []
        for issue in issues:
            issue_title = f"#{issue['number']} {issue['title']}"
            if len(issue_title) > 80:
                issue_title = issue_title[:79] + '>'
            
            issue_list.append(issue_title)

        issue_list = ('\n' + ' ' * TAB_SIZE * 3).join(issue_list)

        return textwrap.dedent(f"""
            ```
            {issue_list}
            {develop_mode.current_path()}
            ```
        """)
    
    else:
        return textwrap.dedent(f"""
            ```
            failed to fetch GitHub issues. Status code: {response.status_code}
            {develop_mode.current_path()}
            ```
        """)


def get_issues(msg: str) -> str:
    if msg[:4] == 'list':
        msg = msg[4:].strip()

        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('issue_list')
        
        return get_issues_on_github()
    
    else:
        return develop_mode.command_not_found(msg)