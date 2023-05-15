# LoRaWAN Fragmented Data Block Transport dashboard
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

### DataFragment auto
This area is a special one.

#### DataFragment auto information
- It is possible to launch a fragmentation session thanks to this area.
Then the dashboard will send a fragment automatically each 7 seconds (540 msg/hour).
Why 540 msg/hour? This sending period is authorized only if:
  - Your NS processes downlinks in the **869.525MHz channel**. There is a 10% (not 1%!) duty-cycle.
  - The SF used is **SF9** (DR3).
  - The payload size is **115-bytes** (it is the maximum). Then, the time on air is 65,6 sec.
- To be noted:
  - If you do not respect these sending parameters, please adjust the **7-seconds period** (var INTERVAL) in the _**Get data & Display**_ function node.
  - If your payload is 115-bytes long, it means the fragment size you can send is **112-bytes** long (115-bytes = 3-bytes header of DataFragment command + 112-bytes fragment)
  - Depending on the NS you use, a policy could affect your sending period (e.i.: TTN fair access policy)

#### How to use the Data Fragment auto?
  - Upload your file containing the fragments to send. **Only .csv files are accepted**.
To generate a .csv file containing the fragments of your firmware, see the Fragmentation tool available here: [ https://github.com/AntoineAugagneur/Tools ]
  - Check the _**Upload information**_ field to see if the upload process imported the right number of fragments.
  - Fill the DevEUI and Session (according to the Session number you’ve programmed in your end-device) fields. Finally, setup the session.
  - When the session is ready for launch, click on _**START**_ button. The progression is displayed on a percentage bar.


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

