from datetime import datetime, timedelta
import json
import psycopg2
#import pymysql
import random
import numpy as np

# --- only YOLO PREDICT ----
from ultralytics import YOLO
model = YOLO('best.pt')
import pybase64
import base64
# ==========================

import paho.mqtt.client as mqtt
#broker_address = "broker.emqx.io"
#broker_address = 'broker.hivemq.com'
broker_address = "24.199.125.52"
broker_port = 1883

client_id = f'publish-{random.randint(0, 1000)}'
username = 'jhanccop'
password = 'jhanccop1'
topic_sub = "jhpOandG/data"
topic_pub = "jhpOandG/settings"

with open("../secret.json") as f:
  secret = json.loads(f.read())

def get_secret(secret_name, secrets = secret):
  try:
    return secrets[secret_name]
  except Exception as e:
    print('Arrival msg error..... ', e)

def db_get(exec):
  conexion = psycopg2.connect(
    host="localhost",
    user=get_secret("USER"),
    password=get_secret("PASSWORD"),
    database=get_secret("DB_NAME"),
  )
  try:
    cursor = conexion.cursor()
    cursor.execute(exec)
    filas = cursor.fetchall()
    conexion.commit()
    return filas
  finally:
    conexion.close()

def db_local(exec):
  conexion = psycopg2.connect(
    host="localhost",
    user=get_secret("USER"),
    password=get_secret("PASSWORD"),
    database=get_secret("DB_NAME"),
  )
  try:
    cursor = conexion.cursor()
    cursor.execute(exec)
    #filas = cursor.fetchall()
    conexion.commit()
  finally:
    conexion.close()

def on_connect(client, userdata, flags, rc,properties):
  print("Connected with result code " + str(rc))
  print("UserData= " + str(userdata))
  print("flags= " + str(flags))
  print("")
  client.subscribe(topic_sub)

