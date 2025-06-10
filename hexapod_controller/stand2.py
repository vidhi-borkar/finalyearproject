import time
import threading
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
    pulse_length = 1000000 / (pca.frequency * 4096)  # µs per bit
    ticks = int(us / pulse_length)
    ticks = max(0, min(4095, ticks))  # Clamp to range
    duty_cycle = int(ticks * 65535 / 4096)
    pca.channels[channel].duty_cycle = duty_cycle
    # Optional: Uncomment below for debugging
    # print(f"Channel {channel}: {us}us -> ticks {ticks} -> duty {duty_cycle}")

# Pulse width constants in microseconds
COXA_NEUTRAL = 1500
FEMUR_LIFT = 1400
TIBIA_EXTEND = 1400
FEMUR_DOWN = 1600
TIBIA_DOWN = 1600

# Leg channel mapping: [PCA, coxa_ch, femur_ch, tibia_ch]
legs = {
    'L1': [pca1, 0, 1, 2],
    'L2': [pca1, 3, 4, 5],
    'L3': [pca1, 6, 7, 8],
    'L4': [pca2, 0, 1, 2],
    'L5': [pca2, 3, 4, 5],
    'L6': [pca2, 6, 7, 8]
}

# Stand-up function
def stand_up():
    print("Standing up...")

    # Step 1: Move femurs
    for leg_name in legs:
        pca, _, femur_ch, _ = legs[leg_name]
        femur_position = FEMUR_DOWN if leg_name in ['L2', 'L4', 'L6'] else FEMUR_LIFT
        set_servo_us(pca, femur_ch, femur_position)

    time.sleep(0.2)

    # Step 2: Move tibias
    for leg_name in legs:
        pca, _, _, tibia_ch = legs[leg_name]
        tibia_position = TIBIA_DOWN if leg_name in ['L2', 'L4', 'L6'] else TIBIA_EXTEND
        set_servo_us(pca, tibia_ch, tibia_position)

    time.sleep(0.3)
    print("Robot is now standing.")

# Continuous PWM refresh to retain position under load
def hold_position_forever():
    print("Starting hold-position loop...")
    while True:
        for leg_name in legs:
            pca, _, femur_ch, tibia_ch = legs[leg_name]
            femur_position = FEMUR_DOWN if leg_name in ['L2', 'L4', 'L6'] else FEMUR_LIFT
            tibia_position = TIBIA_DOWN if leg_name in ['L2', 'L4', 'L6'] else TIBIA_EXTEND

            set_servo_us(pca, femur_ch, femur_position)
            set_servo_us(pca, tibia_ch, tibia_position)

        print("PWM refreshed to hold position.")
        time.sleep(0.02)  # Refresh every 20ms (50Hz)

# Function to stop all legs safely
def stop_all_legs():
    print("Stopping all servos...")
    for leg_name in legs:
        pca, _, femur_ch, tibia_ch = legs[leg_name]
        pca.channels[femur_ch].duty_cycle = 0
        pca.channels[tibia_ch].duty_cycle = 0
    print("All servos released.")

# MAIN PROGRAM
try:
    stand_up()
    threading.Thread(target=hold_position_forever, daemon=True).start()

    print("Robot is holding position. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("KeyboardInterrupt detected.")
    stop_all_legs()

