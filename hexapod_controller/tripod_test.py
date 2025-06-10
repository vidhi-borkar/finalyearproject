'''
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# I2C setup
i2c = busio.I2C(SCL, SDA)

# PCA9685 instance
pca = PCA9685(i2c)
pca.frequency = 50

# Helper function
def set_servo_pulse_us(channel, pulse_us):
    pulse_length = 1000000 / pca.frequency   # ~20000 us per cycle
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# Servo control constants
NEUTRAL = 1500   # Stop
FWD_FEM = 1301   # Rotate forward
REV_FEM = 1700   # Rotate reverse
             
FWD_TIB = 1301   # Rotate forward
REV_TIB = 1700   # Rotate reverse



# Channels for each servo]
legs = {
    'L1': [0, 1, 2],
    'L3': [3, 4, 5],
    'L5': [6, 7, 8]
}

def move_leg_forward(channels):
    # Example movement:
    
    set_servo_pulse_us(channels[1], REV_FEM )  # Femur (lift)
    set_servo_pulse_us(channels[2], FWD_TIB )  # Tibia (extend)
    #set_servo_pulse_us(channels[0], FORWARD)  # Coxa
    time.sleep(0.5)
    stop_leg(channels)

def move_leg_backward(channels):
    
    set_servo_pulse_us(channels[1], FWD_FEM)
    set_servo_pulse_us(channels[2], REV_TIB)
    #set_servo_pulse_us(channels[0], REVERSE)
    time.sleep(0.5)
    stop_leg(channels)

def stop_leg(channels):
    for ch in channels:
        set_servo_pulse_us(ch, NEUTRAL)

# Main loop: simulate tripod gait
try:
    while True:
        print("Tripod Step Forward")
        for leg in ['L1', 'L3', 'L5']:
            move_leg_forward(legs[leg])
        time.sleep(1)

        print("Tripod Step Backward")
        for leg in ['L1', 'L3', 'L5']:
            move_leg_backward(legs[leg])
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping all servos")
    for ch_list in legs.values():
        stop_leg(ch_list)
'''
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

# Servo control pulse widths (for continuous rotation servos like MG996R)
NEUTRAL = 1500   # Stop (no rotation)
FWD_FEM = 1450   # Rotate forward (e.g., lift)
REV_FEM = 1715   # Rotate reverse (e.g., lower)
FWD_TIB = 1301   # Extend
REV_TIB = 1700   # Retract
FWD_COXA = 1400  # Coxa rotate forward
REV_COXA = 1600  # Coxa rotate backward

# Channel assignments for each leg [coxa, femur, tibia]
legs = {
    'L1': [0, 1, 2],
    'L3': [3, 4, 5],
    'L5': [6, 7, 8]
}

# Move all tripod legs forward simultaneously
def move_all_legs_forward():
    for leg in ['L1', 'L3', 'L5']:
        channels = legs[leg]
        set_servo_pulse_us(channels[1], REV_FEM)  # Femur (lift)
        set_servo_pulse_us(channels[2], FWD_TIB)  # Tibia (extend)
    time.sleep(0.5)
    stop_all_legs()

# Move all tripod legs backward simultaneously
def move_all_legs_backward():
    for leg in ['L1', 'L3', 'L5']:
        channels = legs[leg]
        set_servo_pulse_us(channels[1], FWD_FEM)  # Femur (lower)
        set_servo_pulse_us(channels[2], REV_TIB)  # Tibia (retract)
    time.sleep(0.5)
    stop_all_legs()
    
# Move all coxa legs backward simultaneously
def move_all_coxa_forward():
    for leg in ['L1', 'L3']:
        channels = legs[leg]
        set_servo_pulse_us(channels[0], FWD_COXA)  # Coxa forward
    for leg in ['L5']:
        channels = legs[leg]
        set_servo_pulse_us(channels[0], REV_COXA)  # Coxa forward
    time.sleep(0.5)
    stop_all_legs()
    
# Move all coxa backward simultaneously
def move_all_coxa_backward():
    for leg in ['L1', 'L3']:
        channels = legs[leg]
        set_servo_pulse_us(channels[0], REV_COXA)  # Coxa forward
    for leg in ['L5']:
        channels = legs[leg]
        set_servo_pulse_us(channels[0], FWD_COXA)  # Coxa forward        
    time.sleep(0.5)
    stop_all_legs()


# Stop all servos on tripod legs
def stop_all_legs():
    for ch_list in legs.values():
        for ch in ch_list:
            set_servo_pulse_us(ch, NEUTRAL)

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

