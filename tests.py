import json

def load_json(path):
    with open(path) as f:
        data_json = json.load(f)
    return data_json

try:
    dash_pr_json = load_json('grafana_backend/dashboards/principal.json')
    dash_ag_json = load_json('grafana_backend/dashboards/agregat.json')
    dash_es_json = load_json('grafana_backend/dashboards/estat.json')
    dash_al_json = load_json('grafana_backend/dashboards/alertes.json')
    dash_ca_json = load_json('grafana_backend/dashboards/calibration.json')
except:
    error = "Error when loading json files"
    print(error)

http_protocol = "https"
server_ip = "127.0.0.1"
estat_url = http_protocol + "://" + server_ip + "/control/SetSR/$Publisher/$Topic/sensors/$Sensor"
dash_es_json["panels"][3]["panels"][1]["url"] = estat_url  #!!!all panels not collapsed


#alertas, hardcoded dashboard, no templating
try:
    dash_al_json["panels"][2]["panels"][1]["url"] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Temperature-S/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][3][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/AirCO2/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][4][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/WaterLevel/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][5][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Oxygen/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][6][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/AtmosphericTemp/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][7][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Conductivity2/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][8][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Conductivity1/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][9][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Turbidity/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][10][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/pH/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][11][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Humidity/${__org.name}/$__dashboard/${__user.login}"
    dash_al_json[panels][12][panels][1][url] = http_protocol + "://" + server_ip + "/control/SetAlarm/$Topic/sensors/Temperature-D/${__org.name}/$__dashboard/${__user.login}"
except:
    print("error updating alertes dash")

#calibration
try:
    dash_ca_json[panels][0][panels][0][url] = http_protocol + "://" + server_ip + "/control/CAL/$Publisher/$Topic/sensors/AirCO2"
    dash_ca_json[panels][1][panels][0][url] = http_protocol + "://" + server_ip + "/control/CAL/$Publisher/$Topic/sensors/Oxygen"
    dash_ca_json[panels][2][panels][0][url] = http_protocol + "://" + server_ip + "/control/CAL/$Publisher/$Topic/sensors/Conductivity2"
    dash_ca_json[panels][3][panels][0][url] = http_protocol + "://" + server_ip + "/control/CAL/$Publisher/$Topic/sensors/Conductivity1"
    dash_ca_json[panels][4][panels][0][url] = http_protocol + "://" + server_ip + "/control/CAL/$Publisher/$Topic/sensors/pH"
except:
    print("error updating calibration dash")


try:
    data = dash_al_json
    set_min_value = 400
    set_max_value = 600
    data['panels'][2]['panels'][0]['alert']['conditions'][0]['evaluator']['params'][0]= float(set_min_value)
    data['panels'][2]['panels'][0]['alert']['conditions'][0]['evaluator']['params'][1]= float(set_max_value)

            #also change the position of the critical red line
    data['panels'][2]['panels'][0]['thresholds'][0]['value']= float(set_min_value)
    data['panels'][2]['panels'][0]['thresholds'][1]['value']= float(set_max_value)

    #also change the yaxes min and max values which are set to [0,40] by default. +/- 10% of the interval
    interval = set_max_value - set_min_value
    data['panels'][2]['panels'][0]['yaxes'][0]['min']= float(set_min_value - interval/10)
    data['panels'][2]['panels'][0]['yaxes'][0]['max']= float(set_max_value + interval/10)
    print ("all ok with setting alerts")
except:
    print("sth went wrong")