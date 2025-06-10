import time
import keyboard
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# I2C setup
i2c = busio.I2C(SCL, SDA)

# Initialize both PCA9685 controllers
pca1 = PCA9685(i2c, address=0x40)
pca2 = PCA9685(i2c, address=0x41)

# Set PWM frequency to 50Hz for standard servos
pca1.frequency = 50
pca2.frequency = 50

# Function to send microseconds to servo safely
def set_servo_us(pca, channel, us):
    pulse_length = 1000000 / (pca.frequency * 4096)  # microseconds per bit
    ticks = int(us / pulse_length)
    ticks = max(0, min(4095, ticks))  # clamp to 0–4095
    duty_cycle = int(ticks * 65535 / 4096)
    pca.channels[channel].duty_cycle = duty_cycle
    print(f"Channel {channel}: {us}us -> ticks {ticks} -> duty {duty_cycle}")

# Define neutral and standing pulse widths in microseconds
COXA_NEUTRAL = 1504      # Optional for horizontal alignment
FEMUR_LIFT = 1400        # Raise leg
TIBIA_EXTEND = 1400      # Stretch tibia
FEMUR_DOWN = 1600        # Push leg down
TIBIA_DOWN = 1600        # Bring tibia back

# Leg channels mapping: [PCA, coxa_ch, femur_ch, tibia_ch]
legs = {
    'L1': [pca1, 0, 1, 2],
    'L2': [pca1, 3, 4, 5],
    'L3': [pca1, 6, 7, 8],
    'L4': [pca2, 0, 1, 2],
    'L5': [pca2, 3, 4, 5],
    'L6': [pca2, 6, 7, 8]
}

# Move Leg L1
def move_leg_L1():
    print("Moving Leg L1")
    pca, coxa, femur, tibia = legs['L1']
    set_servo_us(pca, femur, FEMUR_LIFT)
    set_servo_us(pca, tibia, TIBIA_EXTEND)
    time.sleep(0.3)
    set_servo_us(pca, femur, FEMUR_DOWN)
    set_servo_us(pca, tibia, TIBIA_DOWN)

# Move Leg L4
def move_leg_L4():
    print("Moving Leg L4")
    pca, coxa, femur, tibia = legs['L4']
    set_servo_us(pca, femur, FEMUR_LIFT)
    set_servo_us(pca, tibia, TIBIA_EXTEND)
    time.sleep(0.3)
    set_servo_us(pca, femur, FEMUR_DOWN)
    set_servo_us(pca, tibia, TIBIA_DOWN)

# Stop (reset) all legs to neutral
def stop_all_legs():
    print("Stopping all legs")
    for leg_name in legs:
        pca, coxa, femur, tibia = legs[leg_name]
        set_servo_us(pca, coxa, COXA_NEUTRAL)
        set_servo_us(pca, femur, FEMUR_DOWN)
        set_servo_us(pca, tibia, TIBIA_DOWN)

# MAIN LOOP
print("Hexapod Control:\n  W = move L1\n  S = move L4\n  X = stop all legs\nCtrl+C to exit")
try:
    stop_all_legs()
    while True:
        if keyboard.is_pressed('w'):
            move_leg_L1()
            time.sleep(0.2)
        elif keyboard.is_pressed('s'):
            move_leg_L4()
            time.sleep(0.2)
        elif keyboard.is_pressed('x'):
            stop_all_legs()
            time.sleep(0.2)
except KeyboardInterrupt:
    stop_all_legs()
    print("\nExiting safely.")

