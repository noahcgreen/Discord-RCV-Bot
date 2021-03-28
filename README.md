# Discord-RCV-Bot
Anonymous ranked choice voting Discord bot

# To add to your Discord server:

Go to
```
https://discord.com/api/oauth2/authorize?client_id=825418814774181938&permissions=0&scope=bot
```

That's it! You should now be able to interact with the bot in your server via the following commands:
* `-vote create {vote-name}`


  Creates a new vote. The bot will prompt for descriptions of each candidate.

* `-vote open {vote-name} {voter-role}`

  Opens a vote. The bot will DM all users in the server with `voter-role` and retrieve their votes.

* `-vote close {vote-name}`

  Closes a vote and displays results.

# To host the bot on your own:

1. Edit the token in `__main__.py` with your application bot token from the Discord Developer Portal.
2. Run `python3 __main__.py`.
