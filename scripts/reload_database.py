
from datetime import datetime
import json
import pymysql
import random
import numpy as np
from tflite_runtime.interpreter import Interpreter


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
                        RunTime = round(float(m_mqtt.get("runtime",0)),3)
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
                                print(sql_query)
                                #db_local(sql_query)

                        elif status == "stopped":
                                SPM = m_mqtt.get("SPM",0)
                                fillPump = m_mqtt["f"]
                                diagnosis = status #m_mqtt["diag"]
                                DT = m_mqtt["dt"]
                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,PumpName_id,Diagnosis,PumpFill,SPM,RunTime) VALUES ("{0}",{1},"{2}",{3},{4},{5})'.format(DT,wells_dict[WellName],"Recovering level",0,0,RunTime)
                                print(sql_query)
                                #db_local(sql_query)
        except Exception as e:
                print('ERROR..... ', e)

def message_input(message):
        try:

                print(message)
                
                m_mqtt = json.loads(message)
                status = m_mqtt.get("status","NULL")
                WellName = str(m_mqtt["well"])
                RunTime = round(float(m_mqtt.get("runtime",0)),3)

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
                        #print(sql_query)
                        db_local(sql_query)
        except Exception as e:
                print('ERROR..... ', e)

import datetime

sql_query = 'SELECT * FROM overview_rodpumpdata;'
rows = db_get(sql_query)
#(1338, datetime.datetime(2023, 8, 31, 6, 37, 47), None, 0.0, 'Recovering level', 0.0, None, 2, None, None, None, 1.733, 'stopped', None, None, None)

count = 0
for i in rows:
        if i[12] == 'stopped':
                msg_dict = {
                        
                        "well":"12026_",
                        "status":i[12],
                        "dt":i[1].strftime("%Y/%m/%d %H:%M:%S"),
                        "runtime":i[11],
                        "SPM":i[3],
                        "f":0,
                        "diag":i[12],
                }
        else:
                #{"well":"12044","status":"running","dt":"2023/08/31 00:19:37","runtime":0.066660002,"SPM":"7.85","f":46.92,"diag":[6],"l":"1.575,1.658,1.758,1.875,2.017,2.183,2.417,2.600,2.800,3.017,3.258,3.483,3.550,3.558,3.542,3.542,3.617,3.750,3.833,3.867,3.850,3.825,3.742,3.650,3.533,3.408,3.292,3.183,3.042,2.892,2.717,2.542,2.367,2.108,1.917,1.742,1.617,1.558,1.533,1.492,1.442,1.375,1.325,1.308,1.350,1.408,1.483,1.575,1.658,1.658","p":"174.67,173.33,173.33,169.33,168.00,165.33,165.33,160.00,154.67,148.00,141.33,137.33,134.67,129.33,124.00,118.67,116.00,112.00,109.33,106.67,106.67,106.67,101.33,100.00,97.33,96.00,98.67,97.33,96.00,92.00,93.33,93.33,97.33,100.00,100.00,101.33,105.33,112.00,118.67,126.67,130.67,137.33,145.33,150.67,160.00,161.33,165.33,165.33,168.00,169.33"}
                #(121, datetime.datetime(2023, 8, 29, 15, 44, 14), None, 8.56, 'Full pump', 50.19, 'Good work area', 2, '1.942,2.042,2.217,2.408,2.600,2.833,3.092,3.342,3.508,3.575,3.575,3.550,3.567,3.617,3.725,3.825,3.892,3.900,3.867,3.833,3.758,3.667,3.550,3.425,3.300,3.225,3.125,3.058,3.000,2.950,2.908,2.842,2.783,2.683,2.533,2.383,2.208,2.092,1.900,1.733,1.650,1.625,1.625,1.608,1.550,1.517,1.517,1.575,1.658,1.658', '0.353,0.144,0.0,0.069,0.162,0.268,0.473,1.1,2.525,4.819,7.933,11.56,15.113,18.285,21.22,24.027,27.093,30.494,34.011,37.503,40.626,43.248,45.54,47.465,49.091,50.376,51.159,51.304,50.85,50.08,49.737,49.1,47.599,44.222,39.187,33.526,28.229,23.667,19.768,16.472,13.483,10.646,7.976,5.62,3.776,2.512,1.795,1.38,0.956,0.484', '168.00,166.67,165.33,164.00,160.00,154.67,148.00,145.33,138.67,133.33,129.33,124.00,122.67,120.00,116.00,113.33,110.67,105.33,101.33,105.33,102.67,102.67,102.67,100.00,100.00,100.00,100.00,100.00,101.33,101.33,102.67,102.67,102.67,106.67,105.33,110.67,118.67,121.33,126.67,130.67,136.00,140.00,146.67,152.00,156.00,160.00,165.33,168.00,169.33,170.67', 0.3, 'running', '', '', None)
                msg_dict = {
                        
                        "well":"12026_",
                        "status":"running",
                        "dt":i[1].strftime("%Y/%m/%d %H:%M:%S"),
                        "runtime":i[11],
                        "SPM":i[3],
                        "f":0,
                        "diag":"n",
                        "l":i[8],
                        "p":i[10],
                }
                
        message_input(json.dumps(msg_dict))
        #if count == 10:
        #        break
        #count = count + 1
                
#print(rows[-1])


