from cmd import remote
from cmd import news


import textwrap


# constants
TAB_SIZE = 4


def split_message(response: str) -> list:

    split_response = []

    if remote.on_remote == True:
        # current message group total word count
        word_count = 0
        # calculate the count of '\n' it takes 1 space
        line_count = 0
        response = response.splitlines()
        # the filename bar
        output_prefix = '\n'.join(response[:3])
        split_response.append(output_prefix)
        # the current path bar
        output_suffix = '\n'.join(response[-3:])
        # cut the prefix and suffix
        response = response[4:-4]
        lines = []
        for line in response:
            # prevent backticks breaking the code block
            # TODO: find a escape backticks method
            line = line.replace('```', '` ` `')

            if word_count + len(line) + line_count * 2 + 100 > 2000:
                word_count = len(line)
                line_count = 1
                content = ('\n' + ' ' * TAB_SIZE * 5).join(lines)
                lines = [line]
                content = textwrap.dedent(f"""
                    ```{remote.file_language}
                    {content}
                    ```
                """)
                split_response.append(content)

            else:
                word_count += len(line)
                line_count += 1
                lines.append(line)
        # last part of message
        if len(lines) > 0:
            content = ('\n' + ' ' * TAB_SIZE * 4).join(lines)
            content = textwrap.dedent(f"""
                ```{remote.file_language}
                {content}
                ```
            """)
        split_response.append(content)
        # the current path bar
        split_response.append(output_suffix)

        remote.on_remote = False
    
    elif news.sending_news == True:
        response = response.splitlines()
        output_suffix = '\n'.join(response[-3:])
        response = response[:-4]
        word_count = 0
        line_count = 0
        lines = []
        for line in response:
            if word_count + len(line) + line_count * 2 + 50 > 2000:
                word_count = len(line)
                line_count = 1
                content = '\n'.join(lines)
                lines = [line]
                split_response.append(content)
            else:
                word_count += len(line)
                line_count += 1
                lines.append(line)
        
        if len(lines) > 0:
            content = '\n'.join(lines)
        split_response.append(content)
        # the current path bar
        split_response.append(output_suffix)
        news.sending_news = False
    
    return split_response