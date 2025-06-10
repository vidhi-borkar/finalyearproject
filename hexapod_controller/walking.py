import time
from adafruit_servokit import ServoKit
import threading

# Initialize the PCA9685 boards
pca1 = ServoKit (channels=16, address=0x40)
pca2 = ServoKit (channels=16, address=0x41)

MIN_IMP = [500, 500, 500, 500, 500, 500, 500, 500, 500]
MAX_IMP = [2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500]

def init():
    for i in range(9):
        pca1.servo[i].set_pulse_width_range (MIN_IMP[i], MAX_IMP [i])

    for i in range (9):
        pca2.servo[i].set_pulse_width_range (MIN_IMP[i], MAX_IMP [i])

# Define servo channels for each leg
leg_channels = {
    1: [0,1,2], # Leg 1 (PCA1)
    2: [3,4,5], # Leg 2 (PCA1)
    3: [6,7,8], # Leg 3 (PCA1)
    4: [0,1,2], # Leg 4 (PCA2)
    5: [3,4,5], # Leg 5 (PCA2)
    6: [6,7,8], # Leg 6 (PCA2)
}

# Function to move a single leg
def move_leg(pca, leg, angles):
    coxa_pin, femur_pin, tibia_pin = leg_channels [leg]
    pca.servo[coxa_pin].angle = angles[0]
    pca.servo[femur_pin].angle = angles[1]
    pca.servo[tibia_pin].angle = angles[2]

# Functton to make the robot stand up
def stand_up(pca1, pca2):
    # Define the initial angles for a standing position
    initial_angles = {
        1: [90, 0, 0], # Leg 4
        2: [90, 0, 0], # Leg 5
        3: [90, 0, 0], # Leg 6
        4: [90, 0, 0], # Leg 1
        5: [90, 0, 0], # Leg 2
        6: [90, 0, 0], # Leg 3
    }

    # Move all legs to the initial angles
    for leg in range(1, 4):
        move_leg(pca1, leg, initial_angles[leg])

    for leg in range(4, 7):
        move_leg(pca2, leg, initial_angles[leg])

    # Wait for 1 seconds
    time.sleep (1)

    # Define the second set of angles
    second_angles = {
        1: [90, 90, 0], # Leg 4
        2: [90, 90, 0], # Leg 5
        3: [90, 90, 0], # Leg 6
        4: [90, 90, 0], # Leg 1
        5: [90, 90, 0], # Leg 2
        6: [90, 90, 0], # Leg 3
    }

    # Move all legs to the second angles
    for leg in range(1, 4):
        move_leg(pca1, leg, second_angles[leg])

    for leg in range(4, 7):
        move_leg(pca2, leg, second_angles[leg])

    # wait for 1 seconds
    time.sleep (1)
    
    continue_movement = False

