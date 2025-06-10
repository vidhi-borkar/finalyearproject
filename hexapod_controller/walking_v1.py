import time
from adafruit_servokit import ServoKit
import threading
import sys # For sys.exit

# --- Configuration ---

# Initialize the PCA9685 boards
# Ensure these addresses are correct for your hardware setup
try:
    pca1 = ServoKit(channels=16, address=0x40)
    pca2 = ServoKit(channels=16, address=0x41)
    print("ServoKit instances created successfully.")
except ValueError as e:
    print(f"Error initializing ServoKit: {e}")
    print("Please check I2C connection and addresses (0x40, 0x41).")
    sys.exit(1) # Exit if boards can't be found
except Exception as e:
    print(f"An unexpected error occurred during ServoKit initialization: {e}")
    sys.exit(1)


# Servo pulse width ranges (adjust if necessary for your servos)
# Using a default value assuming all servos are similar
# You could have individual MIN/MAX per servo if needed
SERVO_MIN_PULSE = 500
SERVO_MAX_PULSE = 2500

# Define servo channels and PCA board for each logical leg number (1-6)
# Adjust comments (e.g., Front-Right) based on your robot's physical layout
# Format: leg_num: (pca_object, [coxa_channel, femur_channel, tibia_channel])
LEG_CONFIG = {
    1: (pca1, [0, 1, 2]),  # Leg 1 (e.g., Front-Right on pca1)
    2: (pca1, [3, 4, 5]),  # Leg 2 (e.g., Middle-Right on pca1)
    3: (pca1, [6, 7, 8]),  # Leg 3 (e.g., Back-Right on pca1)
    4: (pca2, [0, 1, 2]),  # Leg 4 (e.g., Front-Left on pca2)
    5: (pca2, [3, 4, 5]),  # Leg 5 (e.g., Middle-Left on pca2)
    6: (pca2, [6, 7, 8]),  # Leg 6 (e.g., Back-Left on pca2)
}

# --- Global State ---
continue_movement = False
movement_thread = None

# --- Core Functions ---

def init_servos():
    """Sets the pulse width range for all servos defined in LEG_CONFIG."""
    print("Initializing servos...")
    for leg_num, (pca, channels) in LEG_CONFIG.items():
        for channel in channels:
            try:
                pca.servo[channel].set_pulse_width_range(SERVO_MIN_PULSE, SERVO_MAX_PULSE)
            except IndexError:
                print(f"Warning: Channel {channel} on PCA {pca.servo.kit_address} might be out of range (0-15). Check LEG_CONFIG.")
            except Exception as e:
                 print(f"Warning: Could not set pulse width for Leg {leg_num}, Channel {channel} on PCA {pca.servo.kit_address}. Error: {e}")
    print("Servo initialization complete.")

def move_leg(leg_num, angles):
    """
    Moves a single specified leg to the given angles.
    Args:
        leg_num (int): The logical leg number (1-6).
        angles (list/tuple): A list of three angles [coxa, femur, tibia].
    """
    if leg_num not in LEG_CONFIG:
        print(f"Error: Invalid leg number {leg_num}.")
        return
    if len(angles) != 3:
        print(f"Error: Invalid angles list length for leg {leg_num}. Expected 3, got {len(angles)}.")
        return

    pca, channels = LEG_CONFIG[leg_num]
    coxa_pin, femur_pin, tibia_pin = channels

    # Apply angles safely
    try:
        # Clamp angles to a safe range (0-180 typically, adjust if needed)
        safe_angles = [max(0, min(180, angle)) for angle in angles]

        pca.servo[coxa_pin].angle = safe_angles[0]
        pca.servo[femur_pin].angle = safe_angles[1]
        pca.servo[tibia_pin].angle = safe_angles[2]
    except IndexError:
         print(f"Warning: Channel index error for Leg {leg_num} on PCA {pca.servo.kit_address}. Check LEG_CONFIG.")
    except Exception as e:
        # Catch potential communication errors or other servo issues
        print(f"Error moving Leg {leg_num}: {e}")


def move_all_legs(angles_dict, delay=0.0):
    """
    Moves all legs according to the angles specified in the dictionary.
    Args:
        angles_dict (dict): Dictionary where keys are leg numbers (1-6)
                            and values are lists of angles [coxa, femur, tibia].
        delay (float): Optional delay in seconds after moving all legs.
    """
    for leg_num, angles in angles_dict.items():
        move_leg(leg_num, angles)
    if delay > 0:
        time.sleep(delay)

