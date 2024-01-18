
from datetime import datetime, timedelta
import json
import pymysql
import random
import numpy as np
from tflite_runtime.interpreter import Interpreter

import time

import smtplib, ssl

import paho.mqtt.client as mqtt
#broker_address = "broker.emqx.io"
broker_address = 'broker.hivemq.com'
broker_port = 1883

client_id = 'edgemelast435rrrrerrddtrtfuyfuvgjr'
username = 'jhanccop'
password = 'jhanccop1'
topic_sub = "jphOandG/mexdata"

print(broker_address, topic_sub)

well_id = 2
tank_id = 1

labels = ["Full pump","Leak travel valve","Leak standing valve","Worn pump barrel","Light fluid stroke","Medium fluid stroke","Severe fluid stroke","Gas interference","Shock of pump up","Shock of pump down","Rods broken"]

true_load = np.array([3.563758,4.087834,4.391916,4.773022,4.934161,5.24555,5.66214,6.49862,7.65643,8.52101,9.23954,9.67549,10.2889,11.12192,10.891079999999999,10.21849,10.13393,10.019269999999999,9.90962,10.1546,9.91901,9.874179999999999,8.8289,8.32781,8.29486,8.101140000000001,7.99845,8.616520000000001,8.358550000000001,7.8187,8.08804,7.83964,6.156140000000001,6.0034,5.81459,4.987112,4.708225,5.10289,3.3365299999999998,2.95241,2.90319,3.03646,2.95448,2.9191000000000003,2.81147,3.0198270000000003,2.85471,3.0556900000000002,3.427409,3.382243])
true_pos = np.array([0.6509628000000001,2.3093701999999996,3.3760985999999997,2.5606414,2.817795,4.224422,5.790934,7.595478,8.91347,9.439086,9.209869999999999,9.066838,9.260182,10.509963999999998,16.96054,39.91786,69.1581,102.49284,143.06506,175.71313999999998,209.61408,223.55172,225.68694,225.07476,224.22621999999998,223.25987999999998,222.59868,224.1278,227.09065999999999,226.37284,221.41155999999998,212.47814,205.50096,205.26042,206.14582,204.75844,203.813,203.7636,200.14561999999998,189.61126,172.97144,155.69664,135.5916,109.82266,86.45494,57.2033,36.855022,21.87755,8.936992,2.2648151999999997])

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

def send_mail(well, pastState, actualState, dateTime):

        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        port = 587  # For starttls

        smtp_server = "smtp.gmail.com"
        sender_email = "oil4technology@gmail.com"
        receiver_email = "jhanccop@gmail.com,jhanccop@uni.pe"
        password = "dbyk dnyr pwdz mrwu"

        subject = "Change status {0}".format(well)

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        body = "Well: {0}\nPast status: {1}\nActual status: {2}\nDate time: {3}\n\nMore information visit: http://24.199.125.52/overview".format(well,pastState,actualState,dateTime)

        message.attach(MIMEText(body, "plain"))

        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
            print("Successfully sent email")

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

def configure_wells(client,mac):
        sql_query_id = 'SELECT id FROM wells_well WHERE MacAddress = "{0}"'.format(mac)
        raws_id = db_get(sql_query_id)
        well_id = raws_id[0][0]

        sql_query = 'SELECT Refresh, PumpName FROM wells_well WHERE id = {0}'.format(well_id)
        raws = db_get(sql_query)

        topic_pub = "jphOandG/mexdevice/finish"
        client.publish(topic_pub, json.dumps({"mac":mac,"name":raws[0][1],"timeSleep":raws[0][0]-30}))
        
def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        print("UserData= " + str(userdata))
        print("flags= " + str(flags))
        print("")
        client.subscribe(topic_sub)

def build(arr_noise,arr_true):
        return [t + (n)*10 for t,n in zip(arr_true,arr_noise)];

def refilter(l):
        nl = np.zeros(50)
        for i in range(0,25):
                nl[2*i] = l[i]
                nl[2*i+1] = (l[i] + l[i + 1])/2
        return np.array(nl)

