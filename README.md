# POE2Bot
So this is a bot that does a few cool things related to poe2

### POE2 Commands:
- /trade - issue trade query to poe2 trade site API, displays first 10 results in a paginated embed
- /poe2scout - using poe2scout API's collected data you can display current market prices for all kinds of currency items
NOTE: currency command is not working for now since there are changes being made to the poe2 scout API
    I will have to adjust the currency command to the upcoming changes

### Other Commands:
- /gibcat - issue a CATAPI query and get a random picture of a cat
- /rtd - roll the dice -> get result from 1 to 6
- /coinflip - flip a coin -> get tails or head

### What's coming ?
- I will be improving the currency command to cover all item categories
- I want to make trade command more 'user friendly' for now it is just a proof of concept
- I will be adding a command to price check item (so basically Sidekick command)
- I will be adding new commands as GGG will let developers integrate more game data to their apps :>

### Deploy
- `docker-compose up -d --build`