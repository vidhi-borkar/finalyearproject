import board
import busio
from adafruit_pca9685 import PCA9685

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize both PCA9685 boards with different I2C addresses
pca1 = PCA9685(i2c, address=0x41)
pca2 = PCA9685(i2c, address=0x40)

# Set PWM frequency
pca1.frequency = 50
pca2.frequency = 50

# Turn off all channels (set duty_cycle to 0)
for i in range(16):
    pca1.channels[i].duty_cycle = 0
    pca2.channels[i].duty_cycle = 0

# Deinitialize devices
pca1.deinit()
pca2.deinit()

