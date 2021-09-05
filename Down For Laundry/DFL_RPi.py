from gpiozero import Servo, AngularServo
from libdw import sm
import time
import numpy as np
import datetime
import pickle
from libdw import pyrebase
import RPi.GPIO as GPIO
from term3_1d_ML import time_now, minute_count, column_maker, data_collect, pred_use, update_pyrebase

url = 'https://test-4f06e.firebaseio.com/'
apiKey = 'AIzaSyBKnZs78dnlgJDbMRq_xmxt90oV8xf1BQ4'

config = {
	"apiKey": apiKey,
	"databaseURL": url
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def ultrasonic():
    GPIO.setmode(GPIO.BCM)
    TRIG = 19
    ECHO = 20
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    time.sleep(2)
    GPIO.output(TRIG, True)
    time.sleep(0.0001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO)== 1:
        pulse_end = time.time()
    duration = pulse_end - pulse_start
    distance = duration * 17150
    GPIO.cleanup()
    if distance <= 4:
        return 'closed'
    else:
        return 'open'

def Servo():
    GPIO.setmode(GPIO.BCM)
    servo = AngularServo(17, min_angle = 0, max_angle = 90)
    servo.max()
    time.sleep(1)
    servo.min()
    time.sleep(1)

def led_BA(mode):
    GPIO.setmode(GPIO.BCM)
    led = 21
    GPIO.setup(led, GPIO.OUT)
    if mode == 'on':
        if db.child("machine").child("W").child("1").child("assist").get().val() == 'on':
            GPIO.output(led, GPIO.HIGH)
    elif mode == 'off':
        GPIO.output(led, GPIO.LOW)
        if db.child("machine").child("W").child("1").child("assist").get().val() == 'on':
            db.child("machine").child("W").child("1").child("assist").set('off')
            
class RPI(sm.SM):
    start_state = 0
    def __init__(self):
        super().__init__()

    def get_next_values(self, state, inp):
        if state == 0:
            startswitch = db.child("machine").child("W").child("1").child("status").get()
            if 'busy' in startswitch.val():
                next_state = 1
                output = 'machine turned on'
                print(output)
                Servo()
                led_BA('on')
                self.time = time.time()
                self.start_time = time_now()
                db.child("machine").child("W").child("1").child("status").child("busy").set(0)
            else:
                next_state = 0
                output = db.child('machine').child('W').child('1').child('status').get().val()
                print(output)
                print('state 0')
        if state == 1:
            cur_time = time.time()
            elapsed = (cur_time- self.time)/60
            db.child("machine").child("W").child("1").child("status").child("busy").set(float(elapsed))
            if elapsed < 2:
                next_state = 1
                output = "still washing"
                print(output)
                time.sleep(10)
            else:
                next_state = 2
                output = "DONE washing"
                print(output)
                db.child("machine").child("W").child("1").child("status").set("not collected")
        if state == 2:
            door = ultrasonic()
            led_BA('on')
            if door == 'open':
                next_state = 0
                output = "free"
                print(output)
                db.child("machine").child("W").child("1").child("status").set("free")
                userID = db.child("machine").child("W").child("1").child("user").get().val()
                db.child('users').child(userID).child('log').set('free')
                db.child("machine").child("W").child("1").child("user").set("nil")
                led_BA('off')
                self.end_time = time_now()
                data_collect('W1',self.start_time,self.end_time)
            elif door == 'closed':
                next_state = 2
                output = 'not collected'
                print(output)
                db.child("machine").child("W").child("1").child("status").set("not collected")
                time.sleep(5)
        return next_state, output

a = RPI()
a.start()
while True:
    a.step(1)
    if time_now() == '00:00:00':
        update_pyrebase('W1')
