# Battery Safety Client Server System

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

This Safety System aims to keep the temperature, voltage of the batteries modules in the specific range. 

- Automatically detect the number of batteries module
- Automatically send the package from client(raspberry) to server(PC)
- Automatically encode and decode the data from Pcan, and store the data to the local repository
- Automatically reconnect the system when the network break down and reconnected.

# Table of contents

1. [Install](#Install)
2. [Built With](#BuiltWith)
3. [Content](#Content)
   1. [Client](#Client)
   2. [Server](#Server)
4. [Conclusion](#Conclusion)

# Install <a name="Install"></a>

Before we use these code, we need to install peak driver to drive the pcan. <br/>
Installation step: <br />

1. First, install the driving package in the [peak website](https://www.peak-system.com/fileadmin/media/linux/files/peak-linux-driver-8.11.0.tar.gz) 
2. Follow the Read.me to install the driver
   
   ```console
    $ cd peak-linux-driver-x.y.z
    $ sudo make install
   ```
3. Then open the pcan and set the bitrate, the modbus can work now !!
   
   ```console
    $ sudo modprobe pcan
    $ sudo ip link set can0 up type can bitrate 500000
   ```

If there is still error, please refer to this [website](https://forum.peak-system.com/viewtopic.php?f=59&t=3381)

## Built With <a name="BuiltWith"></a>

<!---
your comment goes here
and here
-->

* Language: Python3 <br />

* Python Package: RPi.GPIO, can, cantools, pickle, logging, socket, os, time, csv <br />

* Install tools:
  
  ```console
    $ pip3 install xxx
  ```

* Run Command: <br />
 
 
    For PC: 
        $ cd ./main/Server
        $ python3 Server.py 
    
    
    
    For Raspberry pi

        $ cd ./main/Client
        $ bash start_client.sh
        
      
    ***Note: Please run PC command before Raspberry pi***
    
* Change the Schedule: <br />
   1. Open the ./main/Client/config.properties <br />
   2. Choose the ControlMode (1 means currentControlMode; 2 means powerControlMode) <br />
   3. Then choose controlValueFile and enter the file name <br />
   4. Save and close config.properties <br />
   5. Jump to Run Command Part and run code <br />
   
   
## Module <a name="Module"></a>

### 1. Arduino Model

Please check ArduinoHandler in /main/Client/config.properties. We can change Pump, Fan, Relay Pin numbers if we want. Also if the port is not right, you can also change USB_Port name. 

### 2. PCAN Model
You can change the value of CMA_Voltage, CMA_Temp, Cell_Voltage warning and dangerous value to control the system. <br /> And also, if the Pcan doesn't connect to port can0, you can change the name of channel. 

### 3. Modbus Model
Here, if we want to change the Modbus limitation, we need to change the values of  "max_vol", "min_vol", "max_crt", "max_dis_crt", "max_power". <br /> What's more, warning and dangerous level depend on "volLowWarning", "volHighWarning", "volHighDangerous", "volLowDangerous".

## Content  <a name="Content"></a>

### 1. Client <a name="Client"></a>


#### 

### 2. Server <a name="Server"></a>

Flow Chart

## Conclusion <a name="Conclusion"></a>

## Materials:

modbus manual:

modbus diagram:  [Flow Chart.drawio - Google Drive](https://drive.google.com/file/d/1NNy5NgrcA9PDrtHOePHVPRTp49nq5HQm/view?usp=sharing) Please using drawio app to open it

Modbus datasheet: [MODBUS Programming Manual_100-PBJ1226-PAA_V1.0 (1).xlsx - Google Drive](https://drive.google.com/file/d/1G2-0vgNjH8J68ZtONMKIYocuhhOb2BkP/view?usp=sharing)

## Tools:

 Kvaser Database Editor read dbc: [https://www.kvaser.com/download/](https://urldefense.com/v3/__https://www.kvaser.com/download/__;!!Mih3wA!ReAZfpD6fU6_pbI5hwYomFi2ZcN52VkdjdvT4XQDX1vOkkkJbpPjh9JoaB_i9I2kig$)
