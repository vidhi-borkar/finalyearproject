import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize I2C and both PCA9685 boards
i2c = busio.I2C(board.SCL, board.SDA)
pca1 = PCA9685(i2c, address=0x40)
pca2 = PCA9685(i2c, address=0x41) 

for pca in [pca1, pca2]:
    pca.frequency = 50

# Servo angle to duty cycle converter
def set_servo_angle(pca, channel, angle):
    pulse_min = 1000  # 1 ms
    pulse_max = 2000  # 2 ms
    pulse = pulse_min + (angle / 180) * (pulse_max - pulse_min)
    duty = int(pulse / 1000000 * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty

# Define each leg as (pca_driver, (coxa_ch, femur_ch, tibia_ch))
legs = {
    1: (pca1, (0, 1, 2)),
    2: (pca1, (3, 4, 5)),
    3: (pca1, (6, 7, 8)),
    4: (pca2, (0, 1, 2)),
    5: (pca2, (3, 4, 5)),
    6: (pca2, (6, 7, 8)),
}

# Movement functions
def center_leg(pca, coxa, femur, tibia):
    set_servo_angle(pca, coxa, 90)
    set_servo_angle(pca, femur, 90)
    set_servo_angle(pca, tibia, 90)

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

def move_leg_to_center(pca, coxa):
    set_servo_angle(pca, coxa, 90)

# Gait groupings
tripod_A = [1, 4, 5]  # Lift → forward → down → back
tripod_B = [2, 3, 6]

def move_group(group, lift=True, forward=True, lower=True, back=True):
    for leg_id in group:
        pca, (coxa, femur, tibia) = legs[leg_id]
        if lift:
            lift_leg(pca, femur, tibia)
    time.sleep(0.3)

    for leg_id in group:
        pca, (coxa, femur, tibia) = legs[leg_id]
        if forward:
            move_leg_forward(pca, coxa)
    time.sleep(0.3)

    for leg_id in group:
        pca, (coxa, femur, tibia) = legs[leg_id]
        if lower:
            lower_leg(pca, femur, tibia)
    time.sleep(0.3)

    for leg_id in group:
        pca, (coxa, femur, tibia) = legs[leg_id]
        if back:
            move_leg_backward(pca, coxa)
    time.sleep(0.3)

def center_all():
    for leg_id, (pca, (coxa, femur, tibia)) in legs.items():
        center_leg(pca, coxa, femur, tibia)
    time.sleep(1)

# Main gait loop
if __name__ == "__main__":
    print("Centering all legs...")
    center_all()

    print("Starting tripod gait walk...")
    for step in range(3):  # Walk for 3 steps
        move_group(tripod_A)
        move_group(tripod_B)

    print("Returning to neutral position...")
    center_all()

    print("Done.")
    pca1.deinit()
    pca2.deinit()

