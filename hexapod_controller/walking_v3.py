import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
from pwmio import PWMOut
from adafruit_motor import servo

# Setup I2C and PCA9685 devices
i2c = busio.I2C(SCL, SDA)
pca1 = PCA9685(i2c, address=0x40)  # Legs 1,2,3
pca2 = PCA9685(i2c, address=0x41)  # Legs 4,5,6
pca1.frequency = 50
pca2.frequency = 50

# Servo helper function
def set_servo_angle(pca, channel, angle):
    pulse = int(4096 * ((angle * (2.5/180)) + 0.5) / 20)
    pca.channels[channel].duty_cycle = pulse

# Define legs and their channels (Coxa, Femur, Tibia)
legs = {
    1: (pca1, [0, 1, 2]),
    2: (pca1, [3, 4, 5]),
    3: (pca1, [6, 7, 8]),
    4: (pca2, [0, 1, 2]),
    5: (pca2, [3, 4, 5]),
    6: (pca2, [6, 7, 8]),
}

# Movement phases
def lift_leg(pca, femur, tibia):
    set_servo_angle(pca, femur, 45)
    set_servo_angle(pca, tibia, 120)

def lower_leg(pca, femur, tibia):
    set_servo_angle(pca, femur, 90)
    set_servo_angle(pca, tibia, 90)

def move_leg_forward(pca, coxa):
    set_servo_angle(pca, coxa, 60)

def move_leg_backward(pca, coxa):
    set_servo_angle(pca, coxa, 120)

def center_leg(pca, coxa):
    set_servo_angle(pca, coxa, 90)

# Initialize all legs
def center_all():
    print("Centering all legs...")
    for leg in legs.values():
        pca, (coxa, femur, tibia) = leg
        center_leg(pca, coxa)
        lower_leg(pca, femur, tibia)

# Walk forward one cycle
def walk_tripod_step():
    # Tripod 1: 1, 4, 5
    for i in [1, 4, 5]:
        pca, (coxa, femur, tibia) = legs[i]
        lift_leg(pca, femur, tibia)
    time.sleep(0.2)
    for i in [1, 4, 5]:
        pca, (coxa, femur, tibia) = legs[i]
        move_leg_forward(pca, coxa)
    time.sleep(0.2)
    for i in [1, 4, 5]:
        pca, (coxa, femur, tibia) = legs[i]
        lower_leg(pca, femur, tibia)
    
    # Tripod 2: 2, 3, 6
    for i in [2, 3, 6]:
        pca, (coxa, femur, tibia) = legs[i]
        lift_leg(pca, femur, tibia)
    time.sleep(0.2)
    for i in [2, 3, 6]:
        pca, (coxa, femur, tibia) = legs[i]
        move_leg_forward(pca, coxa)
    time.sleep(0.2)
    for i in [2, 3, 6]:
        pca, (coxa, femur, tibia) = legs[i]
        lower_leg(pca, femur, tibia)

    # Move all legs backward to simulate body movement
    for i in legs:
        pca, (coxa, _, _) = legs[i]
        move_leg_backward(pca, coxa)
    time.sleep(0.2)
    for i in legs:
        pca, (coxa, _, _) = legs[i]
        center_leg(pca, coxa)
    time.sleep(0.2)

# Main loop
if __name__ == "__main__":
    print("Script started")
    try:
        center_all()
        while True:
            walk_tripod_step()
    except KeyboardInterrupt:
        print("Stopping...")
        center_all()
        pca1.deinit()
        pca2.deinit()

