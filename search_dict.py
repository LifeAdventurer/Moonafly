import requests
import json
from bs4 import BeautifulSoup

# en
def get_info_in_English(word, limit_example_count):
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
        en_definition = soup.find('div', {'class': 'def ddef_d db'})
        en_definition_text = en_definition.text.strip() if en_definition else 'No definition found'

        # Extract example sentence
        examples = soup.find_all('div', {'class': 'examp dexamp'})
        for example in examples:
            example_sentence = example.text.strip() if example else 'No example sentence found'
            example_list.append(example_sentence)
            if len(example_list) == limit_example_count:
                break

        return en_definition_text, example_list

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
# en-zh_TW
def get_info_in_English_Chinese_traditional(word, limit_example_count):
    url = f'https://dictionary.cambridge.org/dictionary/english-chinese-traditional/{word}'

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
        # en
        en_definition = soup.find('div', {'class': 'def ddef_d db'})
        en_definition_text = en_definition.text.strip() if en_definition else 'No definition found'
        # zh_TW
        zh_TW_definition = soup.find('span', {'class': 'trans dtrans dtrans-se break-cj'})
        zh_TW_definition_text = zh_TW_definition.text.strip() if zh_TW_definition else 'No definition found'

        # Extract example sentence
        examples = soup.find_all('div', {'class': 'examp dexamp'})
        for example in examples:
            example_sentence = example.text.strip() if example else 'No example sentence found'
            example_list.append(example_sentence)
            if len(example_list) == limit_example_count:
                break

        return en_definition_text, zh_TW_definition_text, example_list

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def search_dict(dictionary, word, limit, tab_size, tab_count, username = ''):
    
    if dictionary == 'en':
        result = get_info_in_English(word, limit)
        space = ' ' * tab_size * tab_count
        if result:
            en_definition, example_list = result
            # removes the certain trailing char from the string
            en_definition = en_definition.rstrip(': ') 

            information = f"# {word}\n"
            information += f"{space}### Definition: \n{space}- {en_definition}\n"
            information += f"{space}### Examples: \n"
            for sentence in example_list:
                information += f"{space}- {sentence}\n"
            return information
        else:
            return f"Failed to retrieve information for the word '{word}'."
            
    elif dictionary == 'en-zh_TW':
        result = get_info_in_English_Chinese_traditional(word, limit)
        space = ' ' * tab_size * tab_count
        if result:
            en_definition, zh_TW_definition, example_list = result
            # removes the certain trailing char from the string
            en_definition = en_definition.strip(': ') 
            zh_TW_definition = zh_TW_definition.strip(': ')

            # save vocabulary
            if zh_TW_definition != 'No definition found':
                with open('./data/json/vocabulary_items.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                if username in data:
                    data[username].append({'word': word.lower(), 'word_in_zh_TW': zh_TW_definition})
                else:
                    data[username] = [{'word': word, 'word_in_zh_TW': zh_TW_definition}]
                
                with open('./data/json/vocabulary_items.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent = 4, ensure_ascii = False)

            information = f"# {word}\n"
            information += f"{space}### Definition: \n"
            information += f"{space}- {en_definition}\n"
            information += f"{space}- {zh_TW_definition}\n"
            information += f"### Examples: \n"
            for sentence in example_list:
                information += f"{space}- {sentence.strip()}\n"
            return information
        else:
            return f"Failed to retrieve information for the word '{word}'."