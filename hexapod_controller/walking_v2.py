import time
from adafruit_servokit import ServoKit
import threading

# Initialize the PCA9685 boards
pca1 = ServoKit(channels=16, address=0x40)
pca2 = ServoKit(channels=16, address=0x41)

MIN_IMP = [500] * 9
MAX_IMP = [2500] * 9

# Initialize servo ranges
def init():
    for i in range(9):
        pca1.servo[i].set_pulse_width_range(MIN_IMP[i], MAX_IMP[i])
        pca2.servo[i].set_pulse_width_range(MIN_IMP[i], MAX_IMP[i])

# Define servo channels for each leg
leg_channels = {
    1: [0, 1, 2],   # Leg 1 (PCA1)
    2: [3, 4, 5],   # Leg 2 (PCA1)
    3: [6, 7, 8],   # Leg 3 (PCA1)
    4: [0, 1, 2],   # Leg 4 (PCA2)
    5: [3, 4, 5],   # Leg 5 (PCA2)
    6: [6, 7, 8],   # Leg 6 (PCA2)
}

# Move one leg
def move_leg(pca, leg, angles):
    coxa_pin, femur_pin, tibia_pin = leg_channels[leg]
    pca.servo[coxa_pin].angle = angles[0]
    pca.servo[femur_pin].angle = angles[1]
    pca.servo[tibia_pin].angle = angles[2]

# Function to make the robot stand up
def stand_up(pca1, pca2):
    global continue_movement
    initial_angles = {i: [90, 0, 0] for i in range(1, 7)}
    for leg in range(1, 4):
        move_leg(pca1, leg, initial_angles[leg])
    for leg in range(4, 7):
        move_leg(pca2, leg, initial_angles[leg])
    time.sleep(1)

    second_angles = {i: [90, 90, 0] for i in range(1, 7)}
    for leg in range(1, 4):
        move_leg(pca1, leg, second_angles[leg])
    for leg in range(4, 7):
        move_leg(pca2, leg, second_angles[leg])
    time.sleep(1)

    continue_movement = False

# Placeholder movement functions

def move_forward(pca1, pca2):
    global continue_movement
    while continue_movement:
        # Example cycle - customize as needed
        for leg in range(1, 7):
            angle = [90, 45, 0] if leg % 2 == 0 else [90, 90, 0]
            (pca1 if leg < 4 else pca2).servo[leg_channels[leg][1]].angle = angle[1]
        time.sleep(0.2)
    continue_movement = False

def move_backward(pca1, pca2):
    global continue_movement
    while continue_movement:
        # Example cycle - customize as needed
        for leg in range(1, 7):
            angle = [90, 135, 0] if leg % 2 == 0 else [90, 90, 0]
            (pca1 if leg < 4 else pca2).servo[leg_channels[leg][1]].angle = angle[1]
        time.sleep(0.2)
    continue_movement = False

def rotate_right(pca1, pca2):
    global continue_movement
    while continue_movement:
        for leg in range(1, 7):
            angle = [60, 90, 0] if leg % 2 == 0 else [120, 90, 0]
            (pca1 if leg < 4 else pca2).servo[leg_channels[leg][0]].angle = angle[0]
        time.sleep(0.2)
    continue_movement = False

def rotate_left(pca1, pca2):
    global continue_movement
    while continue_movement:
        for leg in range(1, 7):
            angle = [120, 90, 0] if leg % 2 == 0 else [60, 90, 0]
            (pca1 if leg < 4 else pca2).servo[leg_channels[leg][0]].angle = angle[0]
        time.sleep(0.2)
    continue_movement = False

def main():
    init()
    stand_up(pca1, pca2)
    global continue_movement

    while True:
        print("\nChoose an action:")
        print("w - Move forward")
        print("s - Move backward")
        print("d - Rotate right")
        print("a - Rotate left")
        print("x - Exit")

        choice = input("Enter your choice: ").strip().lower()

        if choice == 'w':
            continue_movement = True
            thread = threading.Thread(target=move_forward, args=(pca1, pca2))
            thread.start()
            input("Press Enter to stop...")
            continue_movement = False
            thread.join()

        elif choice == 's':
            continue_movement = True
            thread = threading.Thread(target=move_backward, args=(pca1, pca2))
            thread.start()
            input("Press Enter to stop...")
            continue_movement = False
            thread.join()

        elif choice == 'd':
            continue_movement = True
            thread = threading.Thread(target=rotate_right, args=(pca1, pca2))
            thread.start()
            input("Press Enter to stop...")
            continue_movement = False
            thread.join()

        elif choice == 'a':
            continue_movement = True
            thread = threading.Thread(target=rotate_left, args=(pca1, pca2))
            thread.start()
            input("Press Enter to stop...")
            continue_movement = False
            thread.join()

        elif choice == 'x':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter one of: w, a, s, d, or x.")

if __name__ == "__main__":
    main()

