import textwrap

# constants
TAB_SIZE = 4


def split_message(response: str) -> list:
    split_response = []

    response = response.splitlines()
    word_count = 0
    line_count = 0
    lines = []
    cur_msg_wrapper = ''
    for line in response:
        if line.startswith('```'):
            lines.append(line)
            if cur_msg_wrapper == '':
                cur_msg_wrapper = line
            else:
                cur_msg_wrapper = ''

            continue

        line = line.replace('```', '` ` `')
        if word_count + len(line) + line_count * 2 + 50 > 2000:
            word_count = len(line)
            line_count = 1
            if cur_msg_wrapper != '':
                lines.append('```')
            content = '\n'.join(lines)
            split_response.append(content)
            lines = [cur_msg_wrapper, line]
        else:
            word_count += len(line)
            line_count += 1
            lines.append(line)

    if len(lines) > 0:
        content = '\n'.join(lines)
        split_response.append(content)

    return split_response
