# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, io, re, cv2
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import datetime, qrcode, time
import requests
import base64
import json
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
PIN_PIR = 18
PIN_PIR_OUT = 17
PIN_MOTOR_IN = 27
PIN_MOTOR_OUT = 15
#receive = 0
paied = 0
cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 320)
ISOTIMEFORMAT = '%Y%m%d,%H%M%S'
SECRET_KEY = 'sk_DEMODEMODEMODEMODEMODEMO'

def get_QRcode_receive(data):  #透過訂閱接收QRcode資料，並判斷資料是否符合辨識結果
 print ("get QRcode receive")
 print "data:" + str(data) +"\n"
 msg = subscribe.simple('Scan',msg_count=1, retained=False, hostname="m23.cloudmqtt.com",
    port=15601, client_id="mqttjs_IoP", keepalive=60, will=None, auth={'username':"qgxusvba", 'password':"O0QPhjo5O9eb"}, tls=None)
 print "data:" + str(data) +"\n"
 print "msg: " + msg.payload
 if str(data) == msg.payload:
  print ("return 1")
  return 1
 else:
  print("return 0")
  return 0

def open_gate(PIN):          #開門
 pwm_motor = GPIO.PWM(PIN, 50)
 pwm_motor.start(7.5)
 print ("open the gate")
 for b in range(100):
  pwm_motor.ChangeDutyCycle(7.9)
  time.sleep(0.01)
 time.sleep(5)
 print("close the gate")
 for d in range(100):
  pwm_motor.ChangeDutyCycle(3.5)
  time.sleep(0.01)
 pwm_motor.stop()

def show_QRcode(data):       #顯示QRcode
 img_QR = cv2.imread("QRcode.jpg")
 while True:
  cv2.imshow('QRcode', img_QR)
  print ("show")
  if  cv2.waitKey(5000) & get_QRcode_receive(data) == 1 :
   cv2.destroyAllWindows()
   cv2.waitKey(1)
   cv2.waitKey(1)
   cv2.waitKey(1)
   cv2.waitKey(1)
   open_gate(PIN_MOTOR_IN)
   break
  elif get_QRcode_receive(data) == 0:
   main()
 print 'I done'

def paied_detection():
 msg = subscribe.simple('Pay',msg_count=1, retained=False, hostname="m23.cloudmqtt.com",
    port=15601, client_id="mqttjs_IoP", keepalive=60, will=None, auth={'username':"qgxusvba", 'password':"O0QPhjo5O9eb"}, tls=None)


def main():
 try:
  GPIO.setup(PIN_PIR, GPIO.IN)
  GPIO.setup(PIN_MOTOR_IN, GPIO.OUT)
  while True:
   current = 0
   current_OUT = 0
   nowtime = str(time.time())
   IMAGE_PATH = '/home/pi/Downloads/plate_' + nowtime  + '.jpg'
   current = GPIO.input(PIN_PIR)
   current_OUT = GPIO.input(PIN_PIR)
   img_base64 = 0
   if current == 1 or current_OUT == 1:
    print ("takephoto")
    ret, frame = cap.read()
    cv2.imwrite('/home/pi/Downloads/plate_' + nowtime + '.jpg', frame)

    #------------------使用openalpr套件--------------------
    global img_base64
    with open(IMAGE_PATH, 'rb') as image_file:
     img_base64 = base64.b64encode(image_file.read())
    url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % (SECRET_KEY)
    r = requests.post(url, data = img_base64)
    #------------------------------------------------------

    #--從json檔取出需要的資料，若判斷失敗就重新執行main()--
    if  len(r.json()['results']) == 0:
     main()
    elif paied == 1:
     open_gate(PIN_MOTOR_OUT)
    else:
     data = r.json()['results'][0]['plate']
    #------------------------------------------------------

    #-----------用時間跟車牌產生QRcode，並show出來---------
     detection = data + "," + nowtime
     img = qrcode.make(detection)
     img.save("QRcode.jpg")
     print data
     show_QRcode(data)
    #------------------------------------------------------

     publish.single("RaspBerry", payload= data, qos=1, retain=False, hostname="m23.cloudmqtt.com",
      port=15601, client_id="mqttjs_", keepalive=60, will=None, auth={'username':"qgxusvba", 'password':"O0QPhjo5O9eb"}, tls=None)
     print 'publish'
     cap.release()
 except KeyboardInterrupt:
  print ("關閉程式")
 finally:
  print ("clear")
  GPIO.cleanup()
  cap.release()
main()
cap.release()
cv2.destroyAllWindows()
