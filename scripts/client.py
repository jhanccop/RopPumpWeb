from datetime import datetime
import json
import pymysql
import random
import numpy as np

import paho.mqtt.client as mqtt
broker_address = "broker.emqx.io"
#broker_address = 'broker.hivemq.com'
broker_port = 1883

client_id = 'edgemelast435'
username = 'jhanccop'
password = 'jhanccop1'
topic_sub = "rodpumpdata/data"

labels = ["Full pump","Leak travel valve","Leak standing valve","Worn pump barrel","Light fluid stroke","Medium fluid stroke","Severe fluid stroke","Gas interference","Shock of pump up","Shock of pump down","Rods broken"]
wells_dict = {
        "TEST1":10,
        "12014":9,
        "12019":8,
        "12017":7,
        "12022":6,
        "12090":5,
        "12009":4,
        "12015":3,
        "12026":2,
        "12044":1
}

def diagnosis_labels(arr):
        arr_labels = np.array(labels)
        lab = ",".join(arr_labels[arr])
        return lab

def db_local(exec):
        try:
                conexion = pymysql.connect(
                host="localhost",
                user="rpdeveloper",
                passwd="C0l053n5353:20@",
                database="RPdatabase")
                cursor = conexion.cursor()
                cursor.execute(exec)
                filas = cursor.fetchall()
                conexion.commit()
        finally:
                conexion.close()

def db_get(exec):

        try:
                conexion = pymysql.connect(
                host="localhost",
                user="rpdeveloper",
                passwd="C0l053n5353:20@",
                database="RPdatabase")

                cursor = conexion.cursor()
                cursor.execute(exec)
                filas = cursor.fetchall()
                conexion.commit()
                return filas
        finally:
                conexion.close()

def configure(m_mqtt):
        pass

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        print("UserData= " + str(userdata))
        print("flags= " + str(flags))
        print("")
        client.subscribe(topic_sub)


def on_message(client, userdata, message):
        try:
                #client.subscribe(topic_sub)
                topic_in = str(message.topic)
                data_in = str(message.payload.decode("utf-8"))
                print(data_in)
                if data_in == "Device connected":
                        pass
                else:
                        m_mqtt = json.loads(data_in)
                        status = m_mqtt.get("status","NULL")
                        WellName = str(m_mqtt["well"])
                        RunTime = round(m_mqtt.get("runtime",0),3)
                        if status == "running":
                                acc = m_mqtt.get("p")
                                pos = 64*np.array([0.0,0.004,0.016,0.037,0.064,0.099,0.141,0.188,0.241,0.298,0.358,0.42,0.484,0.548,0.611,0.673,0.731,0.786,0.836,0.881,0.919,0.95,0.975,0.991,0.999,0.999,0.991,0.975,0.95,0.919,0.881,0.836,0.786,0.731,0.673,0.611,0.548,0.484,0.42,0.358,0.298,0.241,0.188,0.141,0.099,0.064,0.037,0.016,0.004,0.0])
                                pos_surf = ",".join([str(i) for i in pos])
                                pos_surf = ""
                                #pos = [str(i) for i in pos]
                                #pos_suf = ",".join(pos)
                                load_down = m_mqtt.get("l",0)
                                #load_surf = ",".join([str(float( i ) + 7) for i in load_down.split(",")])
                                load_surf = ""
                                pos_down = "0.353,0.144,0.0,0.069,0.162,0.268,0.473,1.1,2.525,4.819,7.933,11.56,15.113,18.285,21.22,24.027,27.093,30.494,34.011,37.503,40.626,43.248,45.54,47.465,49.091,50.376,51.159,51.304,50.85,50.08,49.737,49.1,47.599,44.222,39.187,33.526,28.229,23.667,19.768,16.472,13.483,10.646,7.976,5.62,3.776,2.512,1.795,1.38,0.956,0.484"
                                #load = [str(i) for i in load]
                                #load = ",".join(load)
                                SPM = m_mqtt.get("SPM",0)
                                fillPump = m_mqtt.get("f",0) + 20
                                #diagnosis = diagnosis_labels(m_mqtt.get("diag","None"))
                                diagnosis = "Full pump"
                                DT = m_mqtt["dt"]
                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,SurfaceLoad,SurfacePosition,SPM,Diagnosis,PumpFill,Recomendation,PumpName_id,RunTime,RawAcceleration,Status,DownLoad,DownPosition) VALUES ("{0}","{1}","{2}",{3},"{4}",{5},"{6}",{7},{8},"{9}","{10}","{11}","{12}");'.format(DT,load_surf,pos_surf,SPM,diagnosis,fillPump,"Good work area",wells_dict[WellName],RunTime,acc,status,load_down,pos_down)
                                db_local(sql_query)
                        elif status == "stopped":
                                SPM = m_mqtt.get("SPM",0)
                                fillPump = m_mqtt["f"]
                                diagnosis = status #m_mqtt["diag"]
                                DT = m_mqtt["dt"]
                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,PumpName_id,Diagnosis,PumpFill,SPM,RunTime,Status) VALUES ("{0}",{1},"{2}",{3},{4},{5},"{6}")'.format(DT,wells_dict[WellName],"Recovering level",0,0,RunTime,status)
                                db_local(sql_query)
        except Exception as e:
                print('Arrival message error..... ', e)

#id_client = "gle" + str(random.randint(1, 20))
#client.connect(broker_address, broker_port, 15)
client = mqtt.Client(client_id, userdata="glertps")
client.connect(broker_address, broker_port, 15)
client.on_connect = on_connect
client.on_message = on_message
#client.connect(broker_address, broker_port, 15)
client.loop_forever()