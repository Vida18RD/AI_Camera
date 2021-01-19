import time
from sensors import driver_motor 
import pigpio




GPIO_EN=16
GPIO_RPWM=12
GPIO_LPWM=13
velocity=255
pi = pigpio.pi()
motor=driver_motor.Motor(GPIO_EN,GPIO_RPWM,GPIO_LPWM,pi)
motor.enableMotor()
motor.right(velocity)
time.sleep(5)
motor.stop()

motor.left(velocity)
time.sleep(5)

motor.stop()
