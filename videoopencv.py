import sys
import time
import arducam_mipicamera as arducam
import v4l2
import cv2


def set_controls(camera):
    try:
        print("Reset the focus...")
        #camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE,1)
    except Exception as e:
        print(e)
        print("The camera may not support this control.")

    try:
        time.sleep(0.3)
        #print("exposure: ",value_exposure)
        camera.software_auto_exposure(enable = True)
        #camera.set_control(v4l2.V4L2_CID_EXPOSURE, 500)
        time.sleep(0.3)
        camera.software_auto_white_balance(enable = True)
    except Exception as e:
        print(e)

def callback(data):
    buff = arducam.buffer(data)
    file = buff.userdata
    buff.as_array.tofile(file)
    return 0

def align_down(size, align):
    return (size & ~((align)-1))

def align_up(size, align):
    return align_down(size + align - 1, align)

def take_video(cama,bloque,fecha):
    var=False
    try:
        camera = arducam.mipi_camera() #Declaro la Camara
        print("Open camera...")
        camera.init_camera()
        print("Setting the resolution...")
        fmt = camera.set_resolution(3280, 2464) #1920x1080  3280x2464
        print("Current resolution is {}".format(fmt))

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        height = int(align_up(fmt[1], 16))
        width  = int(align_up(fmt[0], 32))
        path=f'/home/pi/Video_Dron/{fecha}_{bloque}_{cama}.avi'
        out = cv2.VideoWriter(path,fourcc, 5, (width,height))
        set_controls(camera)
        x=0
        print('Taking Video..')
        while x<1000:
            frame = camera.capture(encoding = 'i420')
            image = frame.as_array.reshape(int(height * 1.5), width)
            image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
            out.write(image)
            x+=1
        camera.close_camera()
        out.release()
        var=True
    except RuntimeError as e:
        var='NO CAMERA CONNECTED'
    except Exception as e:
        print('error',e,type(e))
        camera.close_camera()
        out.release()
    
    return var

def ejemplo(bloque,cama,fecha):
    return f'Bloque: {bloque}, Cama: {cama}, Fecha: {fecha}'

take_video('1','1','1')