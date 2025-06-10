from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# I2C setup
i2c = busio.I2C(SCL, SDA)

# PCA9685 instances for two drivers
pca1 = PCA9685(i2c, address=0x40)
pca2 = PCA9685(i2c, address=0x41)

pca1.frequency = 50
pca2.frequency = 50

# Convert pulse width in microseconds to duty cycle
def set_servo_pulse_us(pca, channel, pulse_us):
    pulse_length = 1000000 / pca.frequency  # us per cycle
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    duty_cycle = max(0, min(65535, duty_cycle))  # Clamp to valid range
    pca.channels[channel].duty_cycle = duty_cycle

# Constants
NEUTRAL = 1500
FWD_FEM = 1450
REV_FEM = 1715
FWD_TIB = 1301
REV_TIB = 1700
FWD_COXA = 1450
REV_COXA = 1550

# Leg map
legs = {
    'L1': [pca1, 0, 1, 2],
    'L2': [pca1, 3, 4, 5],
    'L3': [pca1, 6, 7, 8],
    'L4': [pca2, 0, 1, 2],
    'L5': [pca2, 3, 4, 5],
    'L6': [pca2, 6, 7, 8]
}

# Motion functions
def move_legs(leg_names, femur_pulse, tibia_pulse):
    for leg in leg_names:
        pca, _, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, femur_pulse)
        set_servo_pulse_us(pca, tibia_ch, tibia_pulse)
    time.sleep(0.5)

def move_coxa(leg_names, coxa_pulse):
    for leg in leg_names:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, coxa_pulse)
    time.sleep(0.5)

def stop_all_legs():
    for pca, coxa_ch, femur_ch, tibia_ch in legs.values():
        set_servo_pulse_us(pca, coxa_ch, NEUTRAL)
        set_servo_pulse_us(pca, femur_ch, NEUTRAL)
        set_servo_pulse_us(pca, tibia_ch, NEUTRAL)

# Gait steps
def tripod_step_1():
    move_legs(['L1', 'L3', 'L5'], REV_FEM, FWD_TIB)
    stop_all_legs()
    move_coxa(['L1', 'L3'], FWD_COXA)
    move_coxa(['L5'], REV_COXA)
    stop_all_legs()
    move_legs(['L1', 'L3', 'L5'], FWD_FEM, REV_TIB)
    stop_all_legs()
    move_coxa(['L1', 'L3'], REV_COXA)
    move_coxa(['L5'], FWD_COXA)
    stop_all_legs()

def tripod_step_2():
    move_legs(['L2', 'L4', 'L6'], FWD_FEM, REV_TIB)
    stop_all_legs()
    move_coxa(['L4', 'L6'], REV_COXA)
    move_coxa(['L2'], FWD_COXA)
    stop_all_legs()
    move_legs(['L2', 'L4', 'L6'], REV_FEM, FWD_TIB)
    stop_all_legs()
    move_coxa(['L4', 'L6'], FWD_COXA)
    move_coxa(['L2'], REV_COXA)
    stop_all_legs()

# Main loop
try:
    while True:
        print("Tripod 1 Step")
        tripod_step_1()
        time.sleep(1)

        print("Tripod 2 Step")
        tripod_step_2()
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all_legs()

