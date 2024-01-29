import terminal_mode


from cmd import command_help


import textwrap
import requests
from bs4 import BeautifulSoup


# constants
TAB_SIZE = 4
HELP_FLAG = '--help'

cnn_root_url = 'https://edition.cnn.com'


sending_news = False


def get_cnn_news(category: str) -> str:
    global sending_news
    
    response = requests.get(f"{cnn_root_url}/{category}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        container_field_links = soup.find_all('div', {'class': 'container__field-links'})
        
        headline_list = []
        news_url_list = []
        for container_field_link in container_field_links:
            news_urls = container_field_link.find_all('a')

            news_headlines = container_field_link.find_all('span', {'class': 'container__headline-text'})
            for headline in news_headlines:
                headline_list.append(headline.text)
            
            for data in news_urls:
                news_url = data.get('href')
                if news_url not in news_url_list:
                    if news_url.startswith('/'):
                        news_url = cnn_root_url + news_url

                    news_url_list.append(news_url)

        sending_news = True

        space = '\n' + ' ' * TAB_SIZE * 3
        return textwrap.dedent(f"""
            {(space).join([f"- [{headline_list[i]}](<{news_url_list[i]}>)" for i in range(min(len(headline_list), 15))])}
            ```
            {terminal_mode.current_path()}
            ```
        """)
        
    else:
        print(f"Failed to retrieve page: '{cnn_root_url}'. Status code: {response.status_code}")
        return textwrap.dedent(f"""
            ```
            Failed to retrieve news, please try again later.
            {terminal_mode.current_path()}
            ```
        """)


cnn_news_categories = [
    'us',
    'world',
    'politics',
    'business',
    'opinion',
    'health',
    'entertainment',
    'style',
    'travel',
    'sports'
]


def show_news_categories() -> str:
    space = '\n' + ' ' * TAB_SIZE * 2
    return textwrap.dedent(f"""
        ```
        {space.join(cnn_news_categories)}
        {terminal_mode.current_path()}
        ```
    """)


def get_news(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('news')

    if msg[:3] == 'get':
        msg = msg[3:].strip()

        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('news_get')

        category = 'world'  # default

        if len(msg) > 0:
            if msg in cnn_news_categories:
                category = msg
            else:
                return textwrap.dedent(f"""
                    ```
                    category: '{msg}' not found
                    {terminal_mode.current_path()}
                    ```
                """)

        return get_cnn_news(category)
    elif msg[:4] == 'show':
        msg = msg[4:].strip()

        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('news_show')

        return show_news_categories()
    else:
        return terminal_mode.command_not_found(msg)