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

# Define servo positions in microseconds

#FEMUR
FEMUR_UP = 1600       # Significantly lifted
FEMUR_DOWN = 2000     # Pushed down
FEMUR_CENTER = 1800

# TIBIA 
TIBIA_EXTEND = 1600   # Extended outward
TIBIA_TUCK = 2000     # Tucked under
TIBIA_CENTER = 1800

# COXA
COXA_FORWARD = 1600   # Forward position
COXA_BACKWARD = 2000  # Backward position 
COXA_CENTER = 1800    # Center position


# Leg channels mapping: [PCA, coxa_ch, femur_ch, tibia_ch]
legs = {
    'L1': [pca1, 0, 1, 2],
    # 'L2': [pca1, 3, 4, 5],
    # 'L3': [pca1, 6, 7, 8],
    # 'L4': [pca2, 0, 1, 2],
    # 'L5': [pca2, 3, 4, 5],
    # 'L6': [pca2, 6, 7, 8]
}

def stand_up():
    print("Standing up...")
    
    # # Step 1: Prepare legs - extend tibias outward
    # for leg_name in legs:
    #     pca, _, _, tibia_ch = legs[leg_name]
    #     # Reverse tibia direction for odd-numbered legs
    #     if leg_name in ['L1', 'L3', 'L5']:
    #         tibia_position = TIBIA_TUCK # Reverse direction
    #     else:
    #         tibia_position = TIBIA_EXTEND
        
    #     set_servo_us(pca, tibia_ch, tibia_position)
    # time.sleep(0.1)  # Give time for movement
    # stop_all_legs()

    
    # Step 2: Push down with all femurs to lift body
    for leg_name in legs:
        pca, _, femur_ch, _ = legs[leg_name]
        # Reverse femur direction for odd-numbered legs
        femur_position = 2000
        set_servo_us(pca, femur_ch, femur_position)
        time.sleep(0.2)
        stop_all_legs()
    

def stop_all_legs():
    """Stop all servo motors by setting their duty cycle to 0"""
    for leg_name in legs:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg_name]
        pca.channels[coxa_ch].duty_cycle = 0
        pca.channels[femur_ch].duty_cycle = 0
        pca.channels[tibia_ch].duty_cycle = 0
    print("Controls:")
    print("q - Stand up")
    print("t - Sit down")
    print("w - Walk forward")
    print("e - Stop all legs")
    print("Ctrl+C - Exit code loop")

def sit_down():
    print("Sitting down...")
    
    # Step 1: Lower body by moving femurs to neutral
    for leg_name in legs:
        pca, _, femur_ch, _ = legs[leg_name]
        # Reverse femur direction for odd-numbered legs
        if leg_name in ['L1', 'L3', 'L5']:
            femur_position = FEMUR_DOWN  # Reverse direction for sitting
        else:
            femur_position = FEMUR_UP
        set_servo_us(pca, femur_ch, femur_position)
    time.sleep(0.4)  # Give time for movement
    
    # Step 2: Tuck tibias in
    for leg_name in legs:
        pca, _, _, tibia_ch = legs[leg_name]
        # Reverse tibia direction for odd-numbered legs
        if leg_name in ['L1', 'L3', 'L5']:
            tibia_position = TIBIA_EXTEND  # Reverse direction for sitting
        else:
            tibia_position = TIBIA_TUCK
        set_servo_us(pca, tibia_ch, tibia_position)
    time.sleep(0.1)  # Give time for movement
    
    print("Sitting position achieved")

def move_leg(leg_name, coxa_pos, femur_pos, tibia_pos):
    """Move a single leg to specified positions"""
    pca, coxa_ch, femur_ch, tibia_ch = legs[leg_name]
    
    set_servo_us(pca, coxa_ch, coxa_pos)
    set_servo_us(pca, femur_ch, femur_pos)
    set_servo_us(pca, tibia_ch, tibia_pos)


def tripod_gait_forward():
    """Execute one cycle of tripod gait walking forward."""
    tripod1 = ['L1', 'L3', 'L5']
    tripod2 = ['L2', 'L4', 'L6']

    # Define femur positions for lift/lower based on tripod group
    # For Tripod 1, servo commands are reversed for femur
    FEMUR_UP_T1 = FEMUR_DOWN
    FEMUR_DOWN_T1 = FEMUR_UP
    # For Tripod 2, servo commands are normal
    FEMUR_UP_T2 = FEMUR_UP
    FEMUR_DOWN_T2 = FEMUR_DOWN

    # --- STEP 1: Tripod 1 moves forward while Tripod 2 provides support & propulsion ---
    print("Tripod Gait: Step 1")

    # Lift Tripod 1 legs and move them forward
    for leg in tripod1:
        move_leg(leg, COXA_CENTER, FEMUR_UP_T1, TIBIA_EXTEND)
    stop_all_legs()

    # Push with Tripod 2 to move body forward
    for leg in tripod2:
        move_leg(leg, COXA_CENTER, FEMUR_DOWN_T2, TIBIA_TUCK)
    time.sleep(0.25)
    stop_all_legs()


    # Lower Tripod 1
    for leg in tripod1:
        move_leg(leg, COXA_CENTER, FEMUR_DOWN_T1, TIBIA_TUCK)
    time.sleep(0.25)
    stop_all_legs()


    # --- STEP 2: Tripod 2 moves forward while Tripod 1 provides support & propulsion ---
    print("Tripod Gait: Step 2")

    # Lift Tripod 2 legs and move them forward
    for leg in tripod2:
        move_leg(leg, COXA_CENTER, FEMUR_UP_T2, TIBIA_EXTEND)
    stop_all_legs()

    # Push with Tripod 1 to move body forward
    for leg in tripod1:
        move_leg(leg, COXA_CENTER, FEMUR_DOWN_T1, TIBIA_TUCK)
    time.sleep(0.25)
    stop_all_legs()


    # Lower Tripod 2
    for leg in tripod2:
        move_leg(leg, COXA_CENTER, FEMUR_DOWN_T2, TIBIA_TUCK)
    time.sleep(0.25)
    stop_all_legs()


# Main control loop
print("Controls:")
print("q - Stand up")
print("t - Sit down")
print("w - Walk forward")
print("e - Stop all legs")
print("Ctrl+C - Exit code loop")

try:
    while True:
        key = input("Enter command: ").lower()
        if key == 'q':
            stand_up()
            stop_all_legs()
        elif key == 't':
            sit_down()
            stop_all_legs()
        elif key == 'e':
            stop_all_legs()
        elif key == 'w':
            cnt = 0 
            while cnt < 3:
                print(f"Walking cycle {cnt+1}")
                tripod_gait_forward()
                cnt += 1
            stop_all_legs()
        else:
            print("Invalid command")
except KeyboardInterrupt:
    print("\nExiting program")
    stop_all_legs()

