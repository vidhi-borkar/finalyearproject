from time import sleep
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# Setup I2C and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# Channels for a single leg (adjust according to wiring)
COXA_CHANNEL = 0
FEMUR_CHANNEL = 1
TIBIA_CHANNEL = 2

# PWM duty cycle range for standard servo (0-180 deg)
def set_servo_angle(channel, angle):
    pulse = int(4096 * ((angle * 11) + 500) / 20000)
    pca.channels[channel].duty_cycle = pulse

# Neutral standing position
def stand_position():
    set_servo_angle(COXA_CHANNEL, 90)
    set_servo_angle(FEMUR_CHANNEL, 90)
    set_servo_angle(TIBIA_CHANNEL, 90)

# Lift and move forward step
def step_forward():
    # Lift leg
    set_servo_angle(FEMUR_CHANNEL, 70)
    set_servo_angle(TIBIA_CHANNEL, 60)
    sleep(0.2)
    
    # Swing forward
    set_servo_angle(COXA_CHANNEL, 110)
    sleep(0.2)
    
    # Lower leg
    set_servo_angle(FEMUR_CHANNEL, 90)
    set_servo_angle(TIBIA_CHANNEL, 90)
    sleep(0.2)

# Move leg backward to simulate push
def push_back():
    set_servo_angle(COXA_CHANNEL, 70)
    sleep(0.2)

# Tripod gait simulation for one leg
def tripod_gait_forward():
    step_forward()
    push_back()

# Main loop
try:
    print("Starting single leg tripod gait...")
    while True:
        tripod_gait_forward()
        sleep(0.5)

except KeyboardInterrupt:
    print("Stopping...")
    stand_position()
    pca.deinit()
