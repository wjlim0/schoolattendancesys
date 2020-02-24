from flask import Flask, render_template, jsonify, request,Response,redirect
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

import mysql.connector
import sys

import json
import numpy
import datetime
import decimal

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
#from rpi_lcd import LCD 

gevent.monkey.patch_all()

# For publishing stuff to AWS IoT
host = "a3vpe3hrbnbtvp-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "certs/rootca.pem"
certificatePath = "certs/certificate.pem.crt"
privateKeyPath = "certs/private.pem.key"

#Connect and subscribe to AWS Iot
my_rpi = AWSIoTMQTTClient("Webserver")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()

# For connecting to the AWS RDS
host='iot-ca2-database.chrbatadpqas.us-east-1.rds.amazonaws.com'
user='admin'
password='iotpassword'
database='iot_ca2';
			
class GenericEncoder(json.JSONEncoder):
	
	def default(self, obj):  
		if isinstance(obj, numpy.generic):
			return numpy.asscalar(obj) 
		elif isinstance(obj, datetime.datetime):  
			return obj.strftime('%Y-%m-%d %H:%M:%S') 
		elif isinstance(obj, decimal.Decimal):
			return float(obj)
		else:  
			return json.JSONEncoder.default(self, obj) 

def data_to_json(data):
	json_data = json.dumps(data,cls=GenericEncoder)
	return json_data

def connect_to_mysql(host,user,password,database):
	try:
		cnx = mysql.connector.connect(host=host,user=user,password=password,database=database)

		cursor = cnx.cursor()
		print("Successfully connected to database!")

		return cnx,cursor

	except:
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])

		return None

def fetch_fromdb_as_json(cnx,cursor,sql):
	
	try:
		cursor.execute(sql)
		row_headers=[x[0] for x in cursor.description] 
		results = cursor.fetchall()
		data = []
		for result in results:
			data.append(dict(zip(row_headers,result)))
		
		data_reversed = data[::-1]

		data = {'data':data_reversed}

		return data_to_json(data)

	except:
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])
		return None
							

app = Flask(__name__)

@app.route("/")
def display_main_page():
	return render_template('index.html')

@app.route("/api/SetAnnouncement",methods = ['POST', 'GET'])
def api_set_announcemnet():
	if request.method == 'POST':

		# Create an object of the class LCD
		#lcd = LCD()
		form_data = request.form #get data from form
		Msg = form_data['msg']

		payload = json.dumps({
			"announcement": str(Msg)     
		})

		my_rpi.publish("school/announcement", payload, 1)
		#lcd.text(Msg , 1)
		return redirect("/")

# Real-time data API
@app.route("/api/getTodaysAttendance",methods = ['POST', 'GET'])
def api_get_realtime_data():
	if request.method == 'POST':
		try:
			#host='localhost'; user='SchoolAdmin'; password='root'; database='School_ATS_System';
			sql = "SELECT COUNT(`SchAttendance_ID`) as 'NumberOfStudent' FROM SchoolAttendance WHERE date(Tap_In)= curdate() union SELECT COUNT(`Student_ID`) as 'NumberOfStudent' FROM Student "
			cnx,cursor = connect_to_mysql(host,user,password,database)

			json_data = fetch_fromdb_as_json(cnx,cursor,sql)
			loaded_r = json.loads(json_data)
			
			data = {'chart_data': loaded_r, 'title': "Today's Attendance"}
			
			return jsonify(data)
		except:
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])

@app.route("/api/getLatestArrivedStudent",methods = ['POST', 'GET'])
def api_get_realtime_data_2():
	if request.method == 'POST':
		try:
			#host='localhost'; user='SchoolAdmin'; password='root'; database='School_ATS_System';
			sql = "SELECT CONCAT(First_Name, ' ' ,Last_Name) as Full_Name FROM Student, SchoolAttendance WHERE SchoolAttendance.Student_ID = Student.Student_ID AND date(Tap_In)= curdate() ORDER BY Tap_in ASC"
			cnx,cursor = connect_to_mysql(host,user,password,database)

			json_data = fetch_fromdb_as_json(cnx,cursor,sql)
			loaded_r = json.loads(json_data)
			
			data = {'chart_data': loaded_r, 'title': "Latest Student to Arrive"}
			
			return jsonify(data)
		except:
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			
# Historical data API
@app.route("/api/getPastAttendance",methods = ['POST', 'GET'])
def api_get_historical_data():
	if request.method == 'POST':
		try:
			#host='localhost'; user='SchoolAdmin'; password='root'; database='School_ATS_System';
			sql = "SELECT COUNT(`SchAttendance_ID`) as 'NumberOfStudent', `Tap_In` FROM `SchoolAttendance` WHERE DATE(Tap_In) BETWEEN DATE(NOW()) - INTERVAL 7 DAY AND DATE(NOW()) GROUP BY Date(Tap_In)"
			cnx,cursor = connect_to_mysql(host,user,password,database)
			
			json_data = fetch_fromdb_as_json(cnx,cursor,sql)
			loaded_r = json.loads(json_data)
			data = {'chart_data': loaded_r, 'title': "Historical Data"}
			return jsonify(data)

		except:
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])

#from rpi_lcd import LCD 
#lcd = LCD()


if __name__ == '__main__':
	try:
		http_server = WSGIServer(('0.0.0.0', 8001), app)
		app.debug = True
		print('Server waiting for requests')
		http_server.serve_forever()

	except:
		print(sys.exec_info()[0])
		print(sys.exec_info()[1])
