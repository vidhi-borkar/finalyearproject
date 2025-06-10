import time
from adafruit_servokit import ServoKit
import threading

# Initialize only one PCA9685 (since you're using just one now)
pca1 = ServoKit(channels=16, address=0x40)

MIN_IMP = [500] * 9
MAX_IMP = [2500] * 9

def init():
    for i in range(9):
        pca1.servo[i].set_pulse_width_range(MIN_IMP[i], MAX_IMP[i])

# Define servo channels for each leg
leg_channels = {
    1: [0, 1, 2],  # Leg 1
    2: [3, 4, 5],  # Leg 2
    3: [6, 7, 8],  # Leg 3
}

def move_leg(pca, leg, angles):
    coxa_pin, femur_pin, tibia_pin = leg_channels[leg]
    pca.servo[coxa_pin].angle = angles[0]
    pca.servo[femur_pin].angle = angles[1]
    pca.servo[tibia_pin].angle = angles[2]

def stand_up(pca):
    initial_angles = {
        1: [90, 0, 0],
        2: [90, 0, 0],
        3: [90, 0, 0],
    }
    for leg in range(1, 4):
        move_leg(pca, leg, initial_angles[leg])
    time.sleep(1)

    second_angles = {
        1: [90, 90, 0],
        2: [90, 90, 0],
        3: [90, 90, 0],
    }
    for leg in range(1, 4):
        move_leg(pca, leg, second_angles[leg])
    time.sleep(1)

continue_movement = False

def move_forward(pca):
    global continue_movement
    while continue_movement:
        forward_step1 = {
            1: [100, 60, 0],
            2: [80, 90, 0],
            3: [90, 60, 0],
        }
        for leg in range(1, 4):
            move_leg(pca, leg, forward_step1[leg])
        time.sleep(0.2)

        forward_step2 = {
            1: [100, 90, 0],
            2: [80, 90, 0],
            3: [90, 90, 0],
        }
        for leg in range(1, 4):
            move_leg(pca, leg, forward_step2[leg])
        time.sleep(0.2)
    continue_movement = False

def main():
    init()
    stand_up(pca1)
    global continue_movement

    while True:
        print("\nChoose an action:")
        print("w - Move forward")
        print("x - Exit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == 'w':
            continue_movement = True
            threading.Thread(target=move_forward, args=(pca1,)).start()
            input("Press Enter to stop...")
            continue_movement = False

        elif choice == 'x':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter one of: w or x.")

if __name__ == "__main__":
    main()
