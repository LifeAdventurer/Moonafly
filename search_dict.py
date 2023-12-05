import requests
from bs4 import BeautifulSoup

def get_cambridge_dictionary_info(word, limit_example_count):
    url = f'https://dictionary.cambridge.org/dictionary/english/{word}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    example_list = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the definition
        definition = soup.find('div', {'class': 'def ddef_d db'})
        definition_text = definition.text.strip() if definition else 'No definition found'

        # Extract one example sentence
        examples = soup.find_all('div', {'class': 'examp dexamp'})
        for example in examples:
            example_sentence = example.text.strip() if example else 'No example sentence found'
            example_list.append(example_sentence)
            if len(example_list) == limit_example_count:
                break

        return definition_text, example_list

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def search_dict(word, limit, tab_size, tab_count):
    result = get_cambridge_dictionary_info(word, limit)
    space = ' ' * tab_size * tab_count
    if result:
        definition, example_list = result
        definition = definition.rstrip(': ') # removes the certain trailing char from the string
        information = f"{space}### Definition: \n{space}- {definition}\n"
        information += f"{space}### Examples: \n"
        for sentence in example_list:
            information += f"{space}- {sentence}\n"
        return f"{space}# {word}\n" + information
    else:
        return f"Failed to retrieve information for the word '{word}'."