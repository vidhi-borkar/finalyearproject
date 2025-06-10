from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# I2C setup
i2c = busio.I2C(SCL, SDA)

# PCA9685 instances for two drivers
pca1 = PCA9685(i2c, address=0x40)  # First PCA
pca2 = PCA9685(i2c, address=0x41)  # Second PCA

pca1.frequency = 50  # 50Hz for servo control
pca2.frequency = 50

# Helper function to convert pulse in microseconds to duty cycle
def set_servo_pulse_us(pca, channel, pulse_us):
    pulse_length = 1000000 / pca.frequency  # ~20000 us per cycle
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# Servo control pulse widths
NEUTRAL = 1500
FWD_FEM = 1450
REV_FEM = 1715
FWD_TIB = 1301
REV_TIB = 1700
FWD_COXA = 1400
REV_COXA = 1600

# Channel assignments for each leg [pca, coxa, femur, tibia]
legs = {
    'L1': [pca1, 0, 1, 2],
    'L2': [pca1, 3, 4, 5],
    'L3': [pca1, 6, 7, 8],
    'L4': [pca2, 0, 1, 2],
    'L5': [pca2, 3, 4, 5],
    'L6': [pca2, 6, 7, 8]
}

# Move all tripod legs forward simultaneously
def move_all_legs_forward():
    for leg in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, REV_FEM)  # Femur (lift)
        set_servo_pulse_us(pca, tibia_ch, FWD_TIB)  # Tibia (extend)
    time.sleep(0.5)
    stop_all_legs()

# Move all tripod legs backward simultaneously
def move_all_legs_backward():
    for leg in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, FWD_FEM)  # Femur (lower)
        set_servo_pulse_us(pca, tibia_ch, REV_TIB)  # Tibia (retract)
    time.sleep(0.5)
    stop_all_legs()

# Move all coxa joints forward simultaneously
def move_all_coxa_forward():
    for leg in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, FWD_COXA)
    time.sleep(0.5)
    stop_all_legs()

# Move all coxa joints backward simultaneously
def move_all_coxa_backward():
    for leg in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, REV_COXA)
    time.sleep(0.5)
    stop_all_legs()

# Stop all servos
def stop_all_legs():
    for pca, coxa_ch, femur_ch, tibia_ch in legs.values():
        set_servo_pulse_us(pca, coxa_ch, NEUTRAL)
        set_servo_pulse_us(pca, femur_ch, NEUTRAL)
        set_servo_pulse_us(pca, tibia_ch, NEUTRAL)

# Main control loop
try:
    while True:
        print("Tripod Step Forward")
        move_all_legs_forward()
        time.sleep(1)

        print("Coxa Forward")
        move_all_coxa_forward()
        time.sleep(1)

        print("Tripod Step Backward")
        move_all_legs_backward()
        time.sleep(1)

        print("Coxa Backward")
        move_all_coxa_backward()
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all_legs()

