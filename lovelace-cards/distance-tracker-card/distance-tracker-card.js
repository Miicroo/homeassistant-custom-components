class DistanceTrackerCard extends Polymer.Element {

  static get template() {
    return Polymer.html`
      <link type="text/css" rel="stylesheet" href="/local/custom_ui/distance-tracker-card/distance-tracker-card.css"></link>
      <ha-card>
        <div class="header">
            [[_title]]
        </div>
        <div class="content">
        </div>
      </ha-card>
    `
  }

  setConfig(config) {
    if (!config.entities || config.entities.length === 0) {
      throw new Error("Specify at least one entity!");
    }
    this._title = config.title || 'Distance tracker';
    this._entities = config.entities;
    this._distanceObjects = config.include_predefined_distance_objects ? this._loadDistances() : [];
    this._distanceObjects = this._distanceObjects.concat(config.distances || []);
  }

  _loadDistances() {
    return [
      {
        "name": "Longest street in the world (Yonge street, Toronto Canada)",
        "distance": 1896,
        "icon": "mdi:road-variant",
        "unit_of_measurement": "km"
      },
      {
        "name": "The Great Wall of China",
        "distance": 6430,
        "icon": "mdi:wall",
        "unit_of_measurement": "km"
      },
      {
        "name": "Diameter of the Moon",
        "distance": 3476,
        "icon": "mdi:moon",
        "unit_of_measurement": "km"
      },
      {
        "name": "All of New Yorks's shorelines",
        "distance": 920,
        "icon": "mdi-waves",
        "unit_of_measurement": "km"
      },
      {
        "name": "Diameter of Earth",
        "distance": 12756,
        "icon": "mdi:earth",
        "unit_of_measurement": "km"
      },
      {
        "name": "Kungsleden",
        "distance": 425,
        "icon": "mdi:pine-tree",
        "unit_of_measurement": "km"
      },
      {
        "name": "Circumference of Earth",
        "distance": 40075,
        "icon": "mdi:earth",
        "unit_of_measurement": "km"
      }
    ];
  }

  set hass(hass) {
    this._hass = hass;
    this.update();
  }

  update() {
    if(!this.shadowRoot) {
      return;
    }

    const entitiesAsUi = this._entities
                                     .map(id => this.createRow(id))
                                     .reduce((all, current) => all + current, '');

    const contentElement = this.shadowRoot.querySelector(".content");
    contentElement.innerHTML = entitiesAsUi;
  }

  createRow(entityId) {
    if (!(entityId in this._hass.states)) {
       return;
    }

    const entity = this._hass.states[entityId];
    const attributes = entity.attributes;
    const name = attributes.friendly_name;
    const distance = entity.state;
    const unit = attributes.unit_of_measurement;

    const sortedDistances = this.getDistancesSortedByUnit(unit);
    const firstLargerIndex = sortedDistances.findIndex(d => d.distance > distance);

    const hasPassedAny = firstLargerIndex > 0;
    let lastPassed = undefined;
    if(hasPassedAny) {
    	lastPassed = sortedDistances[firstLargerIndex - 1];
    }

    const nextToPass = sortedDistances[firstLargerIndex];
    return `<div>
              <h3>${name}</h3>
              <p>Distance: ${distance} ${unit}</p>` +
              (hasPassedAny ?
                `<p> You passed ${lastPassed.name} ${distance-lastPassed.distance} ${unit}s ago <ha-icon icon="${lastPassed.icon}"></ha-icon></p>` :
                ''
              ) +
            `
            <p>Next to pass is ${nextToPass.name} in ${nextToPass.distance-distance} ${unit}s <ha-icon icon="${nextToPass.icon}"></ha-icon></p>
            </div>`;

  }

  getDistancesSortedByUnit(unit) {
  	return this._distanceObjects.slice(0)
  	           .map(distanceObj => 
  	               distanceObj.unit_of_measurement === unit ? 
  	               distanceObj :
  	               this.convertDistanceObjectToUnit(distanceObj, unit)
  	           ).sort((a,b) => a.distance-b.distance);
  }

  convertDistanceObjectToUnit(distanceObj, toUnit) {
    const conversions = [];
    conversions['m_km'] = function(value) { value/1000 };
    conversions['km_m'] = function(value) { value*1000 };
    conversions['mi_km'] = function(value) { value*1.609 };
    conversions['km_mi'] = function(value) { value/1.609 };
    conversions['mi_m'] = function(value) { value*1609 };
    conversions['m_mi'] = function(value) { value/1609 };

    const conversionFunction = conversions[`${distanceObj.unit_of_measurement}_${toUnit}`];

    let simpleObjClone = JSON.parse(JSON.stringify(distanceObj));
    simpleObjClone.distance = conversionFunction(distanceObj.distance);
    simpleObjClone.unit_of_measurement = unit;

    return simpleObjClone;
  }
}
customElements.define('distance-tracker-card', DistanceTrackerCard);