def go_to_pose(pose_dict, delay=0.2):
    """Helper function to move to a pose and wait."""
    move_all_legs(pose_dict)
    time.sleep(delay)


# --- Standard Poses ---

REST_POS = {leg: [90, 30, 0] for leg in range(1, 7)} # Legs slightly folded
STAND_INIT_POS = {leg: [90, 0, 0] for leg in range(1, 7)} # Legs fully folded under
STAND_FINAL_POS = {leg: [90, 90, 0] for leg in range(1, 7)} # Standard standing pose

def stand_up():
    """Moves the robot from a likely rest/folded state to a standing position."""
    print("Standing up...")
    move_all_legs(STAND_INIT_POS, delay=0.5)
    move_all_legs(STAND_FINAL_POS, delay=1.0) # Give time to stabilize
    print("Standing position reached.")

def go_to_rest():
    """Moves the robot to a resting position."""
    print("Going to rest position...")
    move_all_legs(REST_POS, delay=0.5)
    # Optional: Release servos to save power and prevent buzzing
    # for leg_num, (pca, channels) in LEG_CONFIG.items():
    #     for channel in channels:
    #         try:
    #             pca.servo[channel].angle = None # Release servo
    #         except Exception: pass # Ignore errors during release
    print("Rest position reached.")


# --- Gait Sequences ---
# Note: Tibia angle is often kept simple (e.g., 0) in these examples.
# Real-world walking often requires more complex tibia control via IK.
# Comments now reflect the logical leg number (1-6) the angles apply to.

# Tripod gait: Legs 2, 4, 6 move together, then 1, 3, 5 move together.

# --- FORWARD ---
FWD_STEP_DURATION = 0.2 # Seconds per step part
FWD_POSE1 = { # Lift 2,4,6
    1: [116, 90, 0],  # Leg 1 Stance
    2: [79,  60, 0],  # Leg 2 Swing Start
    3: [90,  90, 0],  # Leg 3 Stance
    4: [121, 60, 0],  # Leg 4 Swing Start
    5: [84,  90, 0],  # Leg 5 Stance
    6: [83,  60, 0],  # Leg 6 Swing Start
}
FWD_POSE2 = { # Place 2,4,6 forward
    1: [116, 90, 0],  # Leg 1 Stance
    2: [79,  90, 0],  # Leg 2 Swing End (Down)
    3: [90,  90, 0],  # Leg 3 Stance
    4: [121, 90, 0],  # Leg 4 Swing End (Down)
    5: [84,  90, 0],  # Leg 5 Stance
    6: [83,  90, 0],  # Leg 6 Swing End (Down)
}
FWD_POSE3 = { # Lift 1,3,5
    1: [116, 60, 0],  # Leg 1 Swing Start
    2: [79,  90, 0],  # Leg 2 Stance
    3: [90,  60, 0],  # Leg 3 Swing Start
    4: [121, 90, 0],  # Leg 4 Stance
    5: [84,  60, 0],  # Leg 5 Swing Start
    6: [83,  90, 0],  # Leg 6 Stance
}
FWD_POSE4 = { # Place 1,3,5 forward
    1: [99,  60, 0],  # Leg 1 Swing Mid
    2: [101, 90, 0],  # Leg 2 Stance (Shift)
    3: [59,  60, 0],  # Leg 3 Swing Mid
    4: [90,  90, 0],  # Leg 4 Stance (Shift)
    5: [101, 60, 0],  # Leg 5 Swing Mid
    6: [64,  90, 0],  # Leg 6 Stance (Shift)
}
FWD_POSE5 = { # Place 1,3,5 forward (Down)
    1: [99,  90, 0],  # Leg 1 Swing End (Down)
    2: [101, 90, 0],  # Leg 2 Stance
    3: [59,  90, 0],  # Leg 3 Swing End (Down)
    4: [90,  90, 0],  # Leg 4 Stance
    5: [101, 90, 0],  # Leg 5 Swing End (Down)
    6: [64,  90, 0],  # Leg 6 Stance
}
FWD_POSE6 = { # Lift 2,4,6 (Prepare for next cycle start) - similar to POSE1 but shifted
    1: [99, 90, 0],   # Leg 1 Stance
    2: [101, 60, 0],  # Leg 2 Swing Start
    3: [59, 90, 0],   # Leg 3 Stance
    4: [90, 60, 0],   # Leg 4 Swing Start
    5: [98, 90, 0],   # Leg 5 Stance - Note: slight adjustment from FWD_POSE1 leg 5
    6: [64, 60, 0],   # Leg 6 Swing Start
}

