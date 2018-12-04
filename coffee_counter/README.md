# Coffee counter

> PSA: This is not really a custom component in homeassistant, but rather a way of achieving the behaviour of a counter that resets daily.

## Background
I am Swedish, so here [it is custom to drink a lot of coffee](https://static.vinepair.com/wp-content/uploads/2017/04/coffee-infographic-1.png). I also work in an office, meaning that I drink even more coffee. To get a grip on exactly how many cups a day it actually amounts to, I decided to track it with the help of homeassistant.

## Implementation
To implement the coffee counter we are going to use the new `webhook api` together with a simple `input_number` and a set of `automations`.

### Setup input_number
We will begin by setting up a simple [input_number](https://www.home-assistant.io/components/input_number/) to serve as our counter. To specify a range, we assume that we drink no less than 0 cups of coffee, and no more than 25 (though to be fair it would be quite extreme to be even near 25 cups per day). Add the following to your `configuration.yaml`:

```yaml
input_number:
  coffee_counter:
    name: Coffee counter
    initial: 0
    min: 0
    max: 25
    step: 1
    mode: box
    unit_of_measurement: cups
```

### Listen to incoming webhook
The [webhook api](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger) was added in homeassistant 0.80 and provides a simple entry point to trigger an automation. You do not need to authenticate your requests, but to make it harder for potential attackers your webhook id should be a long random string. For the sake of clarity we will use a short webhook id, but it should be replaced in a real setup. Add an automation with the following webhook trigger:

```yaml
- alias: Increment coffee counter
  trigger:
    platform: webhook
    webhook_id: coffee
  action:
    service: input_number.set_value
    data_template:
      entity_id: input_number.coffee_counter
      value: "{{ 1 + (states.input_number.coffee_counter.state | int) }}"
```

Now we have set up our homeassistant to trigger each time we do a POST request with Content-Type: application/json to our endpoint at http://example-ha.duckdns.org:8123/api/webhook/coffee.

### Reset at midnight
It is hard to see how many cups of coffee you drink each day if the value never resets. Thus we will add another automation that sets the counter to 0 every day at midnight. Add a new automation with the following content:

```yaml
- alias: Reset coffee counter
  trigger:
    platform: time
    at: '00:00:00'
  action:
    service: input_number.set_value
    data_template:
      entity_id: input_number.coffee_counter
      value: 0
```

### Adding UI support
To give a good overview of our typical coffee consumption we can add a [history graph card](https://www.home-assistant.io/lovelace/history-graph/) showing the past 5 days (note: you have to use lovelace as default UI in homeassistant). In `ui-lovelace.yaml`, add:

```yaml
- type: history-graph
  entities:
    - input_number.coffee_counter
  title: Coffees
  hours_to_show: 120
```

### Add support for mobile
No system is complete without an easy-to-use interface, and it would be a shame if we had to log on to the homeassistant account every time we wanted to log a new cup of coffee. Instead we will be using a mobile app which lets us instantly increment the counter with a click of an icon. I am currently using [HTTP Shortcuts](https://play.google.com/store/apps/details?id=ch.rmy.android.http_shortcuts&hl=en_US) (which is also [open source](https://github.com/Waboodoo/HTTP-Shortcuts)) to generate an icon on my home screen.

To configure HTTP shortcuts, first add a new shortcut named Coffee (or anything else if you want). Make sure that it is sending a POST to your webhook api endpoint:
<p align="center">
  <img src="https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/coffee_counter/shortcut1.png" alt="Shortcut POSTing to your endpoint"/>
</p>

Make sure that the shortcut sends the Content-Type-header with value application/json, and add an empty body that is still valid json (for instance `{}`). I have also chosen to be notified of the response via a toast:
<p align="center">
  <img src="https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/coffee_counter/shortcut2.png" alt="Add Content-Type and body"/>
</p>

Finally, the advanced settings can be left as default:
<p align="center">
  <img src="https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/coffee_counter/shortcut3.png" alt="Add Content-Type and body"/>
</p>

When the shortcut is saved, longpress on the name in the app and choose `Place on home screen` to get a nice clickable icon just a thumb away!
<p align="center">
  <img src="https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/coffee_counter/shortcut4.png" alt="Place icon on home screen!"/>
</p>
