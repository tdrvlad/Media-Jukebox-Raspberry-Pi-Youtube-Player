import RPi.GPIO as GPIO
import time, os, yaml


rel_path = os.path.relpath(os.path.dirname(os.path.realpath(__file__)), os.getcwd()) 
gpio_wiring_file = os.path.join(rel_path, 'gpio_wiring.yaml')

GPIO.setmode(GPIO.BCM)

with open(gpio_wiring_file) as data_file:
    gpio_map = yaml.load(data_file, Loader=yaml.FullLoader)

class LED:
    def __init__(self):
        self.pin = gpio_map.get('led')
        if self.pin is None:
            print('No wiring found for led.')
        GPIO.setup(gpio_map.get('led'), GPIO.OUT)
        GPIO.output(gpio_map.get('led'), GPIO.LOW)

    def signal(self):
        GPIO.output(gpio_map.get('led'), GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(gpio_map.get('led'), GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(gpio_map.get('led'), GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(gpio_map.get('led'), GPIO.LOW)

if __name__ == '__main__':
	button_pin = gpio_map.get('shutdown_button')
	fan_pin = gpio_map.get('fan')

	led = LED()

	GPIO.setup(button_pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(fan_pin, GPIO.OUT)
	GPIO.output(fan_pin, GPIO.LOW)

	led.signal()

	def shutdown(channel):
		print('Shutting down')
		os.system('shutdown now')

	GPIO.add_event_detect(button_pin,GPIO.RISING, callback=shutdown,bouncetime=2000)

	while True:
		time.sleep(0.1)


