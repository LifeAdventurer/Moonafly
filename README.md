# Moonafly

1. Set your token via `config.json`:

    ```json
    {
        "token": "{your TOKEN}"
    }
    ```

2. Set your password for entering terminal mode via `passwords.json`:

    ```json
    {
        "terminal_password": "{your password}"
    }
    ```

3. Set your special guest list to let certain users use the terminal mode without a password via `special_guests.json`:

    ```json
    {
        "guests": [
            "{guest 1}",
            "{guest 2}",
            "{guest 3}"
        ]
    }
    ```

4. Set rank list for game 1A2B feature via `game_1A2B_ranks.json`:

    ```json
    {

    }
    ```

5. Run the bot in your terminal

    ```bash
    py main.py
    ```
