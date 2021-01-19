import pigpio
import numpy as np
import sys
import os
import time
import arducam_mipicamera as arducam
import v4l2
import cv2
from absl import app, flags, logging
from absl.flags import FLAGS
import threading
from sensors import lightsensor
from sensors import driver_motor 

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

flags.DEFINE_string('output', 'default', 'name of video')
flags.DEFINE_string('direction', 'left', 'Right or Left ')
flags.DEFINE_string('velocity', '255', 'Number from 0 to 255')

#pi.set_mode(GPIO_MOTOR,pigpio.OUTPUT)
pi.set_mode(GPIO_STOP_LEFT,pigpio.INPUT)
pi.set_mode(GPIO_STOP_RIGHT,pigpio.INPUT)



if not pi.connected:
       exit()


def exposure(sensor_luz):
    global stop_total
    global sensor_light
    try:
        while True:
            lec=round(sensor_luz.readLight())
            ratioexposure(lec)
            time.sleep(0.5)
            if stop_total:
                break
        print('Exposure out')
    except Exception as e:
        sensor_light=False
        print('Error Sensor Light',e,type(e))
        

def ratioexposure(lec):
    global value_exposure
    global lumex
    lumex=lec
    if lec<12100 :
        value_exposure=70
    elif (lec>=12100) and (lec<15000):
        value_exposure=65
    elif (lec>=15000) and (lec<21000):
        value_exposure=60
    elif (lec>=21000) and (lec<22100):
        k=55
        value_exposure=k-((lec*3)/8000)
        value_exposure=round(value_exposure)
    elif (lec>=22100) and (lec<24000):
        k=51
        value_exposure=k-((lec*3)/8000)
        value_exposure=round(value_exposure)
    elif (lec>=24000) and (lec<27000):
        k=46 #50 
        value_exposure=k-((lec*3)/8000)
        value_exposure=round(value_exposure)
    elif (lec>=27000) and (lec<50000):
        k=45
        value_exposure=k-((lec*3)/8000)
        value_exposure=round(value_exposure)  
    else:
        k=36
        value_exposure=k-((lec*3)/8000)
        value_exposure=round(value_exposure)         

	

def set_controls(camera,file):
    global value_exposure
    global lumex
    '''
    try:
        print("Reset the focus...")
        #camera.reset_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE)
        #camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE, 100)
    except Exception as e:
        print(e)
        print("The camera may not support this control.")
    '''
    try:
        #print("exposure: ",value_exposure)
        write_txt(file,value_exposure,lumex)
        #camera.software_auto_exposure(enable = True)
        camera.set_control(v4l2.V4L2_CID_EXPOSURE, value_exposure)
        camera.software_auto_white_balance(enable = True)
    except Exception as e:
        print(e)

def align_down(size, align):
    return (size & ~((align)-1))

def align_up(size, align):
    return align_down(size + align - 1, align)

def auto_control(camera,file):
    global stop_total
    global stop_conf
    while True:
        time.sleep(1)
        set_controls(camera,file)
        if stop_total:
            stop_conf=True
            break
    print('out_control out')

def read_button(dir):
    global stop_motor
    anterior =0
    button = GPIO_STOP_LEFT
    if dir == 'RIGHT':
        button = GPIO_STOP_RIGHT
    #actual=int(input('Ingrese 1 para parar'))
    while not stop_motor:
        actual=pi.read(button)
        #input('Ingrese')
        #actual=1
        if(actual != anterior):
            stop_motor=True
            break
    print('motor out')

def write_txt(file,exposure,lx):
    file.write(f'Exposure: {exposure} ,Lumex = {lx}\n')

def time_to_proccess():
    global stop_total
    print('Time to proccess')
    time.sleep(2)
    stop_total=True
    print('Time End')

def motor(_arg):
    global stop_motor
    global stop_conf
    global stop_total
    global value_exposure
    global sensor_light
    motor=driver_motor.Motor(GPIO_EN,GPIO_RPWM,GPIO_LPWM,pi)
    try:
        os.makedirs('./Video_Dron', exist_ok=True)
        camera = arducam.mipi_camera() #Declaro la Camara
        print("Open camera...")
        camera.init_camera()
        print("Setting the resolution...")
        fmt = camera.set_resolution(3280, 2464) #1920x1080  3280x2464
        print("Current resolution is {}".format(fmt))

        sensor_luz=lightsensor.Lumex() #Declaro el sensor de luz

        #En paralelo empieza la lectura del sensor
        exp = threading.Thread(target = exposure,args=(sensor_luz,)) 
        exp.start()

        time.sleep(1)
        if sensor_light:
            #Establezo la direccion del motor
            #motor=0
           
            motor.enableMotor()

            #Txt valores de exposuore y lumex
            txt='./Video_Dron/'+str(FLAGS.output)+'.txt'
            file_exposure=open(txt,"w")

            set_controls(camera,file_exposure)
            out = None

            #opencv 
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            height = int(align_up(fmt[1], 16))
            width  = int(align_up(fmt[0], 32))
            path='./Video_Dron/'+str(FLAGS.output)+'.avi'
            out = cv2.VideoWriter(path,fourcc, 5, (width,height))

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
            #pi.set_servo_pulsewidth(GPIO_MOTOR,motor) #2500 right  #1000 left

            #En paralelo,TUNE Camera 
            autoc = threading.Thread(target = auto_control , args=(camera,file_exposure,))
            autoc.start()

            #Habilitar el boton para parar el motor en cualquier momento
            stopmotor = threading.Thread(target = read_button, args=(str(FLAGS.direction).upper(),))
            stopmotor.start()
            
            #Grabando Video
            print("Taking Video")
            x=0
            while True:
                frame = camera.capture(encoding = 'i420')
                image = frame.as_array.reshape(int(height * 1.5), width)
                image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
                out.write(image)
                if stop_motor and x==0:
                    #pi.set_servo_pulsewidth(GPIO_MOTOR,0)
                    motor.stop()
                    print('Button pressed')
                    time_pro=threading.Thread(target = time_to_proccess)
                    time_pro.start()
                    x=1
                    #time.sleep(5)
                    #break
                if stop_total:
                    break

            print('Please Wait..........')
            while not stop_conf:
                print('Please Wait..........')
            print('Video has been processed')
            del frame
            file_exposure.close()
            camera.close_camera()
            out.release()
            #cv2.destroyAllWindows()
        else:
            raise OSError ('SENSOR LIGHT IS NOT CONNECTED')

    except KeyboardInterrupt:
        #pi.set_servo_pulsewidth(GPIO_MOTOR,0)
        motor.stop()
        stop_motor=True
        stop_total=True
        print('Processing Video..')
        while not stop_conf:
            print('.')
        print('Video has been processed')
        del frame
        camera.close_camera()
        print('Camera closed')
        file_exposure.close()
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