# Combined sequence for the move_forward thread
FORWARD_SEQUENCE = [
    FWD_POSE1, FWD_POSE2, FWD_POSE3, FWD_POSE4, FWD_POSE5, FWD_POSE6
]

def move_forward():
    """ Executes the forward walking gait sequence repeatedly. """
    global continue_movement
    print("Thread: Starting forward movement.")
    while continue_movement:
        for pose in FORWARD_SEQUENCE:
            if not continue_movement: break # Check flag before each step
            go_to_pose(pose, FWD_STEP_DURATION)
    print("Thread: Stopping forward movement.")
    # Go back to stable standing pose after stopping
    if not continue_movement: # Ensure it was an intentional stop
         move_all_legs(STAND_FINAL_POS, delay=0.1)


# --- BACKWARD --- (Similar structure, define BWD_POSE1-6 and BACKWARD_SEQUENCE)
# TODO: Define backward poses based on original code or re-calculate
# Example structure:
BWD_STEP_DURATION = 0.2
BWD_POSE1 = {leg: [90, 90, 0] for leg in range(1, 7)} # Placeholder
BWD_POSE2 = {leg: [90, 90, 0] for leg in range(1, 7)} # Placeholder
# ... define all 6 backward poses ...
BWD_POSE6 = {leg: [90, 90, 0] for leg in range(1, 7)} # Placeholder

BACKWARD_SEQUENCE = [ BWD_POSE1, BWD_POSE2, BWD_POSE3, BWD_POSE4, BWD_POSE5, BWD_POSE6 ] # Replace with actual poses

def move_backward():
    """ Executes the backward walking gait sequence repeatedly. """
    global continue_movement
    print("Thread: Starting backward movement.")
    # *** Replace BWD_POSES above with the actual angles from your original code ***
    # *** Make sure keys are 1-6 and comments reflect the leg ***
    # *** Example using original 'third_angles' for backward: ***
    BWD_POSE1 = { # Lift 2,4,6 (swing backward prep)
        1: [85, 82, 0],  # Leg 1 Stance
        2: [110, 66, 0], # Leg 2 Swing Start
        3: [45, 82, 0],  # Leg 3 Stance
        4: [90, 66, 0],  # Leg 4 Swing Start
        5: [115, 82, 0], # Leg 5 Stance
        6: [50, 66, 0],  # Leg 6 Swing Start
    }
    BWD_POSE2 = { # Place 2,4,6 backward (Down)
        1: [85, 82, 0],  # Leg 1 Stance
        2: [110, 82, 0], # Leg 2 Swing End (Down)
        3: [45, 82, 0],  # Leg 3 Stance
        4: [90, 82, 0],  # Leg 4 Swing End (Down)
        5: [115, 82, 0], # Leg 5 Stance
        6: [50, 82, 0],  # Leg 6 Swing End (Down)
    }
    # ... continue translating the original backward angles ('fourth', 'semifourth', etc.)
    # ... into BWD_POSE3, BWD_POSE4, BWD_POSE5, BWD_POSE6 ...
    # Ensure you have 6 distinct poses for a full cycle.
    print("Warning: Backward gait poses might be incomplete/placeholders.") # Add this warning until fully translated

    while continue_movement:
        # Use BACKWARD_SEQUENCE once all poses are defined
        # For now, just demonstrating with the first two:
        if not continue_movement: break
        go_to_pose(BWD_POSE1, BWD_STEP_DURATION)
        if not continue_movement: break
        go_to_pose(BWD_POSE2, BWD_STEP_DURATION)
        # Add the rest of the BWD_POSE steps here...

    print("Thread: Stopping backward movement.")
    if not continue_movement:
         move_all_legs(STAND_FINAL_POS, delay=0.1)

