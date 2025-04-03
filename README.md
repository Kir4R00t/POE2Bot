# POE2Bot
So this is a bot that does a few cool things related to poe2

### POE2 Commands:
- trade - issue trade query to poe2 trade site API, displays first 10 results in a paginated embed
- currency - using poe2scout API's collected data you can display current market prices for basic currency
NOTE: currency command is not working for now since there are changes being made to the poe2 scout API
    I will have to adjust the currency command to the upcoming changes

### Other Commands:
- rtd - roll the dice -> get result from 1 to 6
- coinflip - flip a coin -> get tails or head
- gibcat - issue a CATAPI query and get a random picture of a cat

### What's coming ?
- I want to improve currency command so that it will let you specify which items you want to convert (for example how many chaos does div cost)
and let users check other categories of items (soul cores, splinters etc.)
- I want to make trade command more 'user friendly' for now it is just a proof of concept

### Deploy
- `docker-compose up -d --build`