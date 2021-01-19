import numpy as np
import sys
import time
import arducam_mipicamera as arducam
import v4l2
import cv2
import ctypes
from absl import app, flags, logging
from absl.flags import FLAGS
import threading
from sensors import lightsensor
import os 

stop=False
lumex=0

flags.DEFINE_string('output', 'default', 'path to output video')


def align_down(size, align):
    return (size & ~((align)-1))

def align_up(size, align):
    return align_down(size + align - 1, align)

def exposure(sensor_luz):
    global stop
    global lumex
    try:
        while True:
            lumex=round(sensor_luz.readLight())
            time.sleep(0.3)
            if stop:
                break
        print('Exposure out')
    except Exception as e:
        print('Error Sensor Light',e,type(e))

def set_controls(camera,file,value_exposure):
    global lumex
    try:
        #print("exposure: ",value_exposure)
        write_txt(file,value_exposure,lumex)
        #camera.software_auto_exposure(enable = True)
        camera.set_control(v4l2.V4L2_CID_EXPOSURE, value_exposure)
        camera.software_auto_white_balance(enable = True)
    except Exception as e:
        print(e)

def read_button():
    global stop
    anterior =0
    input('Ingrese')
    actual=1
    if(actual != anterior):
        stop=True


def write_txt(file,exposure,lx):
    file.write(f'Exposure: {exposure} ,Lumex = {lx}\n')

def ratioexposure(lec):
    global lumex
    lumex=lec


def video(_arg):
    global stop
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
        if not stop:
            txt='./Video_Dron/'+str(FLAGS.output)+'.txt'
            file_exposure=open(txt,"w")

           
            out = None

            #opencv 
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            height = int(align_up(fmt[1], 16))
            width  = int(align_up(fmt[0], 32))
            path='./Video_Dron/'+str(FLAGS.output)+'.avi'
            out = cv2.VideoWriter(path,fourcc, 5, (width,height))
            #Habilitar el boton para parar el motor en cualquier momento
            stopmotor = threading.Thread(target = read_button)
            stopmotor.start()
            
            #Grabando Video
            print("Taking Video")
            exp=10
            while True:
                if exp >900 :
                    print('900')
                    exp=0
                set_controls(camera,file_exposure,exp)
                frame = camera.capture(encoding = 'i420')
                image = frame.as_array.reshape(int(height * 1.5), width)
                image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
                out.write(image)
                if stop:
                    break
                exp+=10
            del frame
            file_exposure.close()
            camera.close_camera()
            out.release()
            #cv2.destroyAllWindows()
        else:
            raise OSError ('SENSOR LIGHT IS NOT CONNECTED')

    except KeyboardInterrupt:
        #pi.set_servo_pulsewidth(GPIO_MOTOR,0)
        del frame
        stop=True
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
        app.run(video)
    except KeyboardInterrupt:
        print('Error')
        print(sys.exc_info()[0])
        pass