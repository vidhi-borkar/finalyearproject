from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# I2C setup
i2c = busio.I2C(SCL, SDA)

# PCA9685 instance
pca = PCA9685(i2c)
pca.frequency = 50  # 50Hz for servo control

# Helper function
def set_servo_pulse_us(channel, pulse_us):
    pulse_length = 1000000 / pca.frequency
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# Pulse values (tweak as needed)
NEUTRAL = 1500

FWD_FEM = 1450
REV_FEM = 1715

FWD_TIB = 1301
REV_TIB = 1700

FWD_COXA = 1450
REV_COXA = 1550

# Channels for each leg [coxa, femur, tibia]
legs = {
    'L1': [0, 1, 2],
    'L3': [3, 4, 5],
    'L5': [6, 7, 8]
}

def tripod_step_forward():
    # Phase 1: Lift and extend
    for leg in legs.values():
        set_servo_pulse_us(leg[1], REV_FEM)  # Femur lift
        set_servo_pulse_us(leg[2], FWD_TIB)  # Tibia extend
    time.sleep(0.4)

    # Phase 2: Swing Coxa forward
    for leg in legs.values():
        set_servo_pulse_us(leg[0], FWD_COXA)  # Coxa forward
    time.sleep(0.4)

    # Phase 3: Lower leg
    for leg in legs.values():
        set_servo_pulse_us(leg[1], FWD_FEM)  # Femur down
        set_servo_pulse_us(leg[2], REV_TIB)  # Tibia retract
    time.sleep(0.4)

    # Phase 4: Swing Coxa backward (return to original)
    for leg in legs.values():
        set_servo_pulse_us(leg[0], REV_COXA)  # Coxa back
    time.sleep(0.4)

    stop_all_legs()

def stop_all_legs():
    for ch_list in legs.values():
        for ch in ch_list:
            set_servo_pulse_us(ch, NEUTRAL)

# Main loop
try:
    while True:
        print("Tripod Step Forward with Coxa movement")
        tripod_step_forward()
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all_legs()

