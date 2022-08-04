# The Wrench

The official(?) bot for the Let's Create...Together Discord server.

## Setup

1. Clone this repo - `git clone git@github.com:Nemesis-AS/create-together-bot.git`
2. Install the dependencies - `pip install -r requirements.txt`
3. Add a file in the root directory called `.env` [More details below]
4. Run the bot - `py main.py` or `python main.py`

**Note:** MySQL is required for this bot to work\

### Setting up the environment variables

The bot requires some environment variables to be set in order to work. It contains the config and sensitive information.\
Create a file named `.env` in the root directory and put the following things in it - 
```
DISCORD_TOKEN = "<your-discord-token>"
PREFIX = "<prefix-for-the-bot>"

DB_USERNAME = "<database-username>"
DB_PASSWORD = "<database-password>"
DB_NAME = "<database-name>"
DB_HOST = "<database-address>"
```
\
`PREFIX` would be the bot's prefix. Suggested value: `-`\
`DB_HOST` should be set to `localhost`, if running locally
