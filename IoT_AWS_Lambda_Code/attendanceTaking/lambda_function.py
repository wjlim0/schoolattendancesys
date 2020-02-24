from __future__ import print_function
  
import json
import boto3

import pymysql
import pytz
from datetime import datetime
  
print('Loading function')
  
def lambda_handler(event, context):
    try:
        # Parse the JSON message
        uid = event['RFID']
        gate_number = event['Location']
        
        # Initialise the variables first
        sns_msg = ''
        remarks = ''
        mqtt_response_msg = ''
        
        # Set time-zone
        tz = pytz.timezone('Asia/Singapore')
      
        # Print the parsed JSON message to the console. You can view this text in the Monitoring tab in the AWS Lambda console or in the Amazon CloudWatch Logs console.
        print('Received event: ', uid)
        
        # Create an SNS client
        sns = boto3.client('sns')
        
        # Create an IoT Core Data client to publish messages back to Raspberry Pis
        iot_mqtt_pub = boto3.client('iot-data')

        host='iot-ca2-database.chrbatadpqas.us-east-1.rds.amazonaws.com'
        user='admin'
        password='iotpassword'
        database='iot_ca2'

        cnx = pymysql.connect(host=host,user=user,password=password,database=database)
        cursor = cnx.cursor()
        print("Successfully connected to database!")

        sql = "SELECT Student_ID, CONCAT(First_Name, ' ' ,Last_Name) as Full_Name FROM Student WHERE RFID_Tag=%(RFID_Tag)s"
        cursor.execute(sql, {'RFID_Tag' : str(uid)})
        StudentDetails = cursor.fetchall()

        #Have a student with the following RFID Tag
        if cursor.rowcount == 1:
            sql = "SELECT * FROM SchoolAttendance WHERE Student_ID=%(Student_ID)s and date(Tap_In)= curdate()"
            cursor.execute(sql, {'Student_ID' : str(StudentDetails[0][0])})
            TodaysAttendance = cursor.fetchall()

            # Check if the user have already clock in for that day
            # If equals to zero, means user is tapping in
            if cursor.rowcount == 0:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time_datetime_obj = datetime.now(tz).astimezone(tz).replace(tzinfo=None)
                timenow = time_datetime_obj.strftime('%H:%M:%S')
                SchoolAssembly_Time = datetime.now().replace(hour=7, minute=30, second=0, microsecond=0).strftime('%H:%M:%S')

                print(timenow)
                print(str(SchoolAssembly_Time))

                if (timenow <= str(SchoolAssembly_Time)):
                    remarks = "on time"
                    mqtt_response_msg = "Card detected! You are on time."
                else:
                    remarks = "late"
                    mqtt_response_msg = "Card detected! You are late."

                sql = "INSERT SchoolAttendance (Student_ID, Remarks, RFID_Tag, Tap_In ) VALUES (%s,%s,%s,%s)"
                values = (str(StudentDetails[0][0]), remarks, str(uid), timestamp )
                cursor.execute(sql, values)
                cnx.commit()

                sns_msg = "Student Arrival Time\nStudent Name: " + str(StudentDetails[0][1])\
                            + "\nClocked in at: " + str(timenow) + " (" + remarks + ")"
                print('Message to parent:')
                print(sns_msg)

            # If equals to one, means user is tapping out
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time_datetime_obj = datetime.now(tz).astimezone(tz).replace(tzinfo=None)
                timenow = time_datetime_obj.strftime('%H:%M:%S')

                sql = "UPDATE SchoolAttendance SET Tap_Out= %s where Student_ID=%s and date(Tap_In)= curdate()"
                values = (timestamp, str(StudentDetails[0][0]))
                cursor.execute(sql, values)
                cnx.commit()
                
                mqtt_response_msg = "Card detected! You tapped out."
                
                sns_msg = "Student left school\nStudent Name: " + str(StudentDetails[0][1])\
                            + "\nLeft at: " + str(timenow)
                print('Message to parent:')
                print(sns_msg)
            
            print("SNS Response:")
            # Publish a message to the specified topic
            sns_response = sns.publish (
                TopicArn = 'arn:aws:sns:us-east-1:458807346986:school',
                Message = sns_msg
            )
            print(sns_response)
            
        else:
            mqtt_response_msg = "Card not in used. Please try another card."

        mqtt_response = iot_mqtt_pub.publish(
            topic='school/attendance/' + gate_number + '/status',
            qos=1,
            payload=json.dumps({
                "Location": str(gate_number),
				"Message": mqtt_response_msg
            })
        )
        print(mqtt_response)

        print('End of function')

    finally:
        cursor.close()
        cnx.close()