# The Wrench

The official(?) bot for the Let's Create...Together Discord server.

## Setup

1. Clone this repo - `git clone git@github.com:Nemesis-AS/create-together-bot.git`
2. Install the dependencies - `pip install -r requirements.txt`
3. Add a file in the root directory called `.env` [More details below]
4. Run the bot - `py main.py` or `python main.py`

### Setting up the environment variables

The bot requires some environment variables to be set in order to work. It contains the config and sensitive information.\
Create a file named `.env` in the root directory and put the following things in it - 
```
DISCORD_TOKEN = "<your-discord-token>"
PREFIX = "<prefix-for-the-bot>"
USER_ROLE = "<name-of-the-role>"

DB_USERNAME = "<database-username>"
DB_PASSWORD = "<database-password>"
DB_NAME = "<database-name>"
```
\
`USER_ROLE` would be the role required to be able to use the bot's commands\
`PREFIX` would be the bot's prefix. Suggested value: `-`