# Function to move forward
def move_forward(pca1, pca2):
    global continue_movement
    while continue_movement:
        # Define the beginning of Leg 2,4,6 swing phase
        third_angles = {
            1: [121, 60, 0],# Leg 4
            2: [84, 90, 0],# Leg 5
            3: [83, 60, 0],# Leg 6
            4: [116, 90, 0],# Leg 1
            5: [79, 60, 0],# Leg 2
            6: [90, 90, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, third_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, third_angles[leg])

        time.sleep (0.2)

        # Define the ending of 2,4,6 swing phase all the legs are down
        fourth_angles = {
            1: [121, 90, 0],# Leg 4
            2: [84, 90, 0],# Leg 5
            3: [83, 90, 0],# Leg 6
            4: [116, 90, 0],# Leg 1
            5: [79, 90, 0],# Leg 2
            6: [90, 90, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fourth_angles[leg])

        time.sleep (0.2)

        #the ending of 2,4,6 swing phase 1,3,5 are up
        semifourth_angles = {
            1: [121, 90, 0],# Leg 4
            2: [84, 60, 0],# Leg 5
            3: [83, 90, 0],# Leg 6
            4: [116, 60, 0],# Leg 1
            5: [79, 90, 0],# Leg 2
            6: [90, 60, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semifourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semifourth_angles[leg])

        time.sleep (0.2)

        # Define the beginning of 1,3,5 swing phase
        fifth_angles = {
            1: [90, 90, 0],# Leg 4
            2: [101, 60, 0],# Leg 5
            3: [64, 90, 0],# Leg 6
            4: [99, 60, 0],# Leg 1
            5: [98, 90, 0],# Leg 2
            6: [59, 60, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fifth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fifth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase  all the legs are down
        sixth_angles = {
            1: [90, 90, 0],# Leg 4
            2: [101, 90, 0],# Leg 5
            3: [64, 90, 0],# Leg 6
            4: [99, 90, 0],# Leg 1
            5: [98, 90, 0],# Leg 2
            6: [59, 90, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, sixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, sixth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase
        semisixth_angles = {
            1: [90, 60, 0],# Leg 4
            2: [101, 90, 0],# Leg 5
            3: [64, 60, 0],# Leg 6
            4: [99, 90, 0],# Leg 1
            5: [98, 60, 0],# Leg 2
            6: [59, 90, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semisixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semisixth_angles[leg])

        time.sleep (0.2)
        
    continue_movement = False
    #Reset 

# Function to move backward
def move_backward(pca1, pca2):
    global continue_movement
    while continue_movement:
        # Define the beginning of Leg 2,4,6 swing phase
        third_angles = {
            1: [90, 66, 0],# Leg 4
            2: [115, 82, 0],# Leg 5
            3: [50, 66, 0],# Leg 6
            4: [85, 82, 0],# Leg 1
            5: [110, 66, 0],# Leg 2
            6: [45, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, third_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, third_angles[leg])

        time.sleep (0.2)

        # Define the ending of 2,4,6 swing phase all the legs are down
        fourth_angles = {
            1: [90, 82, 0],# Leg 4
            2: [115, 82, 0],# Leg 5
            3: [50, 82, 0],# Leg 6
            4: [85, 82, 0],# Leg 1
            5: [110, 82, 0],# Leg 2
            6: [45, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fourth_angles[leg])

        time.sleep (0.2)

        #the ending of 2,4,6 swing phase 1,3,5 are up
        semifourth_angles = {
            1: [90, 82, 0],# Leg 4
            2: [115, 66, 0],# Leg 5
            3: [50, 82, 0],# Leg 6
            4: [85, 66, 0],# Leg 1
            5: [110,82, 0],# Leg 2
            6: [45, 66, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semifourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semifourth_angles[leg])

        time.sleep (0.2)

        # Define the beginning of 1,3,5 swing phase
        fifth_angles = {
            1: [135, 82, 0],# Leg 4
            2: [70, 66, 0],# Leg 5
            3: [95, 82, 0],# Leg 6
            4: [130, 66, 0],# Leg 1
            5: [65, 82, 0],# Leg 2
            6: [90, 66, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fifth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fifth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase  
        sixth_angles = {
            1: [135, 82, 0],# Leg 4
            2: [70, 82, 0],# Leg 5
            3: [95, 82, 0],# Leg 6
            4: [130, 82, 0],# Leg 1
            5: [65, 82, 0],# Leg 2
            6: [90, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, sixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, sixth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase
        semisixth_angles = {
            1: [135, 66, 0],# Leg 4
            2: [70, 82, 0],# Leg 5
            3: [95, 66, 0],# Leg 6
            4: [130, 82, 0],# Leg 1
            5: [65, 66, 0],# Leg 2
            6: [90, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semisixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semisixth_angles[leg])

        time.sleep (0.2)
        
    continue_movement = False
    # Reset the flag once movement stops

# Function to rotate right
def rotate_right(pca1, pca2):
    global continue_movement
    while continue_movement:
        # Define the beginning of 2,4,6 swing phase
        third_angles = {
            1: [112, 66, 0],# Leg 4
            2: [68, 82, 0],# Leg 5
            3: [112, 66, 0],# Leg 6
            4: [68, 82, 0],# Leg 1
            5: [112, 66, 0],# Leg 2
            6: [68, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, third_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, third_angles[leg])

        time.sleep (0.2)

        # Define the ending of 2,4,6 swing phase all the legs are down
        fourth_angles = {
            1: [112, 82, 0],# Leg 4
            2: [68, 82, 0],# Leg 5
            3: [112, 82, 0],# Leg 6
            4: [68, 82, 0],# Leg 1
            5: [112, 82, 0],# Leg 2
            6: [68, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fourth_angles[leg])

        time.sleep (0.2)

        #the ending of 2,4,6 swing phase 1,3,5 are up
        semifourth_angles = {
            1: [112, 82, 0],# Leg 4
            2: [68, 66, 0],# Leg 5
            3: [112, 82, 0],# Leg 6
            4: [68, 66, 0],# Leg 1
            5: [112, 82, 0],# Leg 2
            6: [68, 66, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semifourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semifourth_angles[leg])

        time.sleep (0.2)

        # Define the beginning of 1,3,5 swing phase
        fifth_angles = {
            1: [68, 82, 0],# Leg 4
            2: [112, 66, 0],# Leg 5
            3: [68, 82, 0],# Leg 6
            4: [112, 66, 0],# Leg 1
            5: [68, 82, 0],# Leg 2
            6: [112, 66, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fifth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fifth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase  
        sixth_angles = {
            1: [68, 82, 0],# Leg 4
            2: [112, 82, 0],# Leg 5
            3: [68, 82, 0],# Leg 6
            4: [112, 82, 0],# Leg 1
            5: [68, 82, 0],# Leg 2
            6: [112, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, sixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, sixth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase
        semisixth_angles = {
            1: [68, 66, 0],# Leg 4
            2: [112, 82, 0],# Leg 5
            3: [68, 66, 0],# Leg 6
            4: [112, 82, 0],# Leg 1
            5: [68, 66, 0],# Leg 2
            6: [112, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semisixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semisixth_angles[leg])

        time.sleep (0.2)
    continue_movement = False
    # Reset the flag once movement stops

# Function to rotate right
def rotate_left(pca1, pca2):
    global continue_movement
    while continue_movement:
        # Define the beginning of 2,4,6 swing phase
        third_angles = {
            1: [68, 66, 0],# Leg 4
            2: [112, 82, 0],# Leg 5
            3: [68, 66, 0],# Leg 6
            4: [112, 82, 0],# Leg 1
            5: [68, 66, 0],# Leg 2
            6: [112, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, third_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, third_angles[leg])

        time.sleep (0.2)

        # Define the ending of 2,4,6 swing phase all the legs are down
        fourth_angles = {
            1: [68, 82, 0],# Leg 4
            2: [112, 82, 0],# Leg 5
            3: [68, 82, 0],# Leg 6
            4: [112, 82, 0],# Leg 1
            5: [68, 82, 0],# Leg 2
            6: [112, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fourth_angles[leg])

        time.sleep (0.2)

        #the ending of 2,4,6 swing phase 1,3,5 are up
        semifourth_angles = {
            1: [68, 82, 0],# Leg 4
            2: [112, 66, 0],# Leg 5
            3: [68, 82, 0],# Leg 6
            4: [112, 66, 0],# Leg 1
            5: [68, 82, 0],# Leg 2
            6: [112, 66, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semifourth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semifourth_angles[leg])

        time.sleep (0.2)

        # Define the beginning of 1,3,5 swing phase
        fifth_angles = {
            1: [112, 82, 0],# Leg 4
            2: [68, 66, 0],# Leg 5
            3: [112, 82, 0],# Leg 6
            4: [68, 66, 0],# Leg 1
            5: [112, 82, 0],# Leg 2
            6: [68, 66, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, fifth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, fifth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase  
        sixth_angles = {
            1: [112, 82, 0],# Leg 4
            2: [68, 82, 0],# Leg 5
            3: [112, 82, 0],# Leg 6
            4: [68, 82, 0],# Leg 1
            5: [112, 82, 0],# Leg 2
            6: [68, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, sixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, sixth_angles[leg])

        time.sleep (0.2)

        # Define the ending of 1,3,5 swing phase
        semisixth_angles = {
            1: [112, 66, 0],# Leg 4
            2: [68, 82, 0],# Leg 5
            3: [112, 66, 0],# Leg 6
            4: [68, 82, 0],# Leg 1
            5: [112, 66, 0],# Leg 2
            6: [68, 82, 0],# Leg 3
        }

        for leg in range(1, 4):
            move_leg(pca1, leg, semisixth_angles[leg])

        for leg in range(4, 7):
            move_leg(pca2, leg, semisixth_angles[leg])

        time.sleep (0.2)
    continue_movement = False
    # Reset the flag once movement stops

def main():
    init() # Initialize the robot
    stand_up(pca1, pca2) # Stand up the robot

    #Declare the global variable to control movement
    global continue_movement

    while True:
        # Start an infinite loop to continuously take user input
        # Print the available actions to the user
        print (" \nChoose an action:")
        print ("w - Move forward")
        print ("s - Move backward")
        print ("d - Rotate right")
        print ("a - Rotate left")
        print ("x - Exit")

        #Get user input,strip any extra spaces,and convert to lowercase
        choice = input("Enter your choice: ").strip().lower()

        if choice == 'w':
            continue_movement = True
            # Set the movement flag to True
            # Start a new thread to handle forward movement
            threading.Thread(target=move_forward,args=(pca1, pca2)).start()
            input ("Press Enter to stop...")
            # Wait for the user to press Enter
            continue_movement = False # Stop the movement

        elif choice == 's':
            continue_movement = True
            threading.Thread (target=move_backward, args=(pca1, pca2)).start()
            input ("Press Enter to stop...")
            continue_movement = False

        elif choice == 'd':
            continue_movement = True
            threading.Thread(target=rotate_right ,args=(pca1, pca2)).start() 
            input ("Press Enter to stop...") 
            continue_movement = False

        elif choice == 'a':
            continue_movement = True
            threading.Thread(target=rotate_left, args=(pca1, pca2)).start()
            input("Press Enter to stop...")
            continue_movement = False

        elif choice == 'x':  # If user chooses to exit
            print ("Exiting...")
            break
        
        else:
            print ("Invalid choice. Please enter one of: w,a,s,d,or x.") # If user enters an invalid chotce


if __name__ == "__main__":
    main() # Call the main function to start the program0
