import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import servo_reset
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
FEMUR_UP = 1400       # Significantly lifted
FEMUR_DOWN = 1600     # Pushed down
TIBIA_EXTEND = 1495   # Extended outward
TIBIA_TUCK = 1505     # Tucked under
FEMUR_CENTER = 1500
TIBIA_CENTER = 1500
# Coxa positions for walking
COXA_FORWARD = 1600   # Forward position
COXA_CENTER = 1500    # Center position
COXA_BACKWARD = 1400  # Backward position 

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
    
    # Step 1: Prepare legs - extend tibias outward
    for leg_name in legs:
        pca, _, _, tibia_ch = legs[leg_name]
        # Reverse tibia direction for odd-numbered legs
        if leg_name in ['L1', 'L3', 'L5']:
            tibia_position = 1600 # Reverse direction
        else:
            tibia_position = 1400
        set_servo_us(pca, tibia_ch, tibia_position)
    time.sleep(0.1)  # Give time for movement
    stop_all_legs()

    
    # Step 2: Push down with all femurs to lift body
    for leg_name in legs:
        pca, _, femur_ch, _ = legs[leg_name]
        # Reverse femur direction for odd-numbered legs
        if leg_name in ['L1', 'L3', 'L5']:
            femur_position = FEMUR_UP  # Reverse direction
        else:
            femur_position = FEMUR_DOWN
        set_servo_us(pca, femur_ch, femur_position)
    time.sleep(0.8)
    
    print("Standing position achieved")
    print("Controls:")
    print("q - Stand up") 
    print("t - Sit down")
    print("Ctrl+C - Exit")

def stop_all_legs():
    """Stop all servo motors by setting their duty cycle to 0"""
    for leg_name in legs:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg_name]
        pca.channels[coxa_ch].duty_cycle = 0
        pca.channels[femur_ch].duty_cycle = 0
        pca.channels[tibia_ch].duty_cycle = 0

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
    time.sleep(0.6)  # Give time for movement
    
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


def wave_gait_forward():
    """Execute one cycle of wave gait walking forward (one leg at a time)"""
    # Wave sequence: back to front, alternating sides
    leg_sequence_group1 = ['L5', 'L3', 'L1']
    leg_sequence_group2 = ['L6', 'L4', 'L2']

    
    def move_single_leg_group2(leg_name, step_name):
        """Move a single leg through its complete step cycle"""
        print(f"Step: {step_name}")
        
        # Lift leg
        move_leg(leg_name, COXA_CENTER, FEMUR_UP, TIBIA_EXTEND)
        time.sleep(0.5)
        stop_all_legs()
        
        # Move forward while lifted
        move_leg(leg_name, COXA_FORWARD, FEMUR_CENTER, TIBIA_TUCK)
        time.sleep(0.5)
        stop_all_legs()
        
        # Place down at front
        move_leg(leg_name, COXA_CENTER, FEMUR_DOWN, TIBIA_TUCK)
        time.sleep(0.5)
        stop_all_legs()
        
        # Push backward (moves body forward)
        move_leg(leg_name, COXA_BACKWARD, FEMUR_DOWN, TIBIA_TUCK)
        time.sleep(0.5)
        stop_all_legs()
    
    def move_single_leg_group1(leg_name, step_name):
        """Move a single leg through its complete step cycle"""
        print(f"Step: {step_name}")
        
        # Lift leg
        move_leg(leg_name, COXA_CENTER, FEMUR_DOWN , TIBIA_EXTEND)
        time.sleep(0.5)
        stop_all_legs()
        
        # Move forward while lifted
        move_leg(leg_name, COXA_FORWARD, FEMUR_CENTER, TIBIA_TUCK)
        time.sleep(0.5)
        stop_all_legs()
        
        # Place down at front
        move_leg(leg_name, COXA_CENTER, FEMUR_UP, TIBIA_TUCK)
        time.sleep(0.5)
        stop_all_legs()
        
        # Push backward (moves body forward)
        move_leg(leg_name, COXA_BACKWARD, FEMUR_UP, TIBIA_TUCK)
        time.sleep(0.5)
        stop_all_legs()
    
    # Move each leg in sequence
    for leg in leg_sequence_group2:
        move_single_leg_group2(leg, f"Moving {leg}")

    for leg in leg_sequence_group1:
        move_single_leg_group1(leg, f"Moving {leg}")

    



# Main control loop
print("Controls:")
print("q - Stand up")
print("t - Sit down")
print("w - Walk forward (one cycle)")
print("Ctrl+C - Exit")

try:
    while True:
        key = input("Enter command: ").lower()
        if key == 'q':
            stand_up()
            stop_all_legs()
        elif key == 't':
            sit_down()
            stop_all_legs()
        elif key == 'w':
            cnt = 0 
            while cnt < 3:
                print(f"Walking cycle {cnt+1}/3")
                wave_gait_forward()
                cnt += 1
            stop_all_legs()
        else:
            print("Invalid command")
except KeyboardInterrupt:
    print("\nExiting program")
    stop_all_legs()
