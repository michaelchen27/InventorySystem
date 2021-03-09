import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        print("Bring tag to reader...")
        id, text = reader.read()
        print(id)
        print(text)
finally:
        GPIO.cleanup()
