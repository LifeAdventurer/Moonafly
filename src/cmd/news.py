import terminal_mode


import textwrap
import requests
from bs4 import BeautifulSoup


# constants
TAB_SIZE = 4


cnn_root_url = 'https://edition.cnn.com'


def get_cnn_news() -> str:
    response = requests.get(cnn_root_url + '/world')

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

        space = '\n' + ' ' * TAB_SIZE * 3
        return textwrap.dedent(f"""
            {(space).join([f"- [{headline_list[i]}](<{news_url_list[i]}>)" for i in range(min(len(headline_list), 5))])} 
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


def get_news(msg: str) -> str:
    if msg == 'get':
        return get_cnn_news()
    else:
        return terminal_mode.command_not_found()