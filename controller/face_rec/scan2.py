from adafruit_servokit import ServoKit
import time

# Initialize the PCA9685 using the ServoKit class
kit = ServoKit(channels=16)

# Function to rotate the motor in one direction for a certain time
def rotate_motor(pulse, duration):
    kit.continuous_servo[0].throttle = pulse
    time.sleep(duration)
    kit.continuous_servo[0].throttle = 0  # Stop

# Rotate 90 degrees clockwise (just an approximation)
for i in range(4):
    rotate_motor(0.08, 0.15)  # Positive values = clockwise
    time.sleep(2)

# Rotate 180 degrees counterclockwise (approximation)
for i in range(7):
    rotate_motor(-0.08, 0.15)  # Negative values = counter-clockwise
    time.sleep(2)

# Final move
for i in range(1):
    rotate_motor(0.11, 0.5)

# Stop motor
kit.continuous_servo[0].throttle = 0
