
from datetime import datetime
import json
import pymysql
import random
import numpy as np
from tflite_runtime.interpreter import Interpreter

true_load = np.array([3.563758,4.087834,4.391916,4.773022,4.934161,5.24555,5.66214,6.49862,7.65643,8.52101,9.23954,9.67549,10.2889,11.12192,10.891079999999999,10.21849,10.13393,10.019269999999999,9.90962,10.1546,9.91901,9.874179999999999,8.8289,8.32781,8.29486,8.101140000000001,7.99845,8.616520000000001,8.358550000000001,7.8187,8.08804,7.83964,6.156140000000001,6.0034,5.81459,4.987112,4.708225,5.10289,3.3365299999999998,2.95241,2.90319,3.03646,2.95448,2.9191000000000003,2.81147,3.0198270000000003,2.85471,3.0556900000000002,3.427409,3.382243])
true_pos = np.array([0.6509628000000001,2.3093701999999996,3.3760985999999997,2.5606414,2.817795,4.224422,5.790934,7.595478,8.91347,9.439086,9.209869999999999,9.066838,9.260182,10.509963999999998,16.96054,39.91786,69.1581,102.49284,143.06506,175.71313999999998,209.61408,223.55172,225.68694,225.07476,224.22621999999998,223.25987999999998,222.59868,224.1278,227.09065999999999,226.37284,221.41155999999998,212.47814,205.50096,205.26042,206.14582,204.75844,203.813,203.7636,200.14561999999998,189.61126,172.97144,155.69664,135.5916,109.82266,86.45494,57.2033,36.855022,21.87755,8.936992,2.2648151999999997])

labels = ["Full pump","Leak travel valve","Leak standing valve","Worn pump barrel","Light fluid stroke","Medium fluid stroke","Severe fluid stroke","Gas interference","Shock of pump up","Shock of pump down","Rods broken"]

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
        conexion = pymysql.connect(
                host="localhost",
                user="rpdeveloper",
                passwd="C0l053n5353:20@",
                database="RPdatabase2")

        try:
                cursor = conexion.cursor()
                cursor.execute(exec)
                filas = cursor.fetchall()
                conexion.commit()
        finally:
                conexion.close()

def db_get(exec):
        conexion = pymysql.connect(
                host="localhost",
                user="rpdeveloper",
                passwd="C0l053n5353:20@",
                database="RPdatabase2")
        try:
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

def build(arr_noise,arr_true):
        return [t + (n)*10 for t,n in zip(arr_true,arr_noise)];

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
                        id = str(m_mqtt["id"])
                        if status == "running":
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
                Id = str(m_mqtt["id"])
                SPM = str(m_mqtt["SPM"])
                p = str(m_mqtt["p"])
                l = str(m_mqtt["l"])
                + np.random.uniform(-0.35,0.35,50)

                #v_l = build(str_vec(l)/25,true_load)
                v_p = str_vec(p)

                v_l = str_vec(l) + np.random.uniform(-0.35,0.35,50)

                pos_surf = vec_str(v_p)
                load_surf = vec_str(v_l)

                print(v_p)

                print(v_l)

                #pos_surf = vec_str(acc_to_distance_model(str_vec(acc)) * 63)
                #load_surf = vec_str(str_vec(m_mqtt["l"]) + 6)
                #pos_down = vec_str(pos_down_model(str_vec(pos_surf)) * 0.5)
                pos_down = vec_str(np.array(v_p) * 0.7)
                load_down = vec_str(load_down_model(str_vec(load_surf)) * 6.5)
                fillPump = fill_model(str_vec(load_surf))
                #diagnosis = diagnosis_model(str_vec(load_surf))
                diagnosis = "Full Pump"

                print(fillPump)

                print()

                print(diagnosis)

                sql_query = 'UPDATE overview_rodpumpdata SET SurfaceLoad = "{0}", SurfacePosition = "{1}",SPM = {2},Diagnosis ="{3}",PumpFill={4},DownLoad="{5}",DownPosition="{6}" WHERE id = {7}'.format(load_surf,pos_surf,SPM,diagnosis,fillPump,load_down,pos_down,Id)

                db_local(sql_query)
                
        except Exception as e:
                print('ERROR..... ', e)

def message_noise(message):
        try:
                print(message)
                m_mqtt = json.loads(message)
                Id = str(m_mqtt["id"])
                p = str(m_mqtt["p"])
                l = str(m_mqtt["l"])

                #v_l = build(str_vec(l)/25,true_load)
                v_p = str_vec(p)

                v_l = str_vec(l) + np.random.uniform(-0.35,0.35,50)

                pos_surf = vec_str(v_p)
                load_surf = vec_str(v_l)


                #pos_surf = vec_str(acc_to_distance_model(str_vec(acc)) * 63)
                #load_surf = vec_str(str_vec(m_mqtt["l"]) + 6)
                #pos_down = vec_str(pos_down_model(str_vec(pos_surf)) * 0.5)
                pos_down = vec_str(np.array(v_p) * 0.7)
                load_down = vec_str(load_down_model(str_vec(load_surf)) * 6.5)
                

                sql_query = 'UPDATE overview_rodpumpdata SET SurfaceLoad = "{0}", SurfacePosition = "{1}",DownLoad="{2}",DownPosition="{3}" WHERE id = {4}'.format(load_surf,pos_surf,load_down,pos_down,Id)

                db_local(sql_query)
                
        except Exception as e:
                print('ERROR..... ', e)

import datetime

sql_query = 'SELECT id,SPM,SurfaceLoad,SurfacePosition FROM overview_rodpumpdata;'
rows = db_get(sql_query)
#(1338, datetime.datetime(2023, 8, 31, 6, 37, 47), None, 0.0, 'Recovering level', 0.0, None, 2, None, None, None, 1.733, 'stopped', None, None, None)

#print(rows)
count = 0
for i in rows:
        msg_dict = {
                        "id":i[0],
                        "SPM":i[1] - 2 + 0.2,
                        "l":i[2],
                        "p":i[3],
                }
                
        message_noise(json.dumps(msg_dict))
        #break


                
#print(rows[-1])


