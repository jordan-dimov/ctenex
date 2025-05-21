Market maker bot
=================

The basic approach is this:

1. Repeatedly poll the exchange API to track current market prices and market depth
    (the size of an order needed to move the market price by a given amount)
2. Update internal state to track prices for each contract (the "mid-price") - edge
    case when there is no ask/bid
3. Place multiple orders at different price levels around the mid-price - limit
    the increments, steps and number of steps
4. Implement a spread strategy to profit from the difference between bid and ask prices
5. Regularly cancel and replace orders as needed to maintain the desired spread
6. Control exposure and limit potential losses
7. Configurable settings to adjust the bot's behavior
