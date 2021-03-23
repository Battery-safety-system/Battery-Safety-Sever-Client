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
3. [Conclusion](#Conclusion)

# Install <a name="Install"></a>
Before we use these code, we need to install peak driver to drive the pcan. <br/>
Installation step: <br />
1. First, install the driving package in the [peak website](https://www.peak-system.com/fileadmin/media/linux/files/peak-linux-driver-8.11.0.tar.gz) 
2. Follow the Read.me to install the driver
```console
	$ sudo apt update
	$ sudo apt install build-essential
	$ sudo apt-get install manpages-dev
	$ sudo apt-get install make
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
	$ pip install xxx
	$ pip install python-can
```
* Run Command: <br />

	For PC: 
    
    	$ python3 Server.py 
    

	For Raspberry pi
		
        $ python3 Client.py 

* Download Arduino
	[simulator link](https://www.tinkercad.com/things/bGWVayF3Z1h-start-simulating/editel?lessonid=EHD2303J3YPUS5Z&projectid=OIYJ88OJ3OPN3EA&collectionid=OIYJ88OJ3OPN3EA&tenant=circuits#/lesson-viewer)
	$ sudo apt-get install arduino

## Content  <a name="Content"></a>
### 1. Client <a name="Client"></a>
Flow Chart
	

### 2. Server <a name="Server"></a>
Flow Chart

## Error 
### 1. When run sudo apt-install build-essential: get Waiting for cache lock:
https://stackoverflow.com/questions/62126195/getting-error-waiting-for-cache-lock-could-not-get-lock-var-lib-dpkg-lock-fro
https://itsfoss.com/could-not-get-lock-error/


## Modbus ref:
### function code: https://blog.softwaretoolbox.com/opc-modbus-function-codes
### MinimalModbus API: https://minimalmodbus.readthedocs.io/en/stable/apiminimalmodbus.html

## Conclusion <a name="Conclusion"></a>
