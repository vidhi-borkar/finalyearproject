from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# Initialize I2C bus
i2c = busio.I2C(SCL, SDA)

# Create a PCA9685 object
pca = PCA9685(i2c)

# Set the PWM frequency to 50Hz (standard for servos)
pca.frequency = 50

# Servo channel (0-15)
servo_channel = 2  # Change this depending on your connection

def set_servo_angle(channel, angle):
    """
    Set servo angle for MG996R using PCA9685.

    Args:
        channel (int): PCA9685 channel (0 to 15)
        angle (float): Servo angle (0 to 180 degrees)
    """
    # Convert angle to pulse length between 0 and 65535
    # MG996R expects 0° at ~500us, 90° at ~1500us, 180° at ~2500us
    pulse_min = 1000  # 1 ms
    pulse_max = 2000  # 2 ms
    pulse = pulse_min + (angle / 180) * (pulse_max - pulse_min)

    # Convert pulse to duty cycle (out of 65535)
    duty = int(pulse / 1000000 * pca.frequency * 65535)
    
    pca.channels[channel].duty_cycle = duty

# Example usage
set_servo_angle(servo_channel, 90)
time.sleep(1)
set_servo_angle(servo_channel, 0)
time.sleep(1)
set_servo_angle(servo_channel, 180)
time.sleep(1)

