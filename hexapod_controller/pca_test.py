from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# Setup I2C
i2c = busio.I2C(SCL, SDA)

# Initialize pca2
pca2 = PCA9685(i2c, address=0x41)  # Make sure address matches your setup (0x41 is common for second PCA)
pca2.frequency = 50  # Standard for servos

# Simple test: Move servo on channel 0 back and forth
try:
    while True:
        # Send pulse to move servo one side
        pca2.channels[0].duty_cycle = 0x6666  # About 1500us pulse (center position)
        time.sleep(1)

        # Send pulse to move servo other side
        pca2.channels[0].duty_cycle = 0x9999  # A little more
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up when Ctrl+C is pressed
    pca2.channels[0].duty_cycle = 0
    print("Stopped.")

