from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import psycopg2
import paho.mqtt.client as mqtt
import time
import json
import os

app = Flask(__name__)
CORS(app)

#Obtain variables
postgres_user = os.environ["MF_USER_CONTROL_POSTGRES_USER"] 
postgres_password = os.environ["MF_USER_CONTROL_POSTGRES_PASSWORD"] 
postgres_host = os.environ["MF_USER_CONTROL_POSTGRES_HOST"] # mainflux-things-db
postgres_port = os.environ["MF_USER_CONTROL_POSTGRES_PORT"] #5432
postgres_db = os.environ["MF_USER_CONTROL_POSTGRES_DB"] #things
mqtt_broker_host = "mainflux-mqtt"
mqtt_port = 1883


connection = psycopg2.connect(user=postgres_user,
                                  password=postgres_password,
                                  host=postgres_host,
                                  port=postgres_port,
                                  database=postgres_db)

cursor = connection.cursor()

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


@app.route('/control/CAL///sensors/') #when there is no data in influxdb
def calinitialpage():
	return render_template('calibration-empty.html')

@app.route('/control/CAL/<publisher>/<channel>/sensors/<sensor_name>') #NGINX requires "control"
def calpage(publisher, channel, sensor_name):
	if sensor_name == "pH":
		return render_template('calibration-ph.html', message= "", device = publisher, channel = channel, sensor=sensor_name)
	elif sensor_name == "Conductivity1":
		return render_template('calibration-conductivity1.html', message= "", device = publisher, channel = channel, sensor=sensor_name)
	elif sensor_name == "Conductivity2":
		return render_template('calibration-conductivity2.html', message= "", device = publisher, channel = channel, sensor=sensor_name)
	elif sensor_name == "Oxygen":
		return render_template('calibration-do.html', message= "", device = publisher, channel = channel, sensor=sensor_name)
	elif sensor_name == "AirCO2":
		return render_template('calibration-airco2.html', message= "", device = publisher, channel = channel, sensor=sensor_name)




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
			topic= "channels/" + str(channel) +  "/control/SR/" + str(thing_id)  #only this node will be subscribed to this particular topic
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



@app.route('/control/calibration/Set/<db_to_use>/<target_device>/<channel>/sensors/<sensorname>')
def cal_sensor(db_to_use,target_device,channel,sensorname):

	print("sensor:", sensorname) 
	print("db:", db_to_use) 
	print("target dev:", target_device) 
	print("channel:", channel)
	thing_id, thing_key= query_db(target_device)
	if (thing_id != 0 and thing_key != 0):
		mqtt.Client.connected_flag=False
		client = mqtt.Client()    
		client.username_pw_set(thing_id, thing_key)    #set username and password
		client.on_connect=on_connect
		try:
			client.connect(host=mqtt_broker_host, port=mqtt_port)
			client.loop_start()
			topic= "channels/" + str(channel) +  "/control/CAL/" + str(thing_id)  #only this node will be subscribed to this particular topic
			timestamp = time.time()
			data = {"type": "CAL", "sensor":sensorname, "v":db_to_use, "t":timestamp}
			client.publish(topic,json.dumps(data)) 
			client.disconnect()
			client.loop_stop()
			return "OK"
		except:
			return "Connection to device failed, try again"
	else:
		return "Failed calibrating sensor, try again"	


@app.route('/control/calibration/Check/<target_device>/<channel>/sensors/<sensorname>')
def cal_check(target_device, channel, sensorname):
	return "OK"#"to be implemented"


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
