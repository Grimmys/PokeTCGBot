# PokeTCGOnline

## Requirements

This project requires the following:

- Python version >=3.10 (and the related ```pip``` version)
- direnv (optional)

## Environment setup

Run the following command from the root of the repository to install all the required dependencies:

```commandline
pip3 install -r requirements.txt
```

Then, generate your bot token and set it in an environment variable named ```DISCORD_TOKEN```... Or assign it to ```DISCORD_TOKEN``` in `config.py` file.

For more information about the generation of the token, follow the official Discord documentation: [Documentation - Creating an app](https://discord.com/developers/docs/getting-started#creating-an-app).

For easier handling of your environment variables, you can put them in a ```.envrc``` file copied from ```.envrc.sample``` file, and use the [direnv](https://direnv.net) tool to autoload the variables.

Fill also the required config values in the "Required config parameters to replace" section in `config.py` file.

Before the first start-up, you also need to manually fetch the collection of cards by running `scripts/fetch_cards.py`.

> :warning: **It will take some time to fetch the whole collection of cards**, so be patient

Finally, run ```main.py``` file to start the server.