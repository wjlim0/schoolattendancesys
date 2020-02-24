from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime
from gpiozero import Buzzer
from rpi_lcd import LCD 
from time import sleep

import RPi.GPIO as GPIO
import MFRC522
import signal
import json
import sys

#Gate Number
gate_number = "Gate2"
scanning = True

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
	topic = str(message.topic)
	if (str(message.topic) == str("school/attendance/"+gate_number+"/status")):
		payloadData = json.loads(message.payload)
		message = str(payloadData["Message"])
		GPIO.output(buzzer, GPIO.HIGH)
		GPIO.output(buzzer, GPIO.LOW)
		print(topic + ": " + message)
		lcdWrite(message)
		sleep(1)
		lcd.clear()
	elif (str(message.topic) == str("school/announcement")):
		payloadData = json.loads(message.payload)
		message = str(payloadData["announcement"])
		print(topic + ": " + message)
		lcdWrite(message)
	else:
		payloadData = json.loads(message.payload)
		message = str(payloadData["RFID"])
		GPIO.output(buzzer, GPIO.HIGH)
		GPIO.output(buzzer, GPIO.LOW)
		print(topic + ": " + message)
		lcdWrite(message)
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
my_rpi = AWSIoTMQTTClient(gate_number)
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("school/attendance/"+gate_number+"/#", 1, customCallback)

uid = None
prev_uid = None

#  ===================================================================
#  Main
#  ===================================================================

if __name__ == "__main__":
	
	# Publish to the same topic in a loop forever
	print("Scan card to record Attendance ...")
	lcd.clear()
	lcd.text("Scan card for Attendance ..." , 1)

	while scanning:

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
					"Location": str(gate_number),
					"RFID": str(uid)
				})
				
				my_rpi.publish("school/attendance/"+gate_number+"/tap", payload, 1)
				lcd.text("Scan card for Attendance ..." , 1)
