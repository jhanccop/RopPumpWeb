
from datetime import datetime, timedelta
import json
import pymysql
import random
import numpy as np
from tflite_runtime.interpreter import Interpreter

import time

import paho.mqtt.client as mqtt
#broker_address = "broker.emqx.io"
broker_address = 'broker.hivemq.com'
broker_port = 1883

print(broker_address)

client_id = 'edgemelast435rrrrerrtrtr'
username = 'jhanccop'
password = 'jhanccop1'
topic_sub = "jphOandG/data"

labels = ["Full pump","Leak travel valve","Leak standing valve","Worn pump barrel","Light fluid stroke","Medium fluid stroke","Severe fluid stroke","Gas interference","Shock of pump up","Shock of pump down","Rods broken"]
wells_dict = {
        "TEST1":10,
        "12014":9,
        "12019":8,
        "12017":7,
        "12022":6,
        "12090":5,
        "12009":4,
        "12026_":3,
        "12026":2,
        "12044":1
}

def Norm(x):
        x_norm = (x-np.min(x))/(np.max(x)-np.min(x))
        return x_norm

def acc_to_distance_model(arr):
        acc = Norm(arr)
        interpreter = Interpreter("models/acc_to_distance.tflite")
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], acc.reshape([1,50]).astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        distance = tflite_model_predictions.flatten()
        
        return distance

def pos_down_model(arr):
        arr = Norm(arr)
        interpreter = Interpreter("models/pos_surf_down.tflite")
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], arr.reshape([1,50]).astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        pos_down_v = tflite_model_predictions.flatten()

        return np.round(pos_down_v,2)

def load_down_model(arr):
        arr = Norm(arr)
        interpreter = Interpreter("models/load_surf_down.tflite")
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], arr.reshape([1,50]).astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        load_down_v = tflite_model_predictions.flatten()

        return np.round(load_down_v,2)

def fill_model(arr):
        arr = Norm(arr)
        interpreter = Interpreter("models/fill.tflite")
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], arr.reshape([1,50]).astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        fill_v = tflite_model_predictions.flatten()

        return round(fill_v[0]*100,2)

def diagnosis_labels(arr):
        arr_labels = np.array(labels)
        lab = ",".join(arr_labels[arr])
        return lab

def diagnosis_model(arr):
        arr = Norm(arr)
        interpreter = Interpreter("models/diagnosis.tflite")
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], arr.reshape([1,50]).astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        value_diag = tflite_model_predictions.flatten()
        
        v_d = []
        count = 0
        for i in value_diag:
            if i > 0.7:
                v_d.append(count)
            count = count + 1

        return diagnosis_labels(v_d)

def vec_str(arr):
        return ",".join([str(i) for i in arr])

def str_vec(string):
        return np.array([float(i) for i in string.split(",")])


def db_local(exec):
        try:
                conexion = pymysql.connect(
                host="localhost",
                user="rpdeveloper",
                passwd="C0l053n5353:20@",
                database="RPdatabase2")
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
                database="RPdatabase2")

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
                m_mqtt = json.loads(data_in)
                print("data", m_mqtt)
                if m_mqtt["type"] == "tank":
                        print("-------")
                        status = m_mqtt.get("status","NULL")
                        WellName = str(m_mqtt["name"])
                        now = datetime.now() - timedelta(hours=5)
                        date_time = now.strftime("%Y/%m/%d %H:%M:%S")
                        DT = date_time 
                        TankLevel = m_mqtt["height"]
                        sql_query = 'INSERT INTO overview_rodpumpdata (PumpName_id,DateCreate,Status,TankLevel) VALUES ("{0}","{1}","{2}",{3});'.format(1,DT,status,TankLevel)
                        print(sql_query)
                        db_local(sql_query)
                        client.publish("jphOandG/device/tank/finish", "finish")
                else:
                        #m_mqtt = json.loads(data_in)
                        status = m_mqtt.get("status","NULL")
                        WellName = str(m_mqtt["well"]) + "_"
                        RunTime = round(m_mqtt.get("runtime",0),3)
                        if status == "running":
                                acc = acc = m_mqtt.get("p")
                                pos_surf = vec_str(acc_to_distance_model(str_vec(acc)) * 63)
                                
                                load_surf = vec_str(str_vec(m_mqtt["l"]) + 6)
                                
                                pos_down = vec_str(pos_down_model(str_vec(pos_surf)) * 55)
                                load_down = vec_str(load_down_model(str_vec(load_surf)) * 4)
                                SPM =  m_mqtt.get("SPM",0)
                                fillPump = fill_model(str_vec(load_surf))
                                diagnosis = diagnosis_model(str_vec(load_down))

                                DT = m_mqtt["dt"]

                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,SurfaceLoad,SurfacePosition,SPM,Diagnosis,PumpFill,Recomendation,PumpName_id,RunTime,RawAcceleration,Status,DownLoad,DownPosition) VALUES ("{0}","{1}","{2}",{3},"{4}",{5},"{6}",{7},{8},"{9}","{10}","{11}","{12}");'.format(DT,load_surf,pos_surf,SPM,diagnosis,fillPump,"Good work area",wells_dict[WellName],RunTime,acc,status,load_down,pos_down)
                                #print(sql_query)
                                db_local(sql_query)

                        elif status == "stopped":
                                SPM = m_mqtt.get("SPM",0)
                                fillPump = m_mqtt["f"]
                                diagnosis = status #m_mqtt["diag"]
                                DT = m_mqtt["dt"]
                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,PumpName_id,Diagnosis,PumpFill,SPM,RunTime) VALUES ("{0}",{1},"{2}",{3},{4},{5})'.format(DT,wells_dict[WellName],"Recovering level",0,0,RunTime)
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
#client.loop_forever()

client.loop_start()

while 1:
        client.publish("jphOandG/device/tank/start", json.dumps({"mac":"64:B7:08:CA:18:DC","name":"BLACKMON No. 1","timeSleep":270,"TankHeight":15,"TankFactor":13.9886}))
        time.sleep(300)


