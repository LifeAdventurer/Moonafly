import terminal_mode


import textwrap
import json
import random


vocab_index = 0
previous_index = -1


def get_random_vocab_review(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    if msg.lower() == 'g':
        with open('../data/json/vocabulary_items.json', 'r', encoding='utf-8') as file:
            vocabulary_list = json.load(file)
        
        if username in vocabulary_list:
            if len(vocabulary_list[username]) == 0:
                return textwrap.dedent(f"""
                    ```
                    You have cleared all the words.
                    {terminal_mode.current_path()}
                    ```
                """)
            else:
                random_index = random.randint(0, len(vocabulary_list[username]) - 1)
                while random_index == previous_index:
                    random_index = random.randint(0, len(vocabulary_list[username]) - 1)

                previous_index = vocab_index
                vocab_index = random_index


                return textwrap.dedent(f"""
                    ```
                    {vocabulary_list[username][vocab_index]['word']}
                    {vocabulary_list[username][vocab_index]['word_in_zh_TW']}
                    {terminal_mode.current_path()}
                    ```
                """)
            
        else:
            return textwrap.dedent(f"""
                ```
                You have never use ~/dict feature before. 
                Try it to save vocabulary items in Moonafly, then
                use ~/random/vocab/test to examine yourself and 
                ~/random/vocab/review to review the words.
                {terminal_mode.current_path()}
                ```
            """)
    
    else:
        return command_not_found(msg)