from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime
from tabulate import tabulate
from gpiozero import Buzzer
from rpi_lcd import LCD 
from time import sleep

import RPi.GPIO as GPIO
import MFRC522
import signal
import json
import sys

#Location
location = "AdminOffice"
scanning = True
valid = True
exist = False
StudentList = ""

#Create Buzzer
buzzer = 5
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, GPIO.LOW)

#Create LCD
lcd = LCD()

#Create RFID
mfrc522 = MFRC522.MFRC522()

def lcdWrite(message):

	lcd.text(message, 1)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
	global scanning
	print("Ctrl+C captured, ending read.")
	scanning = False
	GPIO.cleanup()
	lcd.clear()

def customCallback(client, userdata, message):
	global gate_number
	global StudentList
	msgTopic = str(message.topic)
	if (str(message.topic) == str("school/card/status")):
		payloadData = json.loads(message.payload)
		message = str(payloadData["Message"])
		GPIO.output(buzzer, GPIO.HIGH)
		GPIO.output(buzzer, GPIO.LOW)
		print(msgTopic + ": " + str(message))
		lcdWrite(str(message))
		sleep(1)
		lcd.clear()
	
	elif (str(message.topic) == str("school/students/showList")):
		payloadData = json.loads(message.payload)
		StudentList = payloadData["Student List"]
		print(tabulate(StudentList, headers=['Student_ID', 'Full Name', 'RFID_Tag'], tablefmt='psql'))
	
	else:
		payloadData = json.loads(message.payload)
		message = str(payloadData["RFID"])
		GPIO.output(buzzer, GPIO.HIGH)
		GPIO.output(buzzer, GPIO.LOW)
		print(msgTopic + ": " + str(message))
		lcdWrite(str(message))
		sleep(1)
		lcd.clear()

#AWS IoT Setup
host = "a3vpe3hrbnbtvp-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "certs/rootca.pem"
certificatePath = "certs/certificate.pem.crt"
privateKeyPath = "certs/private.pem.key"

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

#Connect and subscribe to AWS Iot
my_rpi = AWSIoTMQTTClient(location)
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("school/students/showList", 1, customCallback)
my_rpi.subscribe("school/card/#", 1, customCallback)

uid = None
prev_uid = None

#  ===================================================================
#  Main
#  ===================================================================
				
if __name__ == "__main__":
	
	#Publish Message to get a list of students
	payload = json.dumps({
			"Message": "Get List of Student records"
		})

	print("Waiting for Student Records...")
	my_rpi.publish("school/students/getList", payload, 1)
	sleep(5)
	
	while valid:

		try: #Using Exceptions For Validation
			StudentIDStr = input("Enter the Student ID of the Student to be assigned an RFID Tag: ") #Will Take Input From User
			StudentID = int(StudentIDStr)
			for Student in StudentList:
				if int(Student[0]) == StudentID:
					exist = True
					break
				
			if not exist:
				print("\n Student ID doesn't exist \n ")
			else:
				break
		
		except:
			print("\n Student ID must be an Integer \n ") #Error Message
	
	while scanning:
		#print("Scan card to register ...")
		lcd.text("Scan card to register ..." , 1)
		
		# Scan for cards
		(status,TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)
		
		# If a card is found
		if status == mfrc522.MI_OK:
			# Get the UID of the card
			(status,uid) = mfrc522.MFRC522_Anticoll()

			if uid!=prev_uid:
				prev_uid = uid
				print("Card detected! UID of card is {}".format(uid))

				payload = json.dumps({
					"RFID": str(uid),
					"StudentID": StudentID
				})
				
				my_rpi.publish("school/card/assign", payload, 1)
				sleep(5)
				lcd.text("Scan card to register ..." , 1)