def on_message(client, userdata, message):
        try:
                #client.subscribe(topic_sub)
                #topic_in = str(message.topic)
                data_in = str(message.payload.decode("utf-8"))
                m_mqtt = json.loads(data_in)
                print("data input: ", m_mqtt)

                mac = str(m_mqtt.get("mac","NULL"))

                #now = datetime.now() - timedelta(hours=6)
                now = datetime.now() - timedelta(hours=5)
                date_time = now.strftime("%Y/%m/%d %H:%M:%S")
                DT = date_time 

                print("finish published", DT)
                configure_wells(client,mac)

                if m_mqtt["type"] == "tank":
                        sql_query = 'SELECT TankHeight FROM wells_tank WHERE id = {0};'.format(well_id)
                        raw = db_get(sql_query)

                        status = m_mqtt.get("status","NULL")
                        temperature = m_mqtt.get("temp","NULL")
                        #TankLevel = 15.01 - m_mqtt["value"]; #15.5
                        TankLevel = raw[0][0] - m_mqtt["value"] - 0.5
                        sql_query = 'INSERT INTO overview_tankdata (DateCreate,Status,OilLevel,WaterLevel,Temperature,TankName_id) VALUES ("{0}","{1}",{2},{3},{4},{5});'.format(DT,status,TankLevel,0,temperature,tank_id)
                        #print(sql_query)
                        db_local(sql_query)
                        #client.publish("jphOandG/device/finish/tank", "finish")
                
                elif m_mqtt["type"] == "analyzer":
                        status = m_mqtt.get("status","NULL")
                        RunTime = round(m_mqtt.get("runtime",0),3)

                        if status == "running":
                                status = "Normal running"
                        elif status == "stopped":
                                status = "Stopped unit"


                        # get last state
                        sql_query_status = 'SELECT Status FROM overview_rodpumpdata WHERE PumpName_id = {0} ORDER BY DateCreate DESC LIMIT 1'.format(well_id)
                        raws_status = db_get(sql_query_status)
                        lastStatus = raws_status[0][0]

                        name = m_mqtt.get("name","NULL")

                        print()

                        if lastStatus != status:
                                send_mail(name, lastStatus, status, DT)

                        if status == "Normal running":

                                SPM =  m_mqtt.get("SPM",0)
                                p = m_mqtt["p"]
                                l = m_mqtt["l"]

                                #if SPM < 1:
                                #        p = refilter(p)
                                #        l = refilter(l)
                                #SPM = SPM * 2

                                acc = vec_str(p)
                                raw_pos_surf = vec_str(acc_to_distance_model(p))
                                raw_load_surf = vec_str(np.array(l))

                                print(1)

                                pos_surf = vec_str(build(acc_to_distance_model((p)), true_pos))
                                print(2)
                                #pos_surf = pos_surf + np.random.uniform(-0.35,0.35,50)
                                print(3)
                                
                                #load_surf = vec_str(build(np.array(m_mqtt["l"]),true_load))
                                load_surf = vec_str(np.array(l) * 24 - 10)
                                print(4)
                                
                                pos_down = vec_str(pos_down_model(str_vec(pos_surf)) * 0.85)
                                print(5)
                                
                                load_down = vec_str(load_down_model(str_vec(load_surf)) - 10)
                                print(6)

                                fillPump = fill_model(str_vec(load_surf))
                                fillPump = 0
                                print(8, fillPump)
                                
                                diagnosis = diagnosis_model(str_vec(load_surf))
                                print(9, diagnosis)
                                
                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,SurfaceLoad,SurfacePosition,SPM,Diagnosis,PumpFill,Recomendation,PumpName_id,RunTime,RawAcceleration,Status,DownLoad,DownPosition,RawSurfaceLoad,RawSurfacePosition) VALUES ("{0}","{1}","{2}",{3},"{4}",{5},"{6}",{7},{8},"{9}","{10}","{11}","{12}","{13}","{14}");'.format(DT,load_surf,pos_surf,SPM,diagnosis,fillPump,"Good work area",well_id,RunTime,acc,status,load_down,pos_down,raw_load_surf,raw_pos_surf)
                                #print(sql_query)
                                db_local(sql_query)


                        elif status == "Stopped unit":
                                SPM = m_mqtt.get("SPM",0)
                                fillPump = m_mqtt["fill"]
                                diagnosis = status #m_mqtt["diag"]
                                sql_query = 'INSERT INTO overview_rodpumpdata (DateCreate,PumpName_id,Diagnosis,Status,PumpFill,SPM,RunTime) VALUES ("{0}",{1},"{2}","{3}",{4},{5},{6})'.format(DT,well_id,"Recovering level","Stopped unit",0,0,RunTime)
                                db_local(sql_query)

                                #sql_query = 'UPDATE overview_rodpumpdata  SET TankLevel = {0}, Status = "{1}" WHERE  PumpName_id = {2} AND DateCreate = "{3}";'.format(TankLevel,status,1,DT)
                                
                
        except Exception as e:
                print('Arrival message error..... ', e)

client = mqtt.Client(client_id, userdata="glertps")
client.connect(broker_address, broker_port, 15)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
#client.loop_start()

#time.sleep(10)

"""
while 1:
        sql_query = 'SELECT Refresh, PumpName FROM wells_well WHERE id = {0}'.format(well_id)
        raws = db_get(sql_query)
        now = datetime.now() - timedelta(hours=4)
        date_time = now.strftime("%Y/%m/%d %H:%M:%S")
        print("start published")
        client.publish("jphOandG/mexdevice/start", json.dumps({"name":raws[0][1],"dt":date_time,"timeSleep":raws[0][0]-30}))
        time.sleep(raws[0][0])
"""

