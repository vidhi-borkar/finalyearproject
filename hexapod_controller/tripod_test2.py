from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# I2C setup
i2c = busio.I2C(SCL, SDA)

# PCA9685 instance
pca = PCA9685(i2c)
pca.frequency = 50  # 50Hz for servo control

# Helper function to convert pulse in microseconds to duty cycle
def set_servo_pulse_us(channel, pulse_us):
    pulse_length = 1000000 / pca.frequency   # ~20000 us per cycle
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# Servo control pulse widths for continuous rotation servos
NEUTRAL = 1500   # Stop
FWD_FEM = 1450   # Femur up
REV_FEM = 1715   # Femur down
FWD_TIB = 1401   # Tibia extend
REV_TIB = 1600   # Tibia retract
FWD_COXA = 1400  # Coxa rotate forward
REV_COXA = 1600  # Coxa rotate backward

# Channel assignments for each leg: [Coxa, Femur, Tibia]
legs = {
    'L1': [0, 1, 2],
    'L3': [3, 4, 5],
    'L5': [6, 7, 8]
}

# Stop all servos on tripod legs
def stop_all_legs():
    for ch_list in legs.values():
        for ch in ch_list:
            set_servo_pulse_us(ch, NEUTRAL)

# One tripod step forward including coxa movement
def tripod_step_forward():
    print("Step: Lift and Extend")
    for leg in legs.values():
        set_servo_pulse_us(leg[1], REV_FEM)  # Femur up
        set_servo_pulse_us(leg[2], FWD_TIB)  # Tibia extend
    time.sleep(0.3)

    print("Step: Coxa Forward")
    for leg in legs.values():
        set_servo_pulse_us(leg[0], FWD_COXA)  # Coxa forward
    time.sleep(0.3)
    for leg in legs.values():
        set_servo_pulse_us(leg[0], NEUTRAL)

    print("Step: Lower Leg")
    for leg in legs.values():
        set_servo_pulse_us(leg[1], FWD_FEM)  # Femur down
        set_servo_pulse_us(leg[2], REV_TIB)  # Tibia retract
    time.sleep(0.4)

    print("Step: Coxa Backward")
    for leg in legs.values():
        set_servo_pulse_us(leg[0], REV_COXA)  # Coxa back
    time.sleep(0.4)
    for leg in legs.values():
        set_servo_pulse_us(leg[0], NEUTRAL)

    stop_all_legs()

# Main control loop
try:
    while True:
        tripod_step_forward()
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all_legs()

