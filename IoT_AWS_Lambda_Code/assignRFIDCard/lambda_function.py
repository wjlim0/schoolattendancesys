from __future__ import print_function
  
import json
import boto3
import pymysql

print('Loading function')

def lambda_handler(event, context):
    try:
        # Parse the JSON message
        uid = event['RFID']
        StudentID = int(event['StudentID'])
      
        # Print the parsed JSON message to the console. You can view this text in the Monitoring tab in the AWS Lambda console or in the Amazon CloudWatch Logs console.
        print('Received event: ', uid)
        
        # Create an IoT Core Data client to publish messages back to Raspberry Pis
        iot_mqtt_pub = boto3.client('iot-data')

        mqtt_response_msg = ''
        
        host='iot-ca2-database.chrbatadpqas.us-east-1.rds.amazonaws.com'
        user='admin'
        password='iotpassword'
        database='iot_ca2'

        cnx = pymysql.connect(host=host,user=user,password=password,database=database)
        cursor = cnx.cursor()
        print("Successfully connected to database!")
        
        sql = "SELECT Student_ID FROM Student WHERE RFID_Tag=%(RFID_Tag)s"
        cursor.execute(sql, {'RFID_Tag' : str(uid)})
        RFID_Tag = cursor.fetchall()

        if cursor.rowcount ==0:
            print("\n New card detected! UID of card is {} ".format(uid))

            sql = "UPDATE Student SET RFID_Tag=%s where Student_ID=%s"
            values = (str(uid), StudentID)
            cursor.execute(sql, values)
            cnx.commit()

            mqtt_response_msg = 'The card have been assigned to the student.'

        else:
            mqtt_response_msg = 'Card with the following RFID Tag '+uid+' have already been used. Please try another card.'
        
        print("MQTT Response:")
        mqtt_response = iot_mqtt_pub.publish(
            topic='school/card/status',
            qos=1,
            payload=json.dumps({
                "Message": mqtt_response_msg
            })
        )
        print(mqtt_response)

        print('End of function')

    finally:
        cursor.close()
        cnx.close()