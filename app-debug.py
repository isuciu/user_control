from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import psycopg2
import paho.mqtt.client as mqtt
import time
import json
import os
import grafana_interactions as gr

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


@app.route('/control/SetAlarm/<channel>/sensors/<sensorname>/<organization>/<dashboard_name>/<user_login>')
def alarmpage(channel, sensorname, organization, dashboard_name, user_login):
#TBD: USER_LOGIN--> USER_EMAIL. to check in channels table the existing link between channel and user
	# for now: just check that channel is valid, or exists

	if sensorname == "Temperature-S":
		pan_order = 2 #panel order in Alertes dashboard
	elif sensorname == "AirCO2":
		pan_order = 3
	elif sensorname == "WaterLevel":
		pan_order = 4
	elif sensorname == "Oxygen":
		pan_order = 5
	elif sensorname == "AtmosphericTemp":
		pan_order = 6
	elif sensorname == "Conductivity2":
		pan_order = 7
	elif sensorname == "Conductivity1":
		pan_order = 8
	elif sensorname == "Turbidity":
		pan_order = 9
	elif sensorname == "pH":
		pan_order = 10
	elif sensorname == "Humidity":
		pan_order = 11
	elif sensorname == "Temperature-D":
		pan_order = 12
	else:
		message = "Invalid sensor name" #will appear in div
		return render_template('alarm.html', message= message, sensor=sensorname, min_val="None", max_val = "None" , channel=channel,
			 organization=organization, dashboard_name=dashboard_name, user_login=user_login)
		
	#try:
	#	user_email = query_channels(channel)
	#except:
	#	message = "Db Query error"
	#	return render_template('alarm.html', message= message, sensor=sensorname, min_val = "None", max_val= "None", channel=channel,
	#		 organization=organization, dashboard_name=dashboard_name, user_login=user_login)
	user_email = 1
	if user_email is not None: #so channel exists
		try:
			#will extract the json definition of this particular dashboard
			#this fc already switches organization
			print("Obtaining dashboard json")  
			data=gr._get_dashboard_json(dashboard_name, organization) #collapsed has to be True for all rows!
			crt_min = data['dashboard']['panels'][pan_order]['panels'][0]['alert']['conditions'][0]['evaluator']['params'][0]
			crt_max = data['dashboard']['panels'][pan_order]['panels'][0]['alert']['conditions'][0]['evaluator']['params'][1]

			return render_template('alarm.html', message= "", sensor=sensorname, min_val=crt_min, max_val = crt_max, channel=channel,
			 organization=organization, dashboard_name=dashboard_name, user_login=user_login)
		except:
			message = "Something went wrong when querying the alarm"
			return render_template('alarm.html', message= message, sensor=sensorname, min_val="None", max_val = "None" , channel=channel,
			 organization=organization, dashboard_name=dashboard_name, user_login=user_login)
	else:
		message = "Invalid channel"
		return render_template('alarm.html', message= message, sensor=sensorname, min_val="None", max_val = "None", channel=channel,
			 organization=organization, dashboard_name=dashboard_name, user_login=user_login)
	

@app.route('/control/UpdateAlarmDashboard/<channel>/sensors/<sensorname>/<organization>/<dashboard_name>/<user_login>/<set_min_value>/<set_max_value>')
def Set_Alarm(channel, sensorname, organization, dashboard_name, user_login, set_min_value, set_max_value):
	#TBD: USER_LOGIN--> USER_EMAIL. to check in channels table the existing link between channel and user
	# for now: just check that channel is valid, or exists

	print("sensor:", sensorname) 
	print("organization:", organization)
	print("dashboard_name:", dashboard_name)
	print("user_login:", user_login)
	print("set_min_value:", set_min_value)
	print("set_max_value:", set_max_value)


	if sensorname == "Temperature-S":
		pan_order = 2 #panel order in Alertes dashboard
	elif sensorname == "AirCO2":
		pan_order = 3
	elif sensorname == "WaterLevel":
		pan_order = 4
	elif sensorname == "Oxygen":
		pan_order = 5
	elif sensorname == "AtmosphericTemp":
		pan_order = 6
	elif sensorname == "Conductivity2":
		pan_order = 7
	elif sensorname == "Conductivity1":
		pan_order = 8
	elif sensorname == "Turbidity":
		pan_order = 9
	elif sensorname == "pH":
		pan_order = 10
	elif sensorname == "Humidity":
		pan_order = 11
	elif sensorname == "Temperature-D":
		pan_order = 12
	else:
		return "Invalid sensor name" #will appear in div
		


	#try:
	
	#	user_email = query_channels(channel)
	#except:
	#	return "Db Query error"
	user_email = 1	

	if user_email is not None: #so channel exists
		try:
			#will extract the json definition of this particular dashboard
			#this fc already switches organization
			print("Obtaining dashboard json")  
			data=gr._get_dashboard_json(dashboard_name, organization) #collapsed has to be True for all rows!

			data['dashboard']['panels'][pan_order]['panels'][0]['alert']['conditions'][0]['evaluator']['params'][0]= float(set_min_value)
			data['dashboard']['panels'][pan_order]['panels'][0]['alert']['conditions'][0]['evaluator']['params'][1]= float(set_max_value)

			print("Uploading dashboard json")

			status, uid = gr._update_existing_dashboard(data)

			#todo:
			# html file for setting alarms
			# upload code to github and dockerhub and mainflux docker
			if status == "success":
				return "OK"
			else:
				return "Unable to set alarm"
		except:
			return "Something went wrong when querying the alarm"
	else:
		return "Invalid channel"
	

@app.route('/calibration/Check/<target_device>/<channel>/sensors/<sensorname>')
def cal_check(target_device, channel, sensorname):
	return "OK"#"to be implemented"


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
