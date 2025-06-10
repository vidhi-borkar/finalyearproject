from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

# I2C setup
i2c = busio.I2C(SCL, SDA)

# Create PCA9685 instance
pca = PCA9685(i2c)
pca.frequency = 50  # 50Hz for servo control

def set_servo_pulse_us(channel, pulse_us):
    # 1 cycle = 20,000 us (50 Hz), 16-bit resolution
    pulse_length = 1000000 / pca.frequency   # 20,000 us
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

## Neutral (stop)
set_servo_pulse_us(3, 1500)
time.sleep(0.4)

# Rotate forward (example)
set_servo_pulse_us(3, 1600)
time.sleep(0.4)

# Rotate reverse (example)
set_servo_pulse_us(3, 1400)
time.sleep(0.8)

# Stop again
set_servo_pulse_us(3, 1500)

