import sys
import os
import socket
import pigpio

LED_ON=17
LED_INTERNET=27

pi = pigpio.pi()
pi.set_mode(LED_ON,pigpio.OUTPUT)
pi.set_mode(LED_INTERNET,pigpio.OUTPUT)

def get_local_ip_address(target):
    ipaddr = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((target, 8000))
        ipaddr = s.getsockname()[0]
        s.close()
    except:
        pass

    return ipaddr



if __name__ == "__main__":
    try:
        pi.write(LED_ON, 1)
        while True:
            ip=get_local_ip_address('10.0.1.1')
            if len(ip)==0:
                pi.write(LED_INTERNET, 0)
            else:
                pi.write(LED_INTERNET, 1)    

    except :
        pi.write(LED_ON, 0)         
        pi.write(LED_INTERNET, 0)


