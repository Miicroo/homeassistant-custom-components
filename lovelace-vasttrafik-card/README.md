vasttrafik-card
========================

Styled entities using the Västtrafik theme in a lovelace entities card. All trams and buses are styled using the colours used in Göteborg, so if you are living in Västra Götaland but outside of Göteborg you have to change the css manually.

## Options

| Name | Type | Default | Description
| ---- | ---- | ------- | -----------
| entities | list | **Required** | Entity ids of the Västtrafik sensors
| title | string | Västtrafik | The title of the card

## Examples
```yaml
type: 'custom:vasttrafik-card'
title: 'Valand <-> Hjalmar Brantingsplatsen'
entities:
  - sensor.fran_valand
  - sensor.fran_hjalmar
```

![Example 1](https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/lovelace-vasttrafik-card/resources/1.png)
![Example 2](https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/lovelace-vasttrafik-card/resources/2.png)
![Example 3](https://raw.githubusercontent.com/Miicroo/homeassistant-custom-components/master/lovelace-vasttrafik-card/resources/3.png)

## Tram and bus styles
<div>
	<div style="border-color: black; color: rgb(0, 182, 240); background-color: white; text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">1</div>
	<div style="border-color: rgb(255, 220, 1); color: rgb(0, 182, 240); background-color: rgb(255, 220, 1); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">2</div>
	<div style="border-color: rgb(0, 121, 194); color: white; background-color: rgb(0, 121, 194); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">3</div>
	<div style="border-color: rgb(0, 162, 97); color: white; background-color: rgb(0, 162, 97); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">4</div>
	<div style="border-color: rgb(238, 58, 65); color: white; background-color: rgb(238, 58, 65); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">5</div>
	<div style="border-color: rgb(247, 151, 39); color: rgb(0, 182, 240); background-color: rgb(247, 151, 39); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">6</div>
	<div style="border-color: rgb(156, 85, 6); color: white; background-color: rgb(156, 85, 6); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">7</div>
	<div style="border-color: rgb(165, 68, 153); color: white; background-color: rgb(165, 68, 153); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">8</div>
	<div style="border-color: rgb(111, 206, 244); color: rgb(0, 182, 240); background-color: rgb(111, 206, 244); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">9</div>
	<div style="border-color: rgb(199, 223, 142); color: rgb(0, 182, 240); background-color: rgb(199, 223, 142); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">10</div>
	<div style="border-color: rgb(35, 31, 32); color: white; background-color: rgb(35, 31, 32); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">11</div>
	<div style="border-color: rgb(253, 204, 153); color: rgb(0, 182, 240); background-color: rgb(253, 204, 153); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">13</div>
</div>
<br />
<div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">16</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">17</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">18</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">19</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">25</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">50</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">52</div>
	<div style="border-color: rgb(0, 182, 240); color: rgb(180, 213, 84); background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">60</div>
</div>
<br />
<div>
	<div style="border-color: rgb(0, 182, 240); color: white; background-color: rgb(0, 182, 240); text-align: center; width: 26px; height: 26px;  font-family: arial; display: table-cell; vertical-align: middle;">40</div>
</div>

## In case of errors
1. There is no explicit check to see if the entity id you provide is a Västtrafik-sensor, so you have to check yourself
2. The sensor does not expose from/to, so it is not possible to show that in the card
3. The sensor updates every 2 minutes, so you will sometimes get `-1 minutes` until departure
