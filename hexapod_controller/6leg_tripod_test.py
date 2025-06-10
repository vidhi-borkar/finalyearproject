from adafruit_pca9685 import PCA9685
from board import SCL, SDA
from adafruit_servokit import ServoKit
import busio
import time
#import keyboard # Ensure that you have the `keyboard` library installed.

# I2C setup
i2c1 = busio.I2C(SCL, SDA) # For PCA1
i2c2 = busio.I2C(SCL, SDA) # For PCA2

# Initialize the PCA9685 boards
pca1 = ServoKit (channels=16, address=0x40)
pca2 = ServoKit (channels=16, address=0x41)

# PCA9685 instances
pca1 = PCA9685(i2c1)
pca1.frequency = 50 # 50Hz for servo control
pca2 = PCA9685(i2c2)
pca2.frequency = 50 # 50Hz for servo control

# Helper function to convert pulse in microseconds to duty cycle
def set_servo_pulse_us(pca, channel, pulse_us):
    pulse_length = 1000000 / pca.frequency # ~20000 us per cycle
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# Servo control pulse widths
NEUTRAL = 1500 # Stop (neutral position)
FWD_FEM = 1450 # Lift femur (forward rotation)
REV_FEM = 1715 # Lower femur (reverse rotation)
FWD_TIB = 1301 # Extend tibia
REV_TIB = 1700 # Retract tibia
FWD_COXA = 1400 # Coxa forward
REV_COXA = 1600 # Coxa backward

# Leg assignments
legs_pca1 = {
    'L1': [0, 1, 2], # [Coxa, Femur, Tibia]
    'L3': [3, 4, 5],
    'L5': [6, 7, 8]
}
legs_pca2 = {
    'L2': [0, 1, 2], # [Coxa, Femur, Tibia]
    'L4': [3, 4, 5],
    'L6': [6, 7, 8]
}

# Set definitions
set_1 = ['L1', 'L3', 'L5'] # Legs 1, 3, 5
set_2 = ['L2', 'L4', 'L6'] # Legs 2, 4, 6

# Step 1: Lift Set
def lift_set(set_legs, pca_legs, pca):
    for leg in set_legs:
        channels = pca_legs[leg]
        set_servo_pulse_us(pca, channels[1], REV_FEM) # Femur (lift)
        set_servo_pulse_us(pca, channels[2], FWD_TIB) # Tibia (extend)
    time.sleep(0.5)

# Step 2: Lower Set
def lower_set(set_legs, pca_legs, pca):
    for leg in set_legs:
        channels = pca_legs[leg]
        set_servo_pulse_us(pca, channels[1], FWD_FEM) # Femur (lower)
        set_servo_pulse_us(pca, channels[2], REV_TIB) # Tibia (retract)
    time.sleep(0.5)

# Step 3: Coxa Movement for All Legs
def move_coxa(set_1, set_2):
    # Set 1 Coxa forward
    for leg in set_1:
        if leg in legs_pca1:
            set_servo_pulse_us(pca1, legs_pca1[leg][0], FWD_COXA)
        else:
            set_servo_pulse_us(pca2, legs_pca2[leg][0], FWD_COXA)

    # Set 2 Coxa backward
    for leg in set_2:
        if leg in legs_pca1:
            set_servo_pulse_us(pca1, legs_pca1[leg][0], REV_COXA)
        else:
            set_servo_pulse_us(pca2, legs_pca2[leg][0], REV_COXA)

    time.sleep(0.5)

# Step 4: Stop all movements (neutral position)
def stop_all():
    for leg, channels in legs_pca1.items():
        for ch in channels:
            set_servo_pulse_us(pca1, ch, NEUTRAL)
    for leg, channels in legs_pca2.items():
        for ch in channels:
            set_servo_pulse_us(pca2, ch, NEUTRAL)

# Main control loop with keyboard input
try:
    while True:
        #if keyboard.is_pressed('w'): # If 'w' is pressed
            print("Starting hexapod movement...")
            
            # Step 1: Lift Set 1 (Legs 1, 3, 5)
            lift_set(set_1, legs_pca1, pca1)

            # Step 2: Coxa Movement for Set 1 Forward and Set 2 Backward
            move_coxa(set_1, set_2)

            # Step 3: Lower Set 1 (Legs 1, 3, 5)
            lower_set(set_1, legs_pca1, pca1)

            # Step 4: Lift Set 2 (Legs 2, 4, 6)
            lift_set(set_2, legs_pca2, pca2)

            # Step 5: Coxa Movement for Set 2 Forward and Set 1 Backward
            move_coxa(set_2, set_1)

            # Step 6: Lower Set 2 (Legs 2, 4, 6)
            lower_set(set_2, legs_pca2, pca2)
            print("Movement cycle completed.")
       
except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all()

