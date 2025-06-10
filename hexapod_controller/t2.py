import RPi.GPIO as GPIO
import time

# Set the GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Define the servo control pin
servo_pin = 37

# Set the PWM frequency
servo_frequency = 50

# Configure the servo pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM object
servo = GPIO.PWM(servo_pin, servo_frequency)

# Start the PWM signal with a 0 duty cycle (initially at the center)
servo.start(0)

def set_servo_angle(angle):
    """
    Sets the servo motor to a specific angle.

    Args:
        angle: The desired angle in degrees (0-180).
    """

    # Calculate the duty cycle for the given angle
    duty_cycle = (angle / 180) * 10 + 5  # Adjust this based on your servo's specifications

    # Change the duty cycle to move the servo
    servo.ChangeDutyCycle(duty_cycle)

    # Wait for the servo to move
    time.sleep(0.5)  # Adjust the delay as needed

# Example usage: Move the servo to 90 degrees
set_servo_angle(90)

# Move the servo to 0 degrees
set_servo_angle(0)

# Stop the PWM and clean up the GPIO pins
servo.stop()
GPIO.cleanup()