# --- ROTATE RIGHT --- (Define ROT_R_POSE1-6 and ROTATE_RIGHT_SEQUENCE)
ROT_STEP_DURATION = 0.2
# TODO: Define rotate right poses based on original code or re-calculate
# Ensure keys are 1-6 and comments reflect the leg.
# Example structure:
ROT_R_POSE1 = { # Lift 2,4,6, swing CW
    1: [68, 82, 0],  # Leg 1 Stance (Push CCW)
    2: [112, 66, 0], # Leg 2 Swing Start (CW)
    3: [68, 82, 0],  # Leg 3 Stance (Push CCW)
    4: [112, 66, 0], # Leg 4 Swing Start (CW)
    5: [68, 82, 0],  # Leg 5 Stance (Push CCW)
    6: [112, 66, 0], # Leg 6 Swing Start (CW)
}
ROT_R_POSE2 = { # Place 2,4,6 down
    1: [68, 82, 0],  # Leg 1 Stance
    2: [112, 82, 0], # Leg 2 Swing End (Down)
    3: [68, 82, 0],  # Leg 3 Stance
    4: [112, 82, 0], # Leg 4 Swing End (Down)
    5: [68, 82, 0],  # Leg 5 Stance
    6: [112, 82, 0], # Leg 6 Swing End (Down)
}
# ... Define ROT_R_POSE3 (Lift 1,3,5), ROT_R_POSE4 (Swing 1,3,5 CW),
# ... ROT_R_POSE5 (Place 1,3,5 down), ROT_R_POSE6 (Lift 2,4,6 prep) ...

ROTATE_RIGHT_SEQUENCE = [ROT_R_POSE1, ROT_R_POSE2, ...] # Add all 6 poses

def rotate_right():
    """ Executes the rotate right gait sequence repeatedly. """
    global continue_movement
    print("Thread: Starting rotate right.")
    print("Warning: Rotate Right gait poses might be incomplete/placeholders.") # Add this warning until fully translated

    while continue_movement:
        # Use ROTATE_RIGHT_SEQUENCE once all poses are defined
        # For now, just demonstrating:
        if not continue_movement: break
        go_to_pose(ROT_R_POSE1, ROT_STEP_DURATION)
        if not continue_movement: break
        go_to_pose(ROT_R_POSE2, ROT_STEP_DURATION)
        # Add the rest of the ROT_R_POSE steps here...

    print("Thread: Stopping rotate right.")
    if not continue_movement:
         move_all_legs(STAND_FINAL_POS, delay=0.1)


# --- ROTATE LEFT --- (Define ROT_L_POSE1-6 and ROTATE_LEFT_SEQUENCE)
ROT_STEP_DURATION = 0.2
# TODO: Define rotate left poses based on original code or re-calculate
# Ensure keys are 1-6 and comments reflect the leg.
# Example structure (mirrors rotate right):
ROT_L_POSE1 = { # Lift 2,4,6, swing CCW
    1: [112, 82, 0], # Leg 1 Stance (Push CW)
    2: [68, 66, 0],  # Leg 2 Swing Start (CCW)
    3: [112, 82, 0], # Leg 3 Stance (Push CW)
    4: [68, 66, 0],  # Leg 4 Swing Start (CCW)
    5: [112, 82, 0], # Leg 5 Stance (Push CW)
    6: [68, 66, 0],  # Leg 6 Swing Start (CCW)
}
ROT_L_POSE2 = { # Place 2,4,6 down
    1: [112, 82, 0], # Leg 1 Stance
    2: [68, 82, 0],  # Leg 2 Swing End (Down)
    3: [112, 82, 0], # Leg 3 Stance
    4: [68, 82, 0],  # Leg 4 Swing End (Down)
    5: [112, 82, 0], # Leg 5 Stance
    6: [68, 82, 0],  # Leg 6 Swing End (Down)
}
# ... Define ROT_L_POSE3 (Lift 1,3,5), ROT_L_POSE4 (Swing 1,3,5 CCW),
# ... ROT_L_POSE5 (Place 1,3,5 down), ROT_L_POSE6 (Lift 2,4,6 prep) ...

ROTATE_LEFT_SEQUENCE = [ROT_L_POSE1, ROT_L_POSE2, ...] # Add all 6 poses


