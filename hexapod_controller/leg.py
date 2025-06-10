import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize I2C and single PCA9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# Servo angle to duty cycle converter
def set_servo_angle(pca, channel, angle):
    pulse_min = 1000  # 1 ms
    pulse_max = 2000  # 2 ms
    pulse = pulse_min + (angle / 180) * (pulse_max - pulse_min)
    duty = int(pulse / 1000000 * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty

# Define each leg as (coxa_ch, femur_ch, tibia_ch)
legs = {
    1: (0, 1, 2),
    2: (3, 4, 5),
    3: (6, 7, 8),
    4: (9, 10, 11),
    5: (12, 13, 14),
}

# Movement functions
def center_leg(coxa, femur, tibia):
    set_servo_angle(pca, coxa, 90)
    set_servo_angle(pca, femur, 90)
    set_servo_angle(pca, tibia, 90)

def lift_leg(femur, tibia):
    set_servo_angle(pca, femur, 45)
    set_servo_angle(pca, tibia, 120)

def lower_leg(femur, tibia):
    set_servo_angle(pca, femur, 90)
    set_servo_angle(pca, tibia, 90)

def move_leg_forward(coxa):
    set_servo_angle(pca, coxa, 60)

def move_leg_backward(coxa):
    set_servo_angle(pca, coxa, 120)

def move_leg_to_center(coxa):
    set_servo_angle(pca, coxa, 90)

# Gait groupings (modified for 5 legs)
group_A = [1, 3, 5]
group_B = [2, 4]

def move_group(group, lift=True, forward=True, lower=True, back=True):
    for leg_id in group:
        coxa, femur, tibia = legs[leg_id]
        if lift:
            lift_leg(femur, tibia)
    time.sleep(0.3)

    for leg_id in group:
        coxa, femur, tibia = legs[leg_id]
        if forward:
            move_leg_forward(coxa)
    time.sleep(0.3)

    for leg_id in group:
        coxa, femur, tibia = legs[leg_id]
        if lower:
            lower_leg(femur, tibia)
    time.sleep(0.3)

    for leg_id in group:
        coxa, femur, tibia = legs[leg_id]
        if back:
            move_leg_backward(coxa)
    time.sleep(0.3)

def center_all():
    for coxa, femur, tibia in legs.values():
        center_leg(coxa, femur, tibia)
    time.sleep(1)

# Main gait loop
if __name__ == "__main__":
    print("Centering all legs...")
    center_all()

    print("Starting 5-leg forward walk...")
    for step in range(3):  # Walk for 3 steps
        move_group(group_A)
        move_group(group_B)

    print("Returning to neutral position...")
    center_all()

    print("Done.")
    pca.deinit()

