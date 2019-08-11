customElements.whenDefined('card-tools').then(() => {
  var cardTools = customElements.get('card-tools');

  class GroceryCard extends cardTools.LitElement {
    setConfig(config) {
      if (!config.entity) {
        throw new Error("You must specify an entity!");
      }

      this._config = config;
    }

    render() {
      return cardTools.LitHtml`
        ${this._stateObj}
      `;
    }

    set hass(hass) {
      this._hass = hass;
      this._stateObj = JSON.parse(cardTools.hass.states[this._config.entity].state) || [];

      if (!Array.isArray(this._stateObj)) {
        throw new Error(`The state of ${this._config.entity} is not an array, but ${JSON.stringify(this._stateObj)}. Please use another entity`);
      }

      this._stateObj.sort();
      this.requestUpdate();
    }
  }

  customElements.define('grocery-card', GroceryCard);
});

setTimeout(() => {
  if(customElements.get('card-tools')) return;
  customElements.define('grocery-card', class extends HTMLElement{
    setConfig() { throw new Error('Can\'t find card-tools. See https://github.com/thomasloven/lovelace-card-tools');}
  });
}, 2000);