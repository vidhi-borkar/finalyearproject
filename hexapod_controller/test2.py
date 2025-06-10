import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize I2C and PCA9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

def set_servo_angle(channel, angle):
    pulse_min = 1000  # 1 ms
    pulse_max = 2000  # 2 ms
    pulse = pulse_min + (angle / 180) * (pulse_max - pulse_min)
    duty = int(pulse / 1000000 * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty

# Define each leg with channels (coxa, femur, tibia)
legs = {
    1: (0, 1, 2),  # Leg 1 - Front Left
    2: (3, 4, 5),  # Leg 2 - Front Right
    3: (6, 7, 8),  # Leg 3 - Middle Left
}

def center_leg(coxa, femur, tibia):
    set_servo_angle(coxa, 90)
    set_servo_angle(femur, 90)
    set_servo_angle(tibia, 90)

def lift_leg(femur, tibia):
    set_servo_angle(femur, 45)
    set_servo_angle(tibia, 120)

def lower_leg(femur, tibia):
    set_servo_angle(femur, 90)
    set_servo_angle(tibia, 90)

def move_forward(coxa):
    set_servo_angle(coxa, 60)

def move_backward(coxa):
    set_servo_angle(coxa, 120)

def center_all():
    for (coxa, femur, tibia) in legs.values():
        center_leg(coxa, femur, tibia)
    time.sleep(1)

def walk_step(leg_ids):
    # Lift and move forward
    for lid in leg_ids:
        coxa, femur, tibia = legs[lid]
        lift_leg(femur, tibia)
    time.sleep(0.3)
    for lid in leg_ids:
        coxa, femur, tibia = legs[lid]
        move_forward(coxa)
    time.sleep(0.3)
    for lid in leg_ids:
        coxa, femur, tibia = legs[lid]
        lower_leg(femur, tibia)
    time.sleep(0.3)
    for lid in leg_ids:
        coxa, femur, tibia = legs[lid]
        move_backward(coxa)
    time.sleep(0.3)

# Main test loop
if __name__ == "__main__":
    print("Centering legs...")
    center_all()

    print("Walking test with 3 legs...")
    for i in range(3):
        walk_step([1, 2, 3])  # All 3 legs step forward

    print("Returning to center position...")
    center_all()

    print("Done.")
    pca.deinit()

