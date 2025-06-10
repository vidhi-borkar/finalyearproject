# Simple servo test (standalone script)
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

def set_servo_angle(channel, angle):
    pulse = int(4096 * ((angle * (2.5/180)) + 0.5) / 20)
    pca.channels[channel].duty_cycle = pulse

print("Moving servo on channel 0 to 90°")
set_servo_angle(0, 90)
time.sleep(1)
print("Done.")

