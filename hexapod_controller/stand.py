
import time
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
COXA_NEUTRAL = 1504  # Optional for horizontal alignment
FEMUR_LIFT = 1400    # Raise leg (adjust if needed)
TIBIA_EXTEND = 1400 
FEMUR_DOWN = 1600 # Push body up (adjust if needed)
TIBIA_DOWN =1600
# Leg channels mapping: [PCA, coxa_ch, femur_ch, tibia_ch]
legs = {
    'L1': [pca1, 0, 1, 2],
    'L2': [pca1, 3, 4, 5],
    'L3': [pca1, 6, 7, 8],
    'L4': [pca2, 0, 1, 2],
    'L5': [pca2, 3, 4, 5],
    'L6': [pca2, 6, 7, 8]
}

def stand_up():
    print("Standing up...")

    # Move femurs of all legs with slow movement
    for leg_name in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, _, femur_ch, _ = legs[leg_name]
        
        # Reverse femur movement for even legs (L2, L4, L6)
        if leg_name in ['L2', 'L4', 'L6']:
            femur_position = FEMUR_DOWN  # Reverse position for these legs
        else:
            femur_position = FEMUR_LIFT
        
        print(f"Moving femur of {leg_name} (channel {femur_ch}) to {femur_position}us")
        set_servo_us(pca, femur_ch, femur_position)
    
    time.sleep(0.2)  # Allow femurs to move

    # Move tibias of all legs with slow movement
    for leg_name in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, _, _, tibia_ch = legs[leg_name]
        
        # Reverse tibia movement for even legs (L2, L4, L6)
        if leg_name in ['L2', 'L4', 'L6']:
            tibia_position = TIBIA_DOWN  # Reverse position for these legs
        else:
            tibia_position = TIBIA_EXTEND
        
        print(f"Moving tibia of {leg_name} (channel {tibia_ch}) to {tibia_position}us")
        set_servo_us(pca, tibia_ch, tibia_position)
    
    time.sleep(0.2)  # Allow tibias to move

    print("All legs (1, 2, 3, 4, 5, 6) should now be standing.")

    # Move all servos to neutral positions
    print("Returning all legs to neutral positions...")

    # Move femurs to neutral positions for all legs
    for leg_name in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, _, femur_ch, _ = legs[leg_name]
        print(f"Moving femur of {leg_name} (channel {femur_ch}) to neutral position {COXA_NEUTRAL}us")
        set_servo_us(pca, femur_ch, COXA_NEUTRAL)
    
    # Move tibias to neutral positions for all legs
    for leg_name in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        pca, _, _, tibia_ch = legs[leg_name]
        print(f"Moving tibia of {leg_name} (channel {tibia_ch}) to neutral position {COXA_NEUTRAL}us")
        set_servo_us(pca, tibia_ch, COXA_NEUTRAL)

    time.sleep(0.5)  # Slow down the return to neutral position for smoother transition

    print("All legs (1, 2, 3, 4, 5, 6) are now in the neutral position.")
'''
def stand_up():
    print("Standing up...")

    # Step 1: Move femurs
    for leg_name in legs:
        pca, _, femur_ch, _ = legs[leg_name]
        femur_position = FEMUR_DOWN if leg_name in ['L2', 'L4', 'L6'] else FEMUR_LIFT
        #print(f"Moving femur of {leg_name} (channel {femur_ch}) to {femur_position}us")
        set_servo_us(pca, femur_ch, femur_position)
    
    time.sleep(0.2)

    # Step 2: Move tibias
    for leg_name in legs:
        pca, _, _, tibia_ch = legs[leg_name]
        tibia_position = TIBIA_DOWN if leg_name in ['L2', 'L4', 'L6'] else TIBIA_EXTEND
        #print(f"Moving tibia of {leg_name} (channel {tibia_ch}) to {tibia_position}us")
        set_servo_us(pca, tibia_ch, tibia_position)

    time.sleep(0.3)
    print("Robot is now standing.")

    # Step 3: Move all legs to neutral and keep them there
    print("Holding all legs at neutral position...")

    while True:
        for leg_name in legs:
            pca, _, femur_ch, tibia_ch = legs[leg_name]
            set_servo_us(pca, femur_ch, COXA_NEUTRAL)
            set_servo_us(pca, tibia_ch, COXA_NEUTRAL)
        time.sleep(0.02)  # Refresh rate to keep servos engaged (~50Hz)
'''
try:
    stand_up()
       
except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all_legs()
'''
stand_up()
'''
