import textwrap
import json
import random
import terminal_mode


random_vocab_testing = False
vocab_index = 0
previous_index = -1


def get_random_vocab_test(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global random_vocab_testing, vocab_index, previous_index

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
                
                random_index = random.randint(0, len(vocabulary_list[username]) - 1)
                while random_index == previous_index:
                    random_index = random.randint(0, len(vocabulary_list[username]) - 1)

                previous_index = vocab_index
                vocab_index = random_index

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
            word = vocabulary_list[username][vocab_index]['word']
            word_in_zh_TW = vocabulary_list[username][vocab_index]['word_in_zh_TW']

            return textwrap.dedent(f"""
                ```
                Oops! Wrong answer
                {word}
                {word_in_zh_TW}
                {terminal_mode.current_path()}
                ```
            """)

        # update data
        with open('../data/json/vocabulary_items.json', 'w', encoding='utf-8') as file:
            json.dump(vocabulary_list, file, indent=4, ensure_ascii=False)

    else:
        return command_not_found(msg)