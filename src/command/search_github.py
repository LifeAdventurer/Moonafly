import textwrap

import requests
import terminal_mode


def get_search_github_response(msg: str) -> str:
    github_url = "https://github.com/" + msg
    response = requests.get(github_url)
    if response.status_code == 404:
        return textwrap.dedent(
            f"""
            The url {github_url} is not found (404 Not Found).
            ```
            {terminal_mode.current_path()}
            ```
            """
        )

    else:
        return textwrap.dedent(
            f"""
            {github_url}
            ```
            {terminal_mode.current_path()}
            ```
            """
        )
