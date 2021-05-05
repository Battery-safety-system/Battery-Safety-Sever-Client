# Battery Safety Client Server System

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

This Safety System aims to keep the temperature, voltage of the batteries modules in the specific range. 

- Automatically detect the number of batteries module
- Automatically send the package from client(raspberry) to server(PC)
- Automatically encode and decode the data from Pcan, and store the data to the local repository
- Automatically reconnect the system when the network break down and reconnected.

# Table of contents

1. [Prerequirement](#Prerequirement)
2. [Built With](#BuiltWith)
3. [Content](#Content)
   1. [Client](#Client)
   2. [Server](#Server)
4. [Conclusion](#Conclusion)

# Hardware Prerequirement <a name="Hardware Prerequirement"></a>
Device: Arduino, Modbus, Pcan, Battery, Raspberry, PC, Network Switcher.
![HardWare FlowChart](/images/hardwareDiagram.png)

# Software Prerequirement <a name="Software Prerequirement"></a>

### Pcan(raspberry): 
Before using these code, you need to install peak driver to drive the pcan. <br/>
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
It should Work!!!!
If there is still error, please refer to this [website](https://forum.peak-system.com/viewtopic.php?f=59&t=3381)

### Python Package(python3, raspberry)
Please use **pip3 install** command to install the following python package: can, cantools, pickle, logging, socket, os, time, csv, minimalmodbus in **raspberry**


### IP Address
Please make sure the PC local IP address is 192.168.137.1, or you need to change ip_addr tags both in main/Server/config.properties and main/Client/config.properties.
What's more, make sure ip_port in main/Server/config.properties and main/Client/config.properties are same and not used by other process, or PC cannot connect to the Raspberry.  

**Note**: Before run the code, please use VNC to check if the local network works well. If the PC local ip address is same as ip_addr and can connect to raspberry pi by VNC(). Then it works well. 

### VNC Connection
VNC Connection is very tricky. First, PC need to connect with raspberry by Network Switcer, or connect with each other directly. Then PC will produce a local network ip address, which can be set as 192.168.137.1 <br />
For Raspberry, you need to make sure Wifi is closed, or wifi will affect the connection with PC. Secondly, go to the Network preferences, and choose config as interface and network name as wlanxx. Set ipv4 as 192.168.137.xx(as you like), then click Apply. Thirdly, disconnect and reconnect the ethernet port of Raspberry and make sure VNC recommended ip addresses has 192.169.137.xx(of course, before all of these, you must open VNC PORT). 

### Arduino(raspberry)
Download Arduino IDE in Linux:
	[simulator link](https://www.tinkercad.com/things/bGWVayF3Z1h-start-simulating/editel?lessonid=EHD2303J3YPUS5Z&projectid=OIYJ88OJ3OPN3EA&collectionid=OIYJ88OJ3OPN3EA&tenant=circuits#/lesson-viewer)
or	

$ sudo apt-get install arduino<br />

Then upload main/Arduino/Arduino.ino to the Arduino IDE. 

## Built <a name="BuiltWith"></a>

* Get the Code: 

  $ git clone https://github.com/Battery-safety-system/Battery-Safety-Sever-Client.git
  $ git checkout TestCode
  $ cd Battery-Safety-Sever-Client


* Run Command: <br />
 
 
    For PC: 
    
        $ cd ./main/Server
        $ python3 server-version5.py 
    
    
    
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

Please check "ArduinoHandler" in /main/Client/config.properties. You can change Pump, Fan, Relay Pin numbers if you want. Also if the port is not right, you can also change "USB_Port" name. 

### 2. PCAN Model
The module is implemented in main/Client/PcanConnection.py. You can set the value of "CMA_Voltage_High_Dangerous", "CMA_Voltage_Low_Dangerous", "CMA_Voltage_High_Warning", "CMA_Voltage_Low_Warning", "CMA_Temp_Dangerous", "CMA_Temp_Warning", "CMA_Temp_security", "Cell_Voltage_High_Warning", "Cell_Voltage_Low_Warning", "Cell_Voltage_High_Dangerous", "Cell_Voltage_Low_Dangerous" from "PcanConnection" in main/Client/config.properties to control dangerous and warning level. What's more, you can also set "cellVoltageNum" to control how many cell voltages you can get from one battery. 
<br /> And also, if the Pcan doesn't connect to port can0, you can change the name of "channel". 

### 3. Modbus Model
Here, if you want to change the Modbus limitation, you need to change the values of  "max_vol", "min_vol", "max_crt", "max_dis_crt", "max_power". <br /> What's more, warning and dangerous level depend on "volLowWarning", "volHighWarning", "volHighDangerous", "volLowDangerous".

## Collected Data(Result) 

For Server: 
* the collected datas will be put in main/Server/Battery-System-database/Battery-System MM-yyyy/log-Battery-System dd-MM-yyyy-hh-mm-ss.log files
it will includes the data, time and all the datas we get from Arduino, Pcan, Modbus.

For Client:
* the collected datas will be put in main/Client/Battery-System-database/Battery-System MM-yyyy/log-Battery-System dd-MM-yyyy-hh-mm-ss.log files
The contents are same as Server. 





## Content  <a name="Content"></a>

### 1. Client <a name="Client"></a>
Here is the Client logic Diagram:
![Client logic Diagram](/images/Client_Flow_Chart.png)

### 2. Server <a name="Server"></a>
Here is the Sever logic Diagram:
Flow Chart

### 3. Warning and Dangerous Level Logic
Here is the Warning and Dangerous Level Logic Diagram: 
![warning and dangerous diagram](/images/warning_dangerous_level_operation.png)


## Conclusion <a name="Conclusion"></a>

## Materials:

modbus manual:

modbus diagram:  [Flow Chart.drawio - Google Drive](https://drive.google.com/file/d/1NNy5NgrcA9PDrtHOePHVPRTp49nq5HQm/view?usp=sharing) Please using drawio app to open it

Modbus datasheet: [MODBUS Programming Manual_100-PBJ1226-PAA_V1.0 (1).xlsx - Google Drive](https://drive.google.com/file/d/1G2-0vgNjH8J68ZtONMKIYocuhhOb2BkP/view?usp=sharing)

## Tools:

 Kvaser Database Editor read dbc: [https://www.kvaser.com/download/](https://urldefense.com/v3/__https://www.kvaser.com/download/__;!!Mih3wA!ReAZfpD6fU6_pbI5hwYomFi2ZcN52VkdjdvT4XQDX1vOkkkJbpPjh9JoaB_i9I2kig$)
 
 ## Possible Error: 
![Possible Error](/images/OperatorException.png) 

## Note:
1. For Raspberry pi, you cannot keep Ethernet and wifi connection together, if you connect Wifi, raspberry pi cannot connect to PC by ethernet. 
2. if the status is very emergent, and you want to close the modbus and battery right now. Please run Battery-Safety-Sever-Client/main/smallControlModule/closeModbus.py and InitArduinoDevice.py  
