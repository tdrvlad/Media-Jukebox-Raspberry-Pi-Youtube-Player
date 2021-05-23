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

    def turn_on(self):
        GPIO.output(gpio_map.get('led'), GPIO.HIGH)
    
    def turn_off(self):
        GPIO.output(gpio_map.get('led'), GPIO.LOW)


def setup_input(gpio, pull_up = False):

    def setup_pin(pin):
        if pin < 0:
            pin *= -1
        print('Setting up pin {} as input (pull_up = {})'.format(pin, pull_up))
        if pull_up:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    if isinstance(gpio, int):
        setup_pin(gpio)
    
    if isinstance(gpio, list):
        for pin in gpio:
            setup_pin(pin)


def pressed(gpio, pull_up = False):

    if isinstance(gpio, int):

        pos = GPIO.input(gpio)
        if pos == GPIO.HIGH:
            condition = True
        else:
            condition = False
        if pull_up:
            condition = not condition
        return condition

    if isinstance(gpio, list):
        condition = True

        for pin in gpio:
            if pin > 0:
                'Pins numbered with positive values have to be pressed.'
                pos = GPIO.input(pin)
                
                if pull_up:
                    'Pull-up buttons are pressed when value is LOW'
                    if pos == GPIO.HIGH:
                        condition = False          
                else:
                    'Pull-down buttons are pressed when value is HIGH'   
                    if pos == GPIO.LOW:
                        condition = False

            else:
                'Pins numbered with negative values have to NOT be pressed.'
                pos = GPIO.input(-pin)
                
                if pull_up:
                    'Pull-up buttons are pressed when value is LOW'
                    if pos == GPIO.LOW:
                        condition = False
                else:
                    'Pull-down buttons are pressed when value is HIGH'   
                    if pos == GPIO.HIGH:
                        condition = False
        
        return condition


def check_button_press(gpio, led, pull_up = False):
    if gpio is None:
        return 0
    if pressed(gpio, pull_up = pull_up):
        print('Button wired to GPIO{} pressed.'.format(gpio))
        start_timestamp = time.time()
        signalled = False
        while pressed(gpio, pull_up = pull_up):
            if time.time() - start_timestamp > 0.05 and signalled == False:
                led.signal()
                signalled = True
            if time.time() - start_timestamp > 3:
                led.signal()
                break
            time.sleep(0.05)
        elapsed_time = time.time() - start_timestamp
        print('Elapsed time: {:.1f}s'.format(elapsed_time))
        return elapsed_time
    return 0


def test_wiring(gpio):

    if isinstance(gpio, int):
        while True:
            print(pressed(gpio))
            time.sleep(0.5)

    if isinstance(gpio, list):
        while True:
            print('\n')
            for pin in gpio:
                print(pressed(pin))
            time.sleep(0.5)

def test_press(gpio):

    while True:
        print(pressed(gpio))
        time.sleep(.5)
if __name__ == '__main__':

    led = LED()
    
    button_pin = gpio_map.get('shutdown_button')
    fan_pin = gpio_map.get('fan')

    print(fan_pin)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, GPIO.HIGH)

    '''
    GPIO.add_event_detect(button_pin, GPIO.RISING,
                          callback=shutdown, bouncetime=2000)
    '''

    while True:
        pressed_time = check_button_press(button_pin, led = led, pull_up = True)
        if pressed_time > 2.5:
            print('Shutdown')
            os.system('shutdown now')
            
