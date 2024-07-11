from datetime import datetime
import json
import psycopg2
#import pymysql
import random
import numpy as np

import paho.mqtt.client as mqtt
#broker_address = "broker.emqx.io"
broker_address = 'broker.hivemq.com'
broker_port = 1883

client_id = 'sodhfo3643435455644'
username = 'jhanccop'
password = 'jhanccop1'
topic_sub = "jhpOandG/data"

def db_get(exec):
  conexion = psycopg2.connect(
    host="localhost",
    user="userapp",
    password="userApp24",
    database="databaseapp",
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
    user="userapp",
    password="userApp24",
    database="databaseapp",
  )
  try:
    cursor = conexion.cursor()
    cursor.execute(exec)
    #filas = cursor.fetchall()
    conexion.commit()
  finally:
    conexion.close()

def on_connect(client, userdata, flags, rc):
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
    print(datetime.now(),data_in)

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
    else:
      pass
          
  except Exception as e:
    print('Arrival message error..... ', e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id,userdata="glertps")

#client = mqtt.Client(client_id, userdata="glertps")
client.connect(broker_address, broker_port, 15)
client.on_connect = on_connect
client.on_message = on_message
#client.connect(broker_address, broker_port, 15)
client.loop_forever()
