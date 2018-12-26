# !/usr/bin/python
# -*- coding: utf-8 -*-
import picamera, time, json, request
import RPi.GPIO as GPIO
import base64, datetime
import paho.mqtt.publish as publish

ISOTIMEFORMAT = '%Y%m%d%H%M%S'
SECRET_KEY = 'sk_DEMODEMODEMODEMODEMODEMO'

def publish_location(data):
 publish.single("RaspBerry", payload= data, qos=1, retain=False, hostname="m23.cloudmqtt.com",
      port=15601, client_id="mqttjs_", keepalive=60, will=None, auth={'username':"qgxusvba", 'password':"O0QPhjo5O9eb"}, tls=None)

def sense_distance(time_):
 GPIO.setmode(GPIO.BCM)
 GPIO_TRIGGER = 23
 GPIO_ECHO = 24
 GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
 GPIO.setup(GPIO_ECHO, GPIO.IN)
 GPIO.output(GPIO_TRIGGER, False)
 time.sleep(time_)
 GPIO.output(GPIO_TRIGGER, True)
 time.sleep(0.00001)
 GPIO.output(GPIO_TRIGGER, False)
 start = time.time()
 while GPIO.input(GPIO_ECHO)==0:
  start = time.time()
 while GPIO.input(GPIO_ECHO)==1:
  stop = time.time()
 elapsed = stop - start
 distance = elapsed * 34000
 distance = distance / 2
 print distance
 return distance

def main():
 global sense_time
 global camera
 sense_time = 0
 try:
  while True:
   if (sense_distance(0.5)<15):
    print "sensing " + str(sense_time) + "times"
    sense_time += 1
    time.sleep(2)
    if sense_time > 1:
     camera = picamera.PiCamera()
     camera.resolution = (640,480)
     time.sleep(0.5)
     nowtime = datetime.datetime.now().strftime(ISOTIMEFORMAT)
     camera.capture('A02.jpg')
     IMAGE_PATH = '/home/pi/A02.jpg'
     with open(IMAGE_PATH, 'rb') as image_file:
      img_base64 = base64.b64encode(image_file.read())
     url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % (SECRET_KEY)
     r = requests.post(url, data = img_base64)
     if len(r.json()['results']) == 0:
      camera.close()
      main()
     else:
      data = r.json()['results'][0]['plate']
      location =  str(data) + ',A03'
      publish_location(location)
      print data
      break
 finally:
  GPIO.cleanup()
  camera.close()
main()
