# Battery Safety Client Server System


[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

This Safety System aims to keep the temperature, voltage of the batteries modules in the specific range. 

  - Automatically detect the number of batteries module
  - Automatically send the package from client(raspberry) to server(PC)
  - Automatically encode and decode the data from Pcan, and store the data to the local repository
  - Automatically reconnect the system when the network break down and reconnected.

# Table of contents
1. [Built With](#introduction)
2. [Usage](#Usage)
    1. [Sub paragraph](#module1)
    2. 
3. [Conclusion](#Conclusion)

# Install
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


## Built With <a name="introduction"></a>
<!---
your comment goes here
and here
-->

* Language: Python3 <br />
* Python Package: RPi.GPIO, can, cantools, pickle, logging, socket, os, time, csv <br />
* Install tools:
```console
	$ pip install xxx
```
* Run Command: <br />

	For PC: 
    
    	$ python3 Server.py 
    

	For Raspberry pi
		
        $ python3 Client.py 



## Content Explanation 

## Conclusion <a name="Conclusion"></a>