# Moonafly

## Secret files

1. Set your token via `config.json`:

    ```json
    {
        "token": "{your TOKEN}"
    }
    ```

2. Set your user identity list via `user_identity.json` including author, developer, guests role:

    ```json
    {
        "author": [
            
        ],
        "developers": [

        ],
        "guests": [

        ]
    }
    ```

3. Set rank list for game 1A2B feature via `game_1A2B_ranks.json`

4. Set terminal login history via `terminal_login_history.json`

5. Set your maintenance status via `maintenance.txt`:

    ```json
    True / False
    YYYY-MM-DD hh:mm:ss
    DEVELOPER_NAME
    ```

6. Set your Moonafly structure via `Moonafly_structure.json`

7. Set your vocabulary items list via `vocabulary_items.json`

8. Set your clipboard via `clipboard.json`

## Run Moonafly

### Windows

```bat
run_moonafly.bat
```

### macOS/Linux

```bash
run_moonafly.sh
```
