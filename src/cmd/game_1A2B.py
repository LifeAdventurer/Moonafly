import terminal_mode


from cmd import command_help


import textwrap
import random
import json


playing_game_1A2B = False
target_number = ''
target_number_len = 0
attempts = 0


def load_game_1A2B_ranks() -> dict:
    global game_1A2B_ranks
    with open('../data/json/game_1A2B_ranks.json') as file:
        game_1A2B_ranks = json.load(file)
    
    return game_1A2B_ranks


def save_game_1A2B_result(length: int, attempts: int) -> int:
    # you must get the ranks every time due to the user might play several times
    records = load_game_1A2B_ranks()
    # set the group if there isn't one in the data
    records.setdefault(str(length), [])
    
    # save the record data including attempts, user, timestamp
    records[str(length)].append(
        {
            'attempts': attempts,
            'user': responses.terminal_mode_current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )
    # sort the rank by attempts first then timestamp
    records[str(length)].sort(key=lambda x: (x['attempts'], x['timestamp']))

    rank = 0
    for record in records[str(length)]:
        # the first position of the next attempts = the last position of the user attempt + 1
        # which can match the rank starts with 0
        if record['attempts'] > attempts:
            break
        rank += 1

    # save the result to json file
    with open('../data/json/game_1A2B_ranks.json', 'w') as file:
        json.dump(records, file, indent = 4)

    return rank


def show_1A2B_every_length_ranking(tab_size: int, tab_count: int) -> str:
    records = load_game_1A2B_ranks()

    indentation = ' ' * tab_size * tab_count
    ranking = 'length | attempts | user\n' + indentation
    ranking += '------------------------\n'
    for length in range(4, 11):
        ranking += indentation + f"  {(' ' + str(length))[-2:]}"
        if len(records[str(length)]) == 0:
            ranking += '   | no data  | no data\n'
            continue

        ranking += f"   |    {('  ' + str(records[str(length)][0]['attempts']))[-max(3, len(str(length))):]}   | {records[str(length)][0]['user']}\n"
    
    return ranking


def show_1A2B_certain_length_ranking(length: int, tab_size: int, tab_count: int) -> str:
    records = load_game_1A2B_ranks()[str(length)]
    
    indentation = ' ' * tab_size * tab_count
    ranking = f"length - {length}\n{indentation}"
    if len(records) == 0:
        ranking += 'no data'
        return ranking
    
    ranking += 'attempts | user\n' + indentation
    ranking += '----------------\n'
    for index, record in enumerate(records):
        if index >= 10:
            break

        ranking += indentation + f"  {('  ' + str(record['attempts']))[-max(3, len(str(length))):]}    | {record['user']}\n"
    
    return ranking


def show_1A2B_certain_user_ranking(username : str, tab_size: int, tab_count: int) -> str:
    records = load_game_1A2B_ranks()

    indentation = ' ' * tab_size * tab_count
    ranking = f"user - {username}\n{indentation}"
    ranking += 'length | attempts\n' + indentation
    ranking += '-------------------\n'
    for length in range(4, 11):
        ranking += indentation + f"  {(' ' + str(length))[-2:]}"
        
        no_data = True
        for index, record in enumerate(records[str(length)]):
            if record['user'] == username:
                no_data = False
                ranking += f"   | {('  ' + str(record['attempts']))[-max(3, len(str(length))):]} (rank {index + 1})\n"
                break
        
        if no_data:
            ranking += '   |  no data\n'
            continue

    return ranking


def play_game_1A2B(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global playing_game_1A2B, target_number, target_number_len, attempts

    # comment or chat during game
    if playing_game_1A2B:
        if (
            msg[:4] != 'stop'
            and msg[:4] != 'Stop'
            and not all(char.isdigit() for char in msg)
        ):
            return ''

    if not playing_game_1A2B:
        if msg[:5] == 'start' or msg[:5] == 'Start':
            playing_game_1A2B = True
            attempts = 0
            msg = msg[6:].strip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('game_1A2B_start')

            # choose the length you want to start playing
            if len(msg) > 0:
                if msg.isdigit() and 4 <= int(msg) <= 10:
                    target_number_len = int(msg)
                    # the numbers won't be duplicated
                    target_number = ''.join(random.sample('0123456789', target_number_len))

                else:
                    return textwrap.dedent(f"""
                        ```
                        please enter a valid number between 4 to 10
                        {terminal_mode.current_path()}
                        ```
                    """)

            else:
                # the default length for this game
                target_number_len = 4
                # the numbers won't be duplicated
                target_number = ''.join(random.sample('123456', target_number_len))
            print(target_number)
            return textwrap.dedent(f"""
                ```
                {target_number_len}-digit number generated.
                ```
            """)

        elif msg[:4] == 'rank' or msg[:4] == 'Rank':
            msg = msg[5:].strip()

            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('game_1A2B_rank')

            # show certain length ranking
            if len(msg) > 0:
                if msg.isdigit():
                    if 4 <= int(msg) <= 10:
                        search_rank_length = int(msg)
                        return textwrap.dedent(f"""
                            ```
                            {show_1A2B_certain_length_ranking(search_rank_length, 4, 7)}
                            {terminal_mode.current_path()}
                            ```
                        """)

                    else:
                        return textwrap.dedent(f"""
                            ```
                            please enter a valid number between 4 to 10
                            {terminal_mode.current_path()}
                            ```
                        """)
                
                # search user ranking
                else:
                    certain_user = msg
                    if msg == '-p':
                        certain_user = username
                    return textwrap.dedent(f"""
                        ```
                        {show_1A2B_certain_user_ranking(certain_user, 4, 6)}
                        {terminal_mode.current_path()}
                        ```
                    """)

            # show every length ranking
            return textwrap.dedent(f"""
                ```
                {show_1A2B_every_length_ranking(4, 4)}
                {terminal_mode.current_path()}
                ```
            """)

    elif playing_game_1A2B:
        # stop the game if you want
        if msg[:4] == 'stop' or msg[:4] == 'Stop':
            playing_game_1A2B = False
            msg = msg[5:].strip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('game_1A2B_stop')

            # use `stop start` to restart the game if you want
            # any other commands can be add after that
            if len(msg) > 0:
                message.content = msg
                return responses.get_response(message)

            return textwrap.dedent(f"""
                ```
                Game ended.
                {terminal_mode.current_path()}
                ```
            """)
        guess = msg

        if len(guess) == target_number_len and guess.isdigit():
            # A means the number is correct and the position is correct
            A_cnt = sum(t == g for t, g in zip(target_number, guess))

            # B means the number is correct, but the position is incorrect
            B_cnt = (
                sum(
                    min(target_number.count(digit), guess.count(digit))
                    for digit in target_number
                ) - A_cnt
            )

            attempts += 1

            # User got the target number
            if A_cnt == target_number_len:
                playing_game_1A2B = False
                
                # save game records for the rank board
                user_rank = save_game_1A2B_result(target_number_len, attempts)

                return textwrap.dedent(f"""
                    ```
                    Congratulations! You guessed the target number {target_number} in {attempts} attempts.
                    Your got rank {user_rank} in length {target_number_len} !!!
                    {terminal_mode.current_path()}
                    ```
                """)

            else:
                return textwrap.dedent(f"""
                    ```
                    {A_cnt}A{B_cnt}B
                    ```
                """)

        else:
            return textwrap.dedent(f"""
                ```
                please enter a valid input with only numbers and the correct length
                ```
            """)

    else:
        return command_not_found(msg)