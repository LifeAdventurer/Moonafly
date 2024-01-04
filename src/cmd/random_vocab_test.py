import textwrap
import json
import random
import terminal_mode

random_vocab_testing = False
vocab_index = 0

def get_random_vocab_test(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global random_vocab_testing, vocab_index

    if msg.lower() == 'g':
        global vocabulary_list
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
                random_vocab_testing = True
                vocab_index = random.randint(0, len(vocabulary_list[username]) - 1)
                return textwrap.dedent(f"""
                    ```
                    {vocabulary_list[username][vocab_index]['word']}
                    ```
                """)

        else: 
            return textwrap.dedent(f"""
                ```
                You have never use dict feature before. 
                Try it to save vocabulary items in Moonafly, then
                use ~/random/vocab/test to examine yourself
                {terminal_mode.current_path()}
                ```
            """)
    
    elif random_vocab_testing:
        if msg in vocabulary_list[username][vocab_index]['word_in_zh_TW']:
            random_vocab_testing = False
            vocabulary_list[username][vocab_index]['count'] -= 1
            word = vocabulary_list[username][vocab_index]['word']
            word_in_zh_TW = vocabulary_list[username][vocab_index]['word_in_zh_TW']
            if vocabulary_list[username][vocab_index]['count'] == 0:
                del vocabulary_list[username][vocab_index]
            with open('../data/json/vocabulary_items.json', 'w', encoding='utf-8') as file:
                json.dump(vocabulary_list, file, indent=4, ensure_ascii=False)
            return textwrap.dedent(f"""
                ```
                Correct!
                {word}
                {word_in_zh_TW}
                {terminal_mode.current_path()}
                ```
            """)

        else:
            random_vocab_testing = False
            vocabulary_list[username][vocab_index]['count'] += 1
            with open('../data/json/vocabulary_items.json', 'w', encoding='utf-8') as file:
                json.dump(vocabulary_list, file, indent=4, ensure_ascii=False)
            return textwrap.dedent(f"""
                ```
                Oops! Wrong
                {vocabulary_list[username][vocab_index]['word']}
                {vocabulary_list[username][vocab_index]['word_in_zh_TW']}
                {terminal_mode.current_path()}
                ```
            """)

    else:
        return command_not_found(msg)