import time
import picamera
import numpy as np
import cv2
import pigpio
import sys
from absl import app, flags, logging
from absl.flags import FLAGS
from sensors import lightsensor#import lightsensor
import threading
from sensors import driver_motor #import driver_motor

#GPIO_MOTOR=17
GPIO_STOP_LEFT=26
GPIO_STOP_RIGHT=21

#Motor
GPIO_EN=16
GPIO_RPWM=12
GPIO_LPWM=13


pi = pigpio.pi()
stop_motor=False
stop_conf=False 
stop_total=False
sensor_light=True

value_exposure=0
lumex=0

flags.DEFINE_string('output', '/home/pi/Video_Dron/default', 'path to output video')
flags.DEFINE_string('direction', 'left', 'Right or Left ')
flags.DEFINE_string('velocity', '0', 'Number from 0 to 255')

pi.set_mode(GPIO_STOP_LEFT,pigpio.INPUT)
pi.set_mode(GPIO_STOP_RIGHT,pigpio.INPUT)



if not pi.connected:
       exit()


       

def read_button(dir):
    global stop_motor
    anterior =0
    button = GPIO_STOP_LEFT
    if dir == 'RIGHT':
        button = GPIO_STOP_RIGHT
    #actual=int(input('Ingrese 1 para parar'))
    while not stop_motor:
        actual=pi.read(button)
        input('Ingrese')
        actual=1
        if(actual != anterior):
            stop_motor=True
            break
    print('motor out')


def time_to_proccess():
    global stop_total
    print('Time to proccess')
    time.sleep(8)
    stop_total=True
    print('Time End')

def motor(_arg):
    global stop_motor
    global stop_conf
    global stop_total
    global lumex
    global value_exposure
    global sensor_light
    motor=driver_motor.Motor(GPIO_EN,GPIO_RPWM,GPIO_LPWM,pi)
    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280) #640 1280
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720) #480 720
        cap.set(cv2.CAP_PROP_FPS, 30)#40
        
       
        motor.enableMotor()
        out = None

        #opencv 
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        path=str(FLAGS.output)+'.avi'
        out = cv2.VideoWriter(path,fourcc, 30, (1280,720))

        #Mover el motor
        velocity=int(FLAGS.velocity)
        if velocity > 255:
            velocity=255
        if (str(FLAGS.direction).upper() == 'RIGHT'):
            #motor=1000
            print('right')
            motor.right(velocity)
        if (str(FLAGS.direction).upper() == 'LEFT'):
            #motor=2500
            print('left')
            motor.left(velocity)

        #Habilitar el boton para parar el motor en cualquier momento
        stopmotor = threading.Thread(target = read_button, args=(str(FLAGS.direction).upper(),))
        stopmotor.start()
            
        #Grabando Video
        print("Taking Video")
        x=0
        while True:
            ret, img = cap.read()
            if ret :
                out.write(img)
            if stop_motor and x==0:
                motor.stop()
                print('Button pressed')
                time_pro=threading.Thread(target = time_to_proccess)
                time_pro.start()
                x=1
            if stop_total:
                break

        print('Please Wait..........')
        print('Video has been processed')

        cap.release()
        out.release()

    except KeyboardInterrupt:
        motor.stop()
        stop_motor=True
        stop_total=True
        print('Processing Video..')
        cap.release()
        print('Camera closed')
        print('File Closed')
        out.release()
        print('Out Release')
    except Exception as e:
        print('Error',e,type(e))



if __name__ == '__main__':
    try:
        app.run(motor)
    except KeyboardInterrupt:
        print('Error')
        print(sys.exc_info()[0])
        pass

