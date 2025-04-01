from datetime import datetime, timedelta
import time
import json
import psycopg2
#import pymysql
import random
import numpy as np
from collections import Counter

# --- only YOLO PREDICT ----
from ultralytics import YOLO
#model = YOLO('best.torchscript')
#model = YOLO('best.pt',task="detect")
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
topic_sub = "jhpOandG/data/#"
topic_pub = "jhpOandG/settings"

payloadImage = json.loads("{}")

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

# =================== funtions for lora decode ===================
class LoRaPacketDecoder:
  def __init__(self):
    self.decoded_data = {}
  
  def decode_base64(self, payload):
    """Decodifica un payload en base64 a bytes."""
    try:
      return base64.b64decode(payload)
    except Exception as e:
      raise ValueError(f"Error decodificando base64: {str(e)}")
  
  def bytes_to_int(self, bytes_data):
    """Convierte bytes a entero."""
    return int.from_bytes(bytes_data, byteorder='big', signed=True)
  
  def decode_float10(self, bytes_data):
    """Decodifica float (asume 2 bytes, con un decimal)."""
    temp = self.bytes_to_int(bytes_data)
    return temp / 10.0
  def decode_float100(self, bytes_data):
    """Decodifica float (asume 3 bytes, con 2 decimal)."""
    temp = self.bytes_to_int(bytes_data)
    return temp / 100.0
  def decode_int(self, bytes_data):
    """Decodifica int (asume 2 bytes, con un decimal)."""
    temp = self.bytes_to_int(bytes_data)
    return temp

  def decode_array(self, bytes_data):
    n = len(bytes_data)
    arrayT = []
    for i in range(0,int(n/2)):
      arrayT.append(self.bytes_to_int(bytes_data[2*i:2*i+2])/100)
    return arrayT

  def decode_packet(self, payload):
    """Decodifica un paquete LoRa completo."""
    # Decodificar base64 si es necesario
    if isinstance(payload, str):
      raw_bytes = self.decode_base64(payload)
    else:
      raw_bytes = payload
    
    # Verificar longitud mínima
    if len(raw_bytes) < 8:
      raise ValueError("Paquete demasiado corto")
    
    # Decodificar los campos
    # Asumimos un formato: 2 bytes temp, 1 byte hum, 2 bytes pressure

    self.decoded_data = {
      'spm': self.decode_float10(raw_bytes[0:2]),
      'fillPump': self.decode_float100(raw_bytes[2:4])*100,
      'sLength': self.decode_float100(raw_bytes[4:6]),
      'vBat': self.decode_float100(raw_bytes[6:8]),
      'status': self.decode_int(raw_bytes[8:9]),
      'load' : self.decode_array(raw_bytes[9:49]),
      'pos' : self.decode_array(raw_bytes[49:])
    }
    
    return self.decoded_data
  
  def to_json(self):
    """Convierte los datos decodificados a JSON."""
    return json.dumps(self.decoded_data, indent=2)

def extract_yolo_predictions(results):
    
    # Extraer las clases como enteros
    classes = results.cls.cpu().numpy().astype(int)
    
    # Extraer los scores de confianza
    confidences = results.conf.cpu().numpy()
    
    # Contar las ocurrencias de cada clase
    class_counts = Counter(classes)
    
    # Crear un diccionario con el conteo
    detections = {
        clase: {
            "cantidad": cantidad,
            "confianza_promedio": np.mean(confidences[classes == clase])
        }
        for clase, cantidad in class_counts.items()
    }
    
    return detections, classes.tolist(), confidences.tolist()

def on_connect(client, userdata, flags, rc,properties):
  print("Connected with result code " + str(rc))
  print("UserData= " + str(userdata))
  print("flags= " + str(flags))
  print("")
  client.subscribe(topic_sub) #qos=2