def on_message(client, userdata, message):
  # {"type":"tank","mac":"48:E7:29:97:23:A0","count":2,"value":"4.729","temp":"74.188","sampleRate":1767}
  # {"type":"env","mac":"48:E7:29:97:23:A8","count":2,"hum1":"4.729","temp1":"74.188","pa1":"74.188","hum2":"4.729","temp2":"4.729","pa2":"74.188","sampleRate":1767}
  try:
    topic_in = str(message.topic)
    data_in = str(message.payload.decode("utf-8"))
    #print(datetime.now(),data_in)
    print(datetime.now())

    m_mqtt = json.loads(data_in)
    type = m_mqtt.get("type","NULL")
    if type == "tank":
      dt = datetime.now()
      mac = m_mqtt.get("mac","NULL")
      value = m_mqtt.get("value","NULL")
      temp = m_mqtt.get("temp","NULL")

      #sql_query_id = "select id from device_tankdevice where device_tankdevice.DeviceMacAddress='{0}'".format(mac)
      sql_query_id = """SELECT id FROM device_tankdevice WHERE "DeviceMacAddress" = '{0}'""".format(mac)

      raws_id = db_get(sql_query_id)
      _id = raws_id[0][0]

      sql_query = """INSERT INTO data_tankdata("DateCreate","IdDevice_id","Level","Temperature","Status") VALUES('{0}',{1},{2},{3},'{4}')""".format(dt,_id,value,temp,"Normal running")
      db_local(sql_query)

    elif type == "env":
      dt = datetime.now()
      mac = m_mqtt.get("mac","NULL")
      hum1 = m_mqtt.get("hum1","NULL")
      temp1 = m_mqtt.get("temp1","NULL")
      pa1 = m_mqtt.get("pa1","NULL")
      hum2 = m_mqtt.get("hum2","NULL")
      temp2 = m_mqtt.get("temp2","NULL")
      pa2 = m_mqtt.get("pa2","NULL")
      
      sql_query_id = """SELECT id FROM device_environmentaldevice WHERE "DeviceMacAddress" = '{0}'""".format(mac)

      raws_id = db_get(sql_query_id)
      _id = raws_id[0][0]
      
      sql_query = """INSERT INTO data_environmentaldata("DateCreate","IdDevice_id","Humidity1","Temperature1","AtmosphericPressure1","Humidity2","Temperature2","AtmosphericPressure2","Status") VALUES('{0}',{1},{2},{3},{4},{5},{6},{7},'{8}')""".format(dt,_id,hum1,temp1,pa1,hum2,temp2,pa2,"Normal running")
      
      db_local(sql_query)

    elif type == "camVidSet":
      name = m_mqtt.get("name","NULL")
      mac = m_mqtt.get("mac","NULL")
      sql_query = """SELECT * FROM device_camviddevice WHERE "DeviceMacAddress" = '{0}'""".format(mac)
      payloadRaw = db_get(sql_query)
      payloadRaw = payloadRaw[0]

      #print(payloadRaw)

      dtNow = datetime.now()
      timeNow = dtNow.time()
      timeStart = payloadRaw[8]
      timeEnd = payloadRaw[7]

      status = False
      if timeNow >= timeStart and timeNow <= timeEnd:
        status = True

      payload = {
        "name":payloadRaw[2],
        "status":status,
        "timesleep":payloadRaw[6],
        "continuous":payloadRaw[9],
        "refresh":payloadRaw[10],
        "saveImage":payloadRaw[11],
        "runningNN":payloadRaw[12],
        }
      payload = json.dumps(payload)
      client.publish(topic_pub,payload)
      print("pub",payload)
      pass
  
    elif type == "camVid":
      dt = datetime.now()
      mac = m_mqtt.get("mac","NULL")
      hum = m_mqtt.get("H","NULL")
      temp = m_mqtt.get("T","NULL")
      bat = m_mqtt.get("B","NULL")
      pan = m_mqtt.get("P","NULL")
      rain = m_mqtt.get("R","NULL")
      velocity = m_mqtt.get("V","NULL")
      direction = m_mqtt.get("D","NULL")
      img_file = m_mqtt.get("img","NULL")
      img64 = m_mqtt.get("image","NULL")

      if hum == "nan":
        hum = 0

      if temp == "nan":
        temp = 0

      nDetected = 0

      if img64 == "NULL" or img64 == "":
        pass
      else:
        # fileImage change b64 to jpg
        decoded_data=pybase64.b64decode((img64))
        Img_file = open('image.jpg', 'wb')
        Img_file.write(decoded_data)
        Img_file.close()
        results = model(["image.jpg"])
        results[0].save(filename="result.jpg")
        nDetected = results[0].boxes.shape[0]

        if nDetected > 0:
          print("detected butterfly")
          with open("result.jpg", "rb") as f:
            img64 = base64.b64encode(f.read())
            img64 = img64.decode('utf-8')

      print(nDetected)
      sql_query_id = """SELECT id FROM device_camviddevice WHERE "DeviceMacAddress" = '{0}'""".format(mac)
      raws_id = db_get(sql_query_id)
      _id = raws_id[0][0]
      
      sql_query = """INSERT INTO data_camviddata("DateCreate","IdDevice_id","Humidity","Temperature","VoltageBattery","VoltagePanel","RainCounter","WindVelocity","WindDirection","Status","img_file_name","img64","nDetected") VALUES('{0}',{1},{2},{3},{4},{5},{6},{7},{8},'{9}','{10}','{11}',{12})""".format(dt,_id,hum,temp,bat,pan,rain,velocity,direction,"Normal running",img_file,img64,nDetected)
      
      db_local(sql_query)

      pass
          
  except Exception as e:
    print('Arrival error..... ', e)

client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

#client = mqtt.Client(client_id, userdata="glertps")
client.connect(broker_address, broker_port, 15)
client.on_connect = on_connect
client.on_message = on_message
#client.connect(broker_address, broker_port, 15)
client.loop_forever()
