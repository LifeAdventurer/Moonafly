import json

import requests
from bs4 import BeautifulSoup


def search_dict(
    dictionary: str,
    search_word: str,
    limit: int,
    tab_size: int,
    tab_count: int,
    username: str = None,
) -> str:
    search_word = search_word.lower()

    if dictionary == 'en':
        result = get_info_in_English(search_word, limit)
        space = ' ' * tab_size * tab_count
        if result:
            information = [f"# {search_word}"]
            for index, item in enumerate(result):
                part_of_speech, en_definition, example_list = item
                # removes the certain trailing char from the string
                en_definition = en_definition.rstrip(': ')

                information += [
                    f"## {index + 1}.",
                    part_of_speech,
                    f"### Definition:",
                    f"- {en_definition}",
                    f"### Examples:",
                ]
                information += [f"- {sentence}" for sentence in example_list]

            return ('\n' + space).join(information)
        else:
            return (
                f"Failed to retrieve information for the word '{search_word}'."
            )

    elif dictionary == 'en-zh_TW':
        result = get_info_in_English_Chinese_traditional(search_word, limit)
        space = ' ' * tab_size * tab_count
        if result:
            part_of_speech, en_definition, zh_TW_definition, example_list = (
                result
            )
            # removes the certain trailing char from the string
            en_definition = en_definition.strip(': ')
            zh_TW_definition = zh_TW_definition.strip(': ')

            # save vocabulary
            if zh_TW_definition != 'No definition found':
                try:
                    with open(
                        '../data/json/vocabulary_items.json',
                        'r',
                        encoding='utf-8',
                    ) as file:
                        data = json.load(file)
                except FileNotFoundError:
                    data = {}
                    with open(
                        '../data/json/vocabulary_items.json',
                        'w',
                        encoding='utf-8',
                    ) as file:
                        json.dump(data, file, indent=4)

                if username in data:
                    word_in_data = False
                    for word in data[username]:
                        if search_word == word['word']:
                            word_in_data = True
                            word['count'] += 1
                    if not word_in_data:
                        data[username].append(
                            {
                                'word': search_word,
                                'word_in_zh_TW': zh_TW_definition,
                                'count': 1,
                            }
                        )
                else:
                    data[username] = [
                        {
                            'word': search_word,
                            'word_in_zh_TW': zh_TW_definition,
                            'count': 1,
                        }
                    ]

                with open(
                    '../data/json/vocabulary_items.json', 'w', encoding='utf-8'
                ) as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

            information = [
                f"# {search_word}",
                part_of_speech,
                f"### Definition:",
                f"- {en_definition}",
                f"- {zh_TW_definition}",
                "### Examples:",
            ]
            information += [f"- {sentence}" for sentence in example_list]

            return ('\n' + space).join(information)
        else:
            return (
                f"Failed to retrieve information for the word '{search_word}'."
            )


# en
def get_info_in_English(word, limit_example_count):
    url = f'https://dictionary.cambridge.org/dictionary/english/{word}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    result = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')

        entries = soup.find_all('div', {'class': 'entry'})

        for entry in entries:
            part_of_speech = entry.find('span', {'class': 'pos dpos'})
            part_of_speech = (
                part_of_speech.text.strip()
                if part_of_speech
                else 'No part of speech found'
            )

            en_definition = entry.find('div', {'class': 'def ddef_d db'})
            en_definition_text = (
                en_definition.text.strip()
                if en_definition
                else 'No definition found'
            )

            # Extract example sentence
            examples = entry.find_all('div', {'class': 'examp dexamp'})
            example_list = []
            for example in examples:
                example_sentence = (
                    example.text.strip()
                    if example
                    else 'No example sentence found'
                )
                example_list.append(example_sentence)
                if len(example_list) == limit_example_count:
                    break

            result.append((part_of_speech, en_definition_text, example_list))

        return result

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

        # Extract part of speech
        part_of_speech = soup.find('span', {'class': 'pos dpos'})
        part_of_speech = (
            part_of_speech.text.strip()
            if part_of_speech
            else 'No part of speech found'
        )

        # Extract the definition
        # en
        en_definition = soup.find('div', {'class': 'def ddef_d db'})
        en_definition_text = (
            en_definition.text.strip()
            if en_definition
            else 'No definition found'
        )
        # zh_TW
        zh_TW_definition = soup.find(
            'span', {'class': 'trans dtrans dtrans-se break-cj'}
        )
        zh_TW_definition_text = (
            zh_TW_definition.text.strip()
            if zh_TW_definition
            else 'No definition found'
        )

        # Extract example sentence
        examples = soup.find_all('div', {'class': 'examp dexamp'})
        for example in examples:
            example_sentence = (
                example.text.replace('\n', '').replace('\t', '').strip()
                if example
                else 'No example sentence found'
            )
            example_list.append(example_sentence)
            if len(example_list) == limit_example_count:
                break

        return (
            part_of_speech,
            en_definition_text,
            zh_TW_definition_text,
            example_list,
        )

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
