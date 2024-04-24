import json
import random
import textwrap
import time

import responses
import terminal_mode
from command import command_help
from constants import HELP_FLAG, TAB_SIZE

playing_game_1A2B = False
target_number = ''
target_number_len = 0
attempts = 0


def load_game_1A2B_ranks() -> dict:
    try:
        with open('../data/json/game_1A2B_ranks.json') as file:
            game_1A2B_ranks = json.load(file)
    except FileNotFoundError:
        game_1A2B_ranks = {
            "4": [],
            "5": [],
            "6": [],
            "7": [],
            "8": [],
            "9": [],
            "10": [],
        }
        with open('../data/json/game_1A2B_ranks.json', 'w') as file:
            json.dump(game_1A2B_ranks, file)

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
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
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
        json.dump(records, file, indent=4)

    return rank


def show_1A2B_every_length_ranking(tab_size: int, tab_count: int) -> str:
    records = load_game_1A2B_ranks()

    ranking = ['length | attempts | user']
    ranking.append('-------------------------')
    for length in range(4, 11):
        len_str = '  ' + (' ' + str(length))[-2:]
        if len(records[str(length)]) == 0:
            ranking.append(f"{len_str}   | no data  | no data")
        else:
            attempts = ('  ' + str(records[str(length)][0]['attempts']))[
                -max(3, len(str(length))) :
            ]
            user = records[str(length)][0]['user']
            ranking.append(f"{len_str}   |    {attempts}   | {user}")

    ranking = ('\n' + ' ' * tab_size * tab_count).join(ranking)

    return ranking


def show_1A2B_certain_length_ranking(
    length: int, tab_size: int, tab_count: int
) -> str:
    records = load_game_1A2B_ranks()[str(length)]

    ranking = [f"length - {length}"]
    if len(records) == 0:
        ranking.append('no data')
    else:
        ranking.append('attempts | user')
        ranking.append('----------------')
        for index, record in enumerate(records):
            if index >= 10:
                break

            ranking.append(
                f"  {('  ' + str(record['attempts']))[-max(3, len(str(length))):]}    | {record['user']}"
            )

    ranking = ('\n' + ' ' * tab_size * tab_count).join(ranking)

    return ranking


def show_1A2B_certain_user_ranking(
    username: str, tab_size: int, tab_count: int
) -> str:
    records = load_game_1A2B_ranks()

    ranking = [f"user - {username}"]
    ranking.append('length | attempts')
    ranking.append('-------------------')
    for length in range(4, 11):
        len_str = f"  {(' ' + str(length))[-2:]}"

        no_data = True
        for index, record in enumerate(records[str(length)], start=1):
            if record['user'] == username:
                no_data = False
                attempts = ('  ' + str(record['attempts']))[
                    -max(3, len(str(length))) :
                ]
                ranking.append(f"{len_str}   | {attempts} (rank {index})")
                break

        if no_data:
            ranking.append(f"{len_str}   |  no data")

    ranking = ('\n' + ' ' * tab_size * tab_count).join(ranking)

    return ranking


def play_game_1A2B(message) -> str:
    username = str(message.author)
    msg = str(message.content).strip()

    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('game_1A2B')

    global playing_game_1A2B, target_number, target_number_len, attempts

    # comment or chat during game
    if playing_game_1A2B and not (
        msg.startswith('stop') or not all(char.isdigit() for char in msg)
    ):
        return ''

    if not playing_game_1A2B:
        if msg.startswith('start'):
            playing_game_1A2B = True
            attempts = 0
            msg = msg[6:].strip()
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('game_1A2B_start')

            # choose the length you want to start playing
            if len(msg) > 0:
                if msg.isdigit() and 4 <= int(msg) <= 10:
                    target_number_len = int(msg)
                    # the numbers won't be duplicated
                    target_number = ''.join(
                        random.sample('0123456789', target_number_len)
                    )

                else:
                    return textwrap.dedent(
                        f"""
                        ```
                        please enter a valid number between 4 to 10
                        {terminal_mode.current_path()}
                        ```
                        """
                    )

            else:
                # the default length for this game
                target_number_len = 4
                # the numbers won't be duplicated
                target_number = ''.join(
                    random.sample('123456', target_number_len)
                )
            print(target_number)
            return textwrap.dedent(
                f"""
                ```
                {target_number_len}-digit number generated.
                ```
                """
            )

        elif msg.startswith('rank'):
            msg = msg[5:].strip()

            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('game_1A2B_rank')

            # show certain length ranking
            if len(msg) > 0:
                if msg.isdigit():
                    if 4 <= int(msg) <= 10:
                        search_rank_length = int(msg)
                        return textwrap.dedent(
                            f"""
                            ```
                            {show_1A2B_certain_length_ranking(search_rank_length, TAB_SIZE, 7)}
                            {terminal_mode.current_path()}
                            ```
                            """
                        )

                    else:
                        return textwrap.dedent(
                            f"""
                            ```
                            please enter a valid number between 4 to 10
                            {terminal_mode.current_path()}
                            ```
                            """
                        )

                # search user ranking
                else:
                    certain_user = msg
                    if msg == '-p':
                        certain_user = username
                    return textwrap.dedent(
                        f"""
                        ```
                        {show_1A2B_certain_user_ranking(certain_user, TAB_SIZE, 6)}
                        {terminal_mode.current_path()}
                        ```
                        """
                    )

            # show every length ranking
            return textwrap.dedent(
                f"""
                ```
                {show_1A2B_every_length_ranking(TAB_SIZE, 4)}
                {terminal_mode.current_path()}
                ```
                """
            )

        else:
            return terminal_mode.command_not_found(msg)

    else:
        # stop the game if you want
        if msg.startswith('stop'):
            playing_game_1A2B = False
            msg = msg[5:].strip()
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('game_1A2B_stop')

            # use `stop start` to restart the game if you want
            # any other commands can be add after that
            if len(msg) > 0:
                message.content = msg
                return responses.get_response(message)

            return textwrap.dedent(
                f"""
                ```
                Game ended.
                {terminal_mode.current_path()}
                ```
                """
            )
        guess = msg

        if len(guess) == target_number_len and guess.isdigit():
            # A means the number is correct and the position is correct
            A_cnt = sum(t == g for t, g in zip(target_number, guess))

            # B means the number is correct, but the position is incorrect
            B_cnt = (
                sum(
                    min(target_number.count(digit), guess.count(digit))
                    for digit in target_number
                )
                - A_cnt
            )

            attempts += 1

            # User got the target number
            if A_cnt == target_number_len:
                playing_game_1A2B = False

                # save game records for the rank board
                user_rank = save_game_1A2B_result(target_number_len, attempts)

                return textwrap.dedent(
                    f"""
                    ```
                    Congratulations! You guessed the target number {target_number} in {attempts} attempts.
                    Your got rank {user_rank} in length {target_number_len} !!!
                    {terminal_mode.current_path()}
                    ```
                    """
                )

            else:
                return textwrap.dedent(
                    f"""
                    ```
                    {A_cnt}A{B_cnt}B
                    ```
                    """
                )

        else:
            return textwrap.dedent(
                """
                ```
                please enter a valid input with only numbers and the correct length
                ```
                """
            )
