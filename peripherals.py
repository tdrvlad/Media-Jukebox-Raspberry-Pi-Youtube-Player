import RPi.GPIO as GPIO
import time
import os
import yaml


rel_path = os.path.relpath(os.path.dirname(
    os.path.realpath(__file__)), os.getcwd())
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


def check_button_press(pin, led):
    if pin is None:
        return 0
    pos = GPIO.input(pin)
    if pos == GPIO.LOW:
        print('Button wired to GPIO{} pressed.'.format(pin))
        start_timestamp = time.time()
        signalled = False
        while pos == GPIO.LOW:
            if time.time() - start_timestamp > 0.05 and signalled == False:
                led.signal()
                signalled = True
            if time.time() - start_timestamp > 3:
                led.signal()
                break
            time.sleep(0.05)
            pos = GPIO.input(pin)
        elapsed_time = time.time() - start_timestamp
        print('Elapsed time: {:.1f}s'.format(elapsed_time))
        return elapsed_time
    return 0


if __name__ == '__main__':

    button_pin = gpio_map.get('shutdown_button')
    fan_pin = gpio_map.get('fan')

    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, GPIO.LOW)

    
    def shutdown(channel):
        pressed_time = check_button_press(button_pin, led = LED())
        if pressed_time > 2.5:
            os.system('shutdown now')

    GPIO.add_event_detect(button_pin, GPIO.RISING,
                          callback=shutdown, bouncetime=2000)

    while True:
        time.sleep(0.01)
