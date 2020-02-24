from __future__ import print_function

import json
import boto3
import pymysql

print('Loading function')

def lambda_handler(event, context):
    try:
        # Parse the JSON message
        inputMsg = str(event['Message'])
        
        # Print the parsed JSON message to the console. You can view this text in the Monitoring tab in the AWS Lambda console or in the Amazon CloudWatch Logs console.
        print('Received event: ' + inputMsg)
        
        # Create an IoT Core Data client to publish messages back to Raspberry Pis
        iot_mqtt_pub = boto3.client('iot-data')
        
        host='iot-ca2-database.chrbatadpqas.us-east-1.rds.amazonaws.com'
        user='admin'
        password='iotpassword'
        database='iot_ca2'

        cnx = pymysql.connect(host=host,user=user,password=password,database=database)
        cursor = cnx.cursor()
        print("Successfully connected to database!")
        
        if inputMsg == "Get List of Student records":    
            sql = "SELECT Student_ID, CONCAT(First_Name, ' ' ,Last_Name) as Full_Name, RFID_Tag FROM Student"
            cursor.execute(sql)
            StudentList = cursor.fetchall()

            print(StudentList)
            
            print("Student List Printed.")
            print("MQTT Response:")
            mqtt_response = iot_mqtt_pub.publish(
                topic='school/students/showList',
                qos=1,
                payload=json.dumps({
                    "Student List": StudentList
                })
            )
            print(mqtt_response)

        print('End of function')

    except Exception as e:
        print("ERROR:")
        print(e)

    finally:
        cursor.close()
        cnx.close()