def rotate_left():
    """ Executes the rotate left gait sequence repeatedly. """
    global continue_movement
    print("Thread: Starting rotate left.")
    print("Warning: Rotate Left gait poses might be incomplete/placeholders.") # Add this warning until fully translated

    while continue_movement:
        # Use ROTATE_LEFT_SEQUENCE once all poses are defined
        # For now, just demonstrating:
        if not continue_movement: break
        go_to_pose(ROT_L_POSE1, ROT_STEP_DURATION)
        if not continue_movement: break
        go_to_pose(ROT_L_POSE2, ROT_STEP_DURATION)
        # Add the rest of the ROT_L_POSE steps here...

    print("Thread: Stopping rotate left.")
    if not continue_movement:
        move_all_legs(STAND_FINAL_POS, delay=0.1)

# --- Main Control ---

def stop_current_movement():
    """Sets the flag to stop movement and waits for the thread to finish."""
    global continue_movement, movement_thread
    if movement_thread and movement_thread.is_alive():
        print("Stopping current movement...")
        continue_movement = False
        movement_thread.join() # Wait for the thread to complete its last cycle
        print("Movement stopped.")
        movement_thread = None
    else:
        # If no thread is active, ensure robot is standing still
        move_all_legs(STAND_FINAL_POS, delay=0.1)


def main():
    """Main function to initialize and handle user input."""
    global continue_movement, movement_thread

    init_servos()
    stand_up()

    try:
        while True:
            print("\n--- Robot Control ---")
            print(" w - Move forward")
            print(" s - Move backward")
            print(" a - Rotate left")
            print(" d - Rotate right")
            print(" r - Go to Rest")
            print(" t - Stand Up")
            print(" x - Exit")
            print("---------------------")

            # FIX: Added .lower() call
            choice = input("Enter your choice: ").strip().lower()

            # Stop any existing movement before starting a new one or exiting
            if choice in ['w', 's', 'a', 'd', 'r', 't', 'x']:
                 stop_current_movement()

            if choice == 'w':
                if not (movement_thread and movement_thread.is_alive()):
                    print("Starting forward movement...")
                    continue_movement = True
                    # Use daemon=True so thread doesn't block program exit
                    movement_thread = threading.Thread(target=move_forward, daemon=True)
                    movement_thread.start()
                else:
                     print("Error: Could not stop previous movement thread.")

            elif choice == 's':
                if not (movement_thread and movement_thread.is_alive()):
                    print("Starting backward movement...")
                    continue_movement = True
                    movement_thread = threading.Thread(target=move_backward, daemon=True)
                    movement_thread.start()
                else:
                     print("Error: Could not stop previous movement thread.")

            elif choice == 'a':
                 if not (movement_thread and movement_thread.is_alive()):
                    print("Starting rotate left...")
                    continue_movement = True
                    movement_thread = threading.Thread(target=rotate_left, daemon=True)
                    movement_thread.start()
                 else:
                     print("Error: Could not stop previous movement thread.")

            elif choice == 'd':
                 if not (movement_thread and movement_thread.is_alive()):
                    print("Starting rotate right...")
                    continue_movement = True
                    movement_thread = threading.Thread(target=rotate_right, daemon=True)
                    movement_thread.start()
                 else:
                     print("Error: Could not stop previous movement thread.")

            elif choice == 'r':
                go_to_rest()

            elif choice == 't':
                stand_up()

            elif choice == 'x':
                print("Exiting program.")
                break # Exit the while loop

            else:
                print("Invalid choice. Please try again.")

            # If a movement was started, prompt to press Enter (optional)
            # This version allows continuous commands without waiting for Enter
            # If you WANT the "Press Enter to stop" behavior, uncomment below:
            # if movement_thread and movement_thread.is_alive():
            #    input("Movement started. Press Enter to stop...")
            #    stop_current_movement()

    except KeyboardInterrupt:
        print("\nCtrl+C detected. Stopping robot and exiting.")
    finally:
        # --- Cleanup ---
        print("Performing cleanup...")
        stop_current_movement() # Ensure any running thread is stopped
        go_to_rest() # Move to a safe position before exiting
        print("Cleanup complete. Exiting.")
        # Optional: Explicitly release I2C bus? Usually handled by library exit.


if __name__ == "__main__":
    main()
    
