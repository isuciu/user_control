from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import psycopg2
import paho.mqtt.client as mqtt
import time
import json
import os

app = Flask(__name__)
CORS(app)



def query_db(publisher):
	postgreSQL_select_Query = "select things.* from things things where things.id='"+ str(publisher)+ "'"
	cursor.execute(postgreSQL_select_Query)
	things_records = cursor.fetchall() 
	thing_id =0
	thing_key=0
	if things_records is not None:
		for row in things_records:
			print("Entry = ", row, "\n")
			thing_id=row[0]
			thing_key=row[2]
		return thing_id,thing_key

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		client.connected_flag=True               #Signal connection 
	else:
		client.connected_flag=False
                   #attach function to callback
@app.route('/control/SetSR///sensors/') #when there is no data in influxdb
def initialpage():
	msg = "Waiting for sensor to initialize" #to send its SR, confirming that is up
	return render_template('index.html', message=msg)

@app.route('/control/SetSR/<publisher>/<channel>/sensors/<sensor_name>')
def mainpage(publisher, channel, sensor_name):
	return render_template('index.html', message= "", device = publisher, channel = channel, sensor=sensor_name)


@app.route('/control/CAL///sensors/') #when there is no data in influxdb, SHOULD SHOW ANOTHER PAGE
def calinitialpage():
	msg = "Waiting for sensor to initialize" #to send its SR, confirming that is up
	return render_template('calibration-ph.html', message=msg)

@app.route('/control/CAL/<publisher>/<channel>/sensors/<sensor_name>')
def calpage(publisher, channel, sensor_name):
	if sensor_name == "pH":
		return render_template('calibration-ph.html', message= "", device = publisher, channel = channel, sensor=sensor_name)



@app.route('/control/SendMessage/<selectedvalue>/<publisher>/<channel>/sensors/<sensor_name>')
def sendmessage(selectedvalue, publisher, channel, sensor_name):
	thing_id, thing_key= query_db(publisher)
	if (thing_id != 0 and thing_key != 0):
		mqtt.Client.connected_flag=False
		client = mqtt.Client()    
		client.username_pw_set(thing_id, thing_key)    #set username and password
		client.on_connect=on_connect
		try:
			client.connect(host=mqtt_broker_host, port=mqtt_port)
			client.loop_start()
			topic= "channels/" + str(channel) +  "/control"
			timestamp = time.time()
			data = {"type": "SET_SR", "sensor":sensor_name, "v":selectedvalue, "u":"s", "t":timestamp}
			client.publish(topic,json.dumps(data)) 
			client.disconnect()
			client.loop_stop()
			return "OK"
		except:
			return "Connection to device failed, try again"
	else:
		return "Failed setting SR, try again"


@app.route('/calibration/Set/<db_to_use>/<target_device>/<channel>/sensors/<sensorname>')
def cal_sensor(db_to_use,target_device,channel,sensorname):

	print("sensor:", sensorname) 
	print("db:", db_to_use) 
	print("target dev:", target_device) 
	print("channel:", channel)

	try:
		thing_id, thing_key= query_db(target_device)
		if (thing_id != 0 and thing_key != 0):
			mqtt.Client.connected_flag=False
			client = mqtt.Client()    
			client.username_pw_set(thing_id, thing_key)    #set username and password
			client.on_connect=on_connect
			try:
				client.connect(host=mqtt_broker_host, port=mqtt_port)
				client.loop_start()
				topic= "channels/" + str(channel) +  "/control" #+"/"+'str(thing_id) #make topic more personal
				timestamp = time.time()
				data = {"type": "CAL", "sensor":sensor, "v":db_to_use, "t":timestamp}
				client.publish(topic,json.dumps(data)) 
				client.disconnect()
				client.loop_stop()
				return "OK"
			except:
				return "Connection to device failed, try again"
		else:
			return "Failed calibrating sensor, try again"	
	except:
		return "OK"	

@app.route('/calibration/Check/<target_device>/<channel>/sensors/<sensorname>')
def cal_check(target_device, channel, sensorname):
	return "OK"#"to be implemented"


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
