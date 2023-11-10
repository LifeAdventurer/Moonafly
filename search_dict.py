import requests
from bs4 import BeautifulSoup

def get_cambridge_dictionary_info(word):
    url = f'https://dictionary.cambridge.org/dictionary/english/{word}'
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the definition
        definition = soup.find('div', {'class': 'def ddef_d db'})
        definition_text = definition.text.strip() if definition else 'No definition found'

        # Extract one example sentence
        example_sentence = soup.find('div', {'class': 'examp dexamp'})
        example_sentence_text = example_sentence.text.strip() if example_sentence else 'No example sentence found'

        return definition_text, example_sentence_text

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def search_dict(word):
    result = get_cambridge_dictionary_info(word)

    if result:
        definition, example_sentence = result
        return f"\n**Definition**: {definition}\n**Example**: {example_sentence}\n"
    else:
        return f"Failed to retrieve information for the word '{word}'."