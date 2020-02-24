# School Attendance System
==================================

## Code style
Standard Python code

[![js-standard-style](https://img.shields.io/badge/code%20style-standard-brightgreen.svg?style=flat)](https://github.com/feross/standard)
# Overview of project

Our project xxx


Quick Start
-----------

To run this project, perform the following steps:

1. `Create Amazon Web Services account.`
2. `Set up EC2 Instance on the Amazon web GUI.`
3. `Set up MySQL AWS RDS on the Amazon web GUI.`
4. `Set up the RPI as shown in the image below`
5. `git clone the repository on the pi.`
6. `cd into IoT_Pi_Code.`
7. `Run the desired program depending on the intended purpose of the pi`

## Supported Python Version
Python2.7

## Installation

To implement AWS and certain RFID functions, the following libraries need to be installed on the Raspberry Pi(s). 

Install Flask library
```bash
sudo pip install flask
```

Install Gevent
```bash
sudo install gevent
```

Install Rpi-lcd
```bash
sudo pip install rpi-lcd
```

Install AWSIoTPythonSDK
```bash
sudo pip install AWSIoTPythonSDK
```

Install Paho-Mqtt
```bash
sudo pip install paho-mqtt
```

Install Numpy
```bash
sudo pip install numpy
```

Install MySQL libraries
```bash
sudo pip install mysql-connector-python
sudo pip install mysql-connector
```

Install SPI
```bash
git clone https://github.com/lthiery/SPI-Py.git && cd SPI-py && python setup.py
```

Install MFRC522
```bash
git clone https://github.com/pimylifeup/MFRC522-python.git && cd MFRC522-python && python setup.py
```

## Authentication

For this project, an Amazon Web Services account has to be set up. For the purposes of this project, an educational account or billing-enabled account can be used. Certificates also need to be set up so that the Raspberry Pis are able to utilise the APIs and can communicate with the Amazon servers.

Simply place the certificate and key files in the "certs" directory, and the code will locate it when it is run.

## Hardware (for 1 setup)
*1 Buzzer
*1 Raspberry Pi
*1 LCD Display Screen
*1 RFID Card reader
*many RFID cards
Note: We have built 3 setups for the purpose of this project: 2 for attendance taking, 1 for assigning RFID cards.

## Picture of actual system
![Picture](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture5.png)
![Picture2](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture6.png)
![Picture3](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture7.png)

# Fritzing
The image shows how to connect the components to the Pi
![Fritzing](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture1.png)

## Storage

With a AWS RDS database created with the web GUI, allow all traffic within the security group. The Raspberry Pi is now able to access the database through the use of a Lambda handler in the code itself.

## System Architecture

The System architecture of our project.

![Architecture](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture2.png)

## Web Application
The following images are screenshots of the running web application.
![Webpage](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture3.png)
![Webpage2](https://github.com/wjlim0/schoolattendancesys/blob/master/iot_pic/Picture4.png)

## Running of project

If the setup is a gate system, run school_ats_gate.py.
If the setup is a RFID assigning system, run assign_rfid.py.

If all the steps above have been completed properly, the software is now up and ready for usage.

## Team Members

* **Muhammad Danial Adam**
* **Lim Wei Jie**
* **Ben Chua**

The group would like to thank Ms Dora Chua for her guidance and support
