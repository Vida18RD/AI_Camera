import pigpio
import time

class Motor():
    
    def __init__(self,GPIO_EN,GPIO_RPWM,GPIO_LPWM,GPIO):
        self.GPIO_EN=GPIO_EN
        self.GPIO_RPWM=GPIO_RPWM
        self.GPIO_LPWM=GPIO_LPWM
        self.GPIO=GPIO
        self.GPIO.set_mode(self.GPIO_EN,pigpio.OUTPUT)
        self.GPIO.set_mode(self.GPIO_RPWM,pigpio.OUTPUT)
        self.GPIO.set_mode(self.GPIO_LPWM,pigpio.OUTPUT)

    def enableMotor(self):
        self.GPIO.write(self.GPIO_EN,1)
    
    def right(self,velocity=255):
        self.GPIO.set_PWM_dutycycle(self.GPIO_RPWM,velocity)
        time.sleep(0.01)
        self.GPIO.set_PWM_dutycycle(self.GPIO_LPWM,0)

    def left(self,velocity=255):
        self.GPIO.set_PWM_dutycycle(self.GPIO_RPWM,0)
        time.sleep(0.01)
        self.GPIO.set_PWM_dutycycle(self.GPIO_LPWM,velocity)
    
    def stop(self):
        self.GPIO.set_PWM_dutycycle(self.GPIO_RPWM,0)
        time.sleep(0.01)
        self.GPIO.set_PWM_dutycycle(self.GPIO_LPWM,0) 











