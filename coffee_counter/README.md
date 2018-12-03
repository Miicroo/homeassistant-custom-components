# Coffee counter

> PSA: This is not really a custom component in homeassistant, but rather a way of achieving the behaviour of a counter that resets daily.

## Background
I am Swedish, so here [it is custom to drink a lot of coffee](https://static.vinepair.com/wp-content/uploads/2017/04/coffee-infographic-1.png). I also work in an office, meaning that I drink even more coffee. To get a grip on exactly how many cups a day it actually amounts to, I decided to track it with the help of homeassistant.

## Implementation
To implement the coffee counter we are going to use the new [webhook api](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger) together with a simple `input_number` and a set of `automations`.

### Setup input_number
### Listen to incoming webhook
### Reset at midnight
### Add support for mobile