def on_message(client, userdata, message):
  # {"type":"tank","mac":"48:E7:29:97:23:A0","count":2,"value":"4.729","temp":"74.188","sampleRate":1767}
  # {"type":"env","mac":"48:E7:29:97:23:A8","count":2,"hum1":"4.729","temp1":"74.188","pa1":"74.188","hum2":"4.729","temp2":"4.729","pa2":"74.188","sampleRate":1767}
  try:
    topic_in = str(message.topic)
    data_in = str(message.payload.decode("utf-8"))

    # ================ SENSOR DATA ================
    if topic_in == "jhpOandG/data":
      print(datetime.now(), topic_in)
      m_mqtt = json.loads(data_in)
      typeM = m_mqtt.get("type","NULL")
      print(typeM)

      if typeM == "tank":
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

      elif typeM == "env":
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

      elif typeM == "camVidSet":
        name = m_mqtt.get("name","NULL")
        mac = m_mqtt.get("mac","NULL")
        sql_query = """SELECT * FROM device_camviddevice WHERE "DeviceMacAddress" = '{0}'""".format(mac)
        payloadRaw = db_get(sql_query)
        payloadRaw = payloadRaw[0]

        dtNow = datetime.now()
        timeNow = dtNow.time()
        timeStart = payloadRaw[4]
        timeEnd = payloadRaw[5]

        status = False
        if timeNow >= timeStart and timeNow <= timeEnd:
          status = True

        payload = {
          "name":payloadRaw[2],
          "status":status,
          "timesleep":payloadRaw[6],
          "continuous":payloadRaw[7],
          "refresh":payloadRaw[8],
          "saveImage":payloadRaw[9],
          "runningNN":payloadRaw[10],
          }
        payload = json.dumps(payload)
        client.publish(topic_pub,payload)
        print("pub ",payload)
        pass
    
      elif typeM == "camVid":
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
          model = YOLO('best.pt',task="detect")
          decoded_data=pybase64.b64decode((img64))
          Img_file = open('image.jpg', 'wb')
          Img_file.write(decoded_data)
          Img_file.close()

          results = model(["image.jpg"])
          results[0].save(filename="result.jpg")

          nDetected = results[0].boxes.shape[0]

          if nDetected > 0:
            with open("result.jpg", "rb") as f:
              img64 = base64.b64encode(f.read())
              img64 = img64.decode('utf-8')

        print(nDetected)
        sql_query_id = """SELECT id FROM device_camviddevice WHERE "DeviceMacAddress" = '{0}'""".format(mac)
        raws_id = db_get(sql_query_id)
        _id = raws_id[0][0]
        
        sql_query = """INSERT INTO data_camviddata("DateCreate","IdDevice_id","Humidity","Temperature","VoltageBattery","VoltagePanel","RainCounter","WindVelocity","WindDirection","Status","img_file_name","img64","nDetected") VALUES('{0}',{1},{2},{3},{4},{5},{6},{7},{8},'{9}','{10}','{11}',{12})""".format(dt,_id,hum,temp,bat,pan,rain,velocity,direction,"Normal running",img_file,img64,nDetected)
        
        db_local(sql_query)

      elif typeM == "gatewaySetting":
        name = m_mqtt.get("name","NULL")
        mac = m_mqtt.get("mac","NULL")
        function = m_mqtt.get("function","NULL")

        if function == "setting":
          sql_query = """SELECT * FROM device_gateway WHERE "DeviceMacAddress" = '{0}'""".format(mac)
          payloadRaw = db_get(sql_query)
          payloadRaw = payloadRaw[0]

          #print("gat -- Gateway",payloadRaw)

          dtNow = datetime.now()
          timeNow = dtNow.time()
          timeStart = payloadRaw[4]
          timeEnd = payloadRaw[5]

          status = False
          if timeNow >= timeStart and timeNow <= timeEnd:
            status = True

          payload = {
            "function":function,
            "gateway":payloadRaw[2],
            "status":status,
            "timesleep":payloadRaw[6],
            "refresh":payloadRaw[7],
            }
          payload = json.dumps(payload)
          time.sleep(0.1)
          client.publish(topic_pub + "/"+ mac ,payload)
          print("server GATEWAY",payload)
          
      elif typeM == "trapViewSetting":
        mac = m_mqtt.get("mac","NULL")
        function = m_mqtt.get("function","NULL")

        if function == "setting":
          sql_query = """SELECT * FROM device_trapview WHERE "DeviceMacAddress" = '{0}'""".format(mac)
          payloadDev = db_get(sql_query)
          payloadDev = payloadDev[0]

          #print("****---**",payloadDev)

          A_TH = payloadDev[5]
          runningNN = payloadDev[11]

          #print("dev -- Gateway",payloadGat)

          dtNow = datetime.now()
          timeNow = dtNow.time()
          timeStart = payloadDev[6]
          timeEnd = payloadDev[7]

          status = False
          if timeNow >= timeStart and timeNow <= timeEnd:
            status = True

          payload = {
            #"name":payloadDev[1],
            "function":function,
            "status":status,
            "timesleep":payloadDev[8],
            "A_TH":A_TH,
            "runningNN":runningNN,
            "gateway": "1",
            "refresh":10,
            "continuous":False,
            }
          payload = json.dumps(payload)
          time.sleep(0.2)
          client.publish(topic_pub + "/" + mac ,payload)
          print("SERVER TRAPVIEW",payload)

      elif typeM == "trapView":
        dt = datetime.now()
        mac = m_mqtt.get("mac","NULL")
        hum = m_mqtt.get("H","NULL")
        temp = m_mqtt.get("T","NULL")
        bat = m_mqtt.get("B","NULL")
        pan = m_mqtt.get("P","NULL")
        rain = m_mqtt.get("R","NULL")
        velocity = m_mqtt.get("V","NULL")
        direction = m_mqtt.get("D","NULL")
        img64 = m_mqtt.get("image","NULL")

        if hum == "nan":
          hum = 0

        if temp == "nan":
          temp = 0

        nDetected = 0
        CLASSES = []
        QUANTITY = []

        sql_query_id = """SELECT * FROM device_trapview WHERE "DeviceMacAddress" = '{0}';""".format(mac)
        raws_id = db_get(sql_query_id)

        _id = raws_id[0][0]

        img_bool = True
        if img64 == "NULL" or img64 == "":
          img_bool = False
          CLASSES = [ str(i) for i in CLASSES]
          CLASSES = ",".join(CLASSES)
          CLASSES = "{" + CLASSES + "}"

          QUANTITY = [ str(i) for i in QUANTITY]
          QUANTITY = ",".join(QUANTITY)
          QUANTITY = "{" + QUANTITY + "}"
        else:

          if raws_id[0][7]: # running CNN
            # fileImage change b64 to jpg
            decoded_data=pybase64.b64decode((img64))
            Img_file = open('image.jpg', 'wb')
            Img_file.write(decoded_data)
            Img_file.close()

            model = YOLO('bestHP.pt',task="detect")
            #results = model(["image.jpg"])
            results = model.predict("image.jpg", save=False, imgsz=320, conf=0.15)
            results[0].save(filename="result.jpg")
            detections, classes, confidences = extract_yolo_predictions(results[0].boxes)

            CLASSES = list(detections.keys())
            QUANTITY = [ x['cantidad'] for x in detections.values()]

            if 2 in CLASSES:
              nDetected = QUANTITY[CLASSES.index(2)] #obtener cantidad de plutella - index 2

            CLASSES = [ str(i) for i in CLASSES]
            CLASSES = ",".join(CLASSES)
            CLASSES = "{" + CLASSES + "}"

            QUANTITY = [ str(i) for i in QUANTITY]
            QUANTITY = ",".join(QUANTITY)
            QUANTITY = "{" + QUANTITY + "}"

            if nDetected > 0:
              print("detected insects")
              with open("result.jpg", "rb") as f:
                img64 = base64.b64encode(f.read())
                img64 = img64.decode('utf-8')
          else:
            CLASSES = [ str(i) for i in CLASSES]
            CLASSES = ",".join(CLASSES)
            CLASSES = "{" + CLASSES + "}"

            QUANTITY = [ str(i) for i in QUANTITY]
            QUANTITY = ",".join(QUANTITY)
            QUANTITY = "{" + QUANTITY + "}"
      
        sql_query = """INSERT INTO data_trapviewdata("DateCreate","IdDevice_id","Humidity","Temperature","VoltageBattery","VoltagePanel","RainCounter","WindVelocity","WindDirection","Status","img64","nDetected","img_bool","Classes","Quantity") VALUES('{0}',{1},{2},{3},{4},{5},{6},{7},{8},'{9}','{10}',{11},{12},'{13}','{14}')""".format(dt,_id,hum,temp,bat,pan,rain,velocity,direction,"Normal running",img64,nDetected,img_bool,CLASSES,QUANTITY)
        
        db_local(sql_query)

      elif typeM == "gatewayData":
        dt = datetime.now()
        mac = m_mqtt.get("mac","NULL")
        bat = m_mqtt.get("B","NULL")
        pan = m_mqtt.get("P","NULL")

        sql_query_id = """SELECT id FROM device_gateway WHERE "DeviceMacAddress" = '{0}'""".format(mac)
        raws_id = db_get(sql_query_id)
        _id = raws_id[0][0]
        
        sql_query = """INSERT INTO data_gatewaydata("DateCreate","IdDevice_id","VoltageBattery","VoltagePanel","Status") VALUES('{0}',{1},{2},{3},'{4}')""".format(dt,_id,bat,pan,"Normal running")
        
        db_local(sql_query)

      elif typeM == "wellAnalizer":
        print(m_mqtt)

        dt = datetime.now()
        loraDevEUI = m_mqtt.get("devEUI","0")
        loraDevEUI = loraDevEUI[4:] + "0000" + loraDevEUI[0:4]
        spm = m_mqtt.get("spm","0")
        fillPump = m_mqtt.get("fillPump","0")
        sLength = m_mqtt.get("sLength","0")
        vBat = m_mqtt.get("vBat","0")
        status = m_mqtt.get("status","-1")
        sLoad = m_mqtt.get("load","")
        sPos = m_mqtt.get("pos","")

        print(vBat,sLength,fillPump,sLoad,sPos)

        Diagnosis = 0

        if status == "0" :
          Diagnosis = 11;
        
        sql_query_id = """SELECT id FROM device_wellanalyzerdevice WHERE "DeviceMacAddress" = '{0}'""".format(loraDevEUI)

        raws_id = db_get(sql_query_id)
        _id = raws_id[0][0]

        sql_query = """INSERT INTO data_rodpumpdata("DateCreate","IdDevice_id","RawSurfaceLoad","RawSurfacePosition","SPM","PumpFillage","Diagnosis","Status") VALUES('{0}',{1},'{2}','{3}',{4},{5},'{6}','{7}')""".format(dt,_id,sLoad,sPos,spm,fillPump,Diagnosis,"Normal running")
        db_local(sql_query)
    # ================ LORA DATA ================
    elif topic_in == "jhpOandG/data/lora":
      try:
        loraData = json.loads(data_in)
        loraDevEUI = loraData["devEUI"]
        loraData = loraData["data"]
        decoder = LoRaPacketDecoder()
        decoded = decoder.decode_packet(loraData)

        #client.publish("jhpOandG/setting/lora","77777")
        dt = datetime.now()
        spm = decoded.get("spm","0")
        fillPump = decoded.get("fillPump","0")
        sLength = decoded.get("sLength","0")
        vBat = decoded.get("vBat","0")
        status = decoded.get("status","-1")
        sLoad = decoded.get("load","")
        sPos = decoded.get("pos","")

        print(vBat,sLength,fillPump,sLoad,sPos)

        Diagnosis = 0

        if status == 0 :
          Diagnosis = 11;
        
        sql_query_id = """SELECT id FROM device_wellanalyzerdevice WHERE "DeviceMacAddress" = '{0}'""".format(loraDevEUI)

        raws_id = db_get(sql_query_id)
        _id = raws_id[0][0]

        sql_query = """INSERT INTO data_rodpumpdata("DateCreate","IdDevice_id","RawSurfaceLoad","RawSurfacePosition","SPM","PumpFillage","Diagnosis","Status") VALUES('{0}',{1},'{2}','{3}',{4},{5},'{6}','{7}')""".format(dt,_id,sLoad,sPos,spm,fillPump,Diagnosis,"Normal running")
        db_local(sql_query)
        
        #print(decoder.to_json())
      except Exception as e:
        print(f"Error decodificando: {str(e)}")

    # ================ CAMERAS PAYLOAD ================
    else:
      topicSplit = topic_in.split("/")
    
      # FILTER FOR TOPIC
      I_mac = str(topicSplit[3])
      I_Nparts = int(topicSplit[4])
      I_i = int(topicSplit[5])

      if I_i == 0:
        print("building figure", I_mac)
        mar  = payloadImage.get(I_mac, "1")
        if mar != "1":
          del payloadImage[I_mac]

      pay = payloadImage.get(I_mac,[])
      pay.append(data_in)
      payloadImage[I_mac] = pay

      if I_Nparts == len(payloadImage[I_mac]):
        imsg = "".join(payloadImage[I_mac])
        imsg = json.loads(imsg)

        dt = datetime.now()
        mac = imsg.get("DeviceMacAddress","NULL")
        hum = imsg.get("Humidity","NULL")
        temp = imsg.get("Temperature","NULL")
        bat = imsg.get("VoltageBattery","NULL")
        
        img64 = imsg.get("img64","NULL")

        if hum == "nan":
          hum = 0

        if temp == "nan":
          temp = 0

        StatusB = "0"
        if float(bat) < 3.5:
          StatusB = "1"

        nDetected = 0
        Objective = 0

        sql_query_id = """SELECT * FROM device_trapview WHERE "DeviceMacAddress" = '{0}';""".format(mac)
        raws_id = db_get(sql_query_id)

        _id = raws_id[0][0]

        img_bool = True
        if img64 == "NULL" or img64 == "":
          img_bool = False
        else:
          nDetected = 2
          Objective = 1

        sql_query = """INSERT INTO data_trapviewdata("DateCreate","IdDevice_id","Humidity","Temperature","VoltageBattery","Status","img64","nDetected","img_bool","Objective") VALUES('{0}',{1},{2},{3},{4},'{5}','{6}',{7},{8},{9})""".format(dt,_id,hum,temp,bat,StatusB,img64,nDetected,img_bool,Objective)

        db_local(sql_query)

        del payloadImage[I_mac]

        print(dt, "Successfully")
  
  except Exception as e:
    print('Arrival error..... ', e)

client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

#client = mqtt.Client(client_id, userdata="glertps")
client.connect(broker_address, broker_port, 15)
client.on_connect = on_connect
client.on_message = on_message
#client.connect(broker_address, broker_port, 15)
client.loop_forever()
