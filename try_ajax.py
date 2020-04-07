from flask import Flask, jsonify, render_template
from flask_cors import CORS
import psycopg2
import paho.mqtt.client as mqtt
import time
import json

app = Flask(__name__)
counter = -1
CORS(app)
connection = psycopg2.connect(user="mainflux",
                                  password="mainflux",
                                  host="172.18.0.3",
                                  port="5432",
                                  database="things")
cursor = connection.cursor()

broker_address= "localhost"
port = 1883
           #create new instance

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
	print("inside on connect")
	if rc == 0:
		client.connected_flag=True               #Signal connection 
	else:
		client.connected_flag=False
                   #attach function to callback

@app.route('/tryingajax/SetSR/<publisher>/<channel>/sensors/<sensor_name>')
def hello(publisher, channel, sensor_name):
	global counter, dom
	counter = counter + 1
	val = str(counter)
	un = "s" #seconds
	return render_template('index.html', device = publisher, channel = channel, sensor=sensor_name,value=val, unit=un)


@app.route('/SendMessage/<selectedvalue>/<publisher>/<channel>/sensors/<sensor_name>')
def sendmessage(selectedvalue, publisher, channel, sensor_name):
	thing_id, thing_key= query_db(publisher)
	if (thing_id != 0 and thing_key != 0):
		mqtt.Client.connected_flag=False
		client = mqtt.Client()    
		client.username_pw_set(thing_id, thing_key)    #set username and password
		client.on_connect=on_connect
		try:
			client.connect(broker_address, port=port)
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

if __name__ == '__main__':
	app.run()
