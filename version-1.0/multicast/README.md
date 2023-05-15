# LoRaWAN Remote Multicast dashboard
Antoine AUGAGNEUR, USMB 2022

## How to use it ?
* Download the .json file
* Open your NodeRED application
* Click on Import button
* Choose the .json file previously downloaded

## Needed modifications berfore use
- Add YOUR MQTT broker settings in the MQTT nodes.
- Set YOUR topic (to publish on) in the "JSON downlink setup" node.
- Set YOUR topic (to subscribe to) in the "Topic to subscribe" node.
- In the function nodes, there is JS code. Pay attention to the lines with the **"/!\\" symbol**.

## Working philosophy

The dashboard is divided in areas.

### Commands generators
These areas have a command name as title. They generate the payload to send. The user only needs to set the parameters of the command (if needed).
Then the command is created. Finally, the user shall copy the command and past it in the _**Payload**_ field of the **Downlink area**.

### Downlink area
- This area gets 3 parameters:
  - DevEUI
  - Port
  - Payload
- By clicking on the _**SEND**_ button, the tool builds the payload to send via MQTT protocol and send it to the NS.

### Uplink area
- When an uplink is received, basic information about this message is displayed:
  - DevEUI
  - Fcnt
  - Port
  - Payload
- If the uplink is a command in relation with the messaging package, the Uplink area shows:
  - The _**Command type**_ (the name of the command received)
  - The _**Command analysis**_ (the command’s payload is analyzed and human-readable conclusions are displayed)


## In order to use this tool effectively...
- ... check the video demonstrations. Available here: [https://www.youtube.com/watch?v=i_WMjN9jRvk]
- ... check the **_LoRaWAN Advanced Features_** book. Available here: [https://www.univ-smb.fr/lorawan/en/free-book/]

