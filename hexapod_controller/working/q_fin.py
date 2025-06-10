import threading
import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# I2C setup
i2c = busio.I2C(SCL, SDA)

# PCA9685 instances
pca1 = PCA9685(i2c, address=0x40)
pca2 = PCA9685(i2c, address=0x41)

pca1.frequency = 50
pca2.frequency = 50

# Helper
def set_servo_pulse_us(pca, channel, pulse_us):
    pulse_length = 1000000 / pca.frequency
    duty_cycle = int((pulse_us / pulse_length) * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# Constants
NEUTRAL = 1500
FWD_FEM = 1400
REV_FEM = 1615
FWD_TIB = 1401
REV_TIB = 1600
FWD_COXA = 1450
REV_COXA = 1630
STAND_FEM = 1450
STAND_TIB = 1550

# Leg channels
legs = {
    'L1': [pca1, 0, 1, 2],
    'L2': [pca1, 3, 4, 5],
    'L3': [pca1, 6, 7, 8],
    'L4': [pca2, 0, 1, 2],
    'L5': [pca2, 3, 4, 5],
    'L6': [pca2, 6, 7, 8]
}

# STAND posture
def stand():
    print("Standing posture...")
    for pca, coxa_ch, femur_ch, tibia_ch in legs.values():
        set_servo_pulse_us(pca, coxa_ch, NEUTRAL)
        set_servo_pulse_us(pca, femur_ch, STAND_FEM)
        set_servo_pulse_us(pca, tibia_ch, STAND_TIB)
    time.sleep(1)

# Control functions
def move_all_legs_forward1():
    for leg in ['L1', 'L3', 'L5']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, REV_FEM)
        set_servo_pulse_us(pca, tibia_ch, FWD_TIB)
    time.sleep(0.5)
    stop_all_legs()

def move_all_legs_forward2():
    for leg in ['L2', 'L4', 'L6']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, FWD_FEM)
        set_servo_pulse_us(pca, tibia_ch, REV_TIB)
    time.sleep(0.5)
    stop_all_legs()

def move_all_legs_backward1():
    for leg in ['L1', 'L3', 'L5']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, FWD_FEM)
        set_servo_pulse_us(pca, tibia_ch, REV_TIB)
    time.sleep(0.5)
    stop_all_legs()

def move_all_legs_backward2():
    for leg in ['L2', 'L4', 'L6']:
        pca, coxa_ch, femur_ch, tibia_ch = legs[leg]
        set_servo_pulse_us(pca, femur_ch, REV_FEM)
        set_servo_pulse_us(pca, tibia_ch, FWD_TIB)
    time.sleep(0.5)
    stop_all_legs()

def move_all_coxa_forward1():
    threads = []
    for leg, pulse in zip(['L1', 'L3', 'L5'], [FWD_COXA, FWD_COXA, REV_COXA]):
        pca, coxa_ch, _, _ = legs[leg]
        t = threading.Thread(target=set_servo_pulse_us, args=(pca, coxa_ch, pulse))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    time.sleep(0.5)
    stop_all_legs()

def move_all_coxa_forward2():
    threads = []
    for leg, pulse in zip(['L4', 'L6', 'L2'], [REV_COXA, REV_COXA, FWD_COXA]):
        pca, coxa_ch, _, _ = legs[leg]
        t = threading.Thread(target=set_servo_pulse_us, args=(pca, coxa_ch, pulse))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    time.sleep(0.5)
    stop_all_legs()

def move_all_coxa_backward1():
    threads = []
    for leg, pulse in zip(['L1', 'L3', 'L5'], [REV_COXA, REV_COXA, FWD_COXA]):
        pca, coxa_ch, _, _ = legs[leg]
        t = threading.Thread(target=set_servo_pulse_us, args=(pca, coxa_ch, pulse))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    time.sleep(0.5)
    stop_all_legs()

def move_all_coxa_backward2():
    threads = []
    for leg, pulse in zip(['L4', 'L6', 'L2'], [FWD_COXA, FWD_COXA, REV_COXA]):
        pca, coxa_ch, _, _ = legs[leg]
        t = threading.Thread(target=set_servo_pulse_us, args=(pca, coxa_ch, pulse))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    time.sleep(0.5)
    stop_all_legs()

def stop_all_legs():
    for pca, coxa_ch, femur_ch, tibia_ch in legs.values():
        set_servo_pulse_us(pca, coxa_ch, NEUTRAL)
        set_servo_pulse_us(pca, femur_ch, NEUTRAL)
        set_servo_pulse_us(pca, tibia_ch, NEUTRAL)

def turn_left1():
    for leg in ['L1', 'L3', 'L5']:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, FWD_COXA)
    time.sleep(0.5)
    stop_all_legs()

def turn_left2():
    for leg in ['L2', 'L4', 'L6']:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, FWD_COXA)
    time.sleep(0.5)
    stop_all_legs()

def rotate_left():
    for leg in legs:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, REV_COXA)
    time.sleep(0.5)
    stop_all_legs()

def turn_right1():
    for leg in ['L1', 'L3', 'L5']:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, REV_COXA)
    time.sleep(0.5)
    stop_all_legs()

def turn_right2():
    for leg in ['L2', 'L4', 'L6']:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, REV_COXA)
    time.sleep(0.5)
    stop_all_legs()

def rotate_right():
    for leg in legs:
        pca, coxa_ch, _, _ = legs[leg]
        set_servo_pulse_us(pca, coxa_ch, FWD_COXA)
    time.sleep(0.5)
    stop_all_legs()

def threaded_call(fn):
    t = threading.Thread(target=fn)
    t.start()
    return t

# MAIN LOOP
try:
    stand()
    print("stand")
    time.sleep(1)
    
    while True:
        print("Tripod Step Forward")
        threaded_call(move_all_legs_forward1).join()
        threaded_call(move_all_coxa_forward1).join()
        threaded_call(move_all_legs_backward1).join()
        threaded_call(move_all_coxa_backward1).join()

        threaded_call(move_all_legs_forward2).join()
        threaded_call(move_all_coxa_forward2).join()
        threaded_call(move_all_legs_backward2).join()
        threaded_call(move_all_coxa_backward2).join()
        time.sleep(2)
        
        '''
        print("Move left")
        threaded_call(move_all_legs_forward1).join()
        threaded_call(turn_left1).join()
        threaded_call(move_all_legs_backward1).join()
        threaded_call(move_all_legs_forward2).join()
        threaded_call(turn_left2).join()
        threaded_call(move_all_legs_backward2).join()
        threaded_call(rotate_left).join()
        time.sleep(2)

        print("Tripod Step Forward")
        threaded_call(move_all_legs_forward1).join()
        threaded_call(move_all_coxa_forward1).join()
        threaded_call(move_all_legs_backward1).join()
        threaded_call(move_all_coxa_backward1).join()
        threaded_call(move_all_legs_forward2).join()
        threaded_call(move_all_coxa_forward2).join()
        threaded_call(move_all_legs_backward2).join()
        threaded_call(move_all_coxa_backward2).join()
        time.sleep(2)

        print("Move right")
        threaded_call(move_all_legs_forward1).join()
        threaded_call(turn_right1).join()
        threaded_call(move_all_legs_backward1).join()
        threaded_call(move_all_legs_forward2).join()
        threaded_call(turn_right2).join()
        threaded_call(move_all_legs_backward2).join()
        threaded_call(rotate_right).join()
        time.sleep(2)
        '''
    

except KeyboardInterrupt:
    print("Stopping all servos")
    stop_all_legs()

