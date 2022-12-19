# PokeTCGOnline

## Requirements

This project requires the following:

- Python version >=3.9 (and the related ```pip``` version)
- direnv (optional)

## Environment setup

Run the following command from the root of the repository to install all the required dependencies:

```commandline
pip3 install -r requirements.txt
```

Then, generate your bot token and set it in an environment variable named ```DISCORD_TOKEN```.

For more information about the generation of the token, follow the official Discord documentation: [Documentation - Creating an app](https://discord.com/developers/docs/getting-started#creating-an-app).

For easier handling of your environment variables, you can put them in a ```.envrc``` file copied from ```.envrc.sample``` file, and use the [direnv](https://direnv.net) tool to autoload the variables.

Finally, run ```main.py``` file to start the server.