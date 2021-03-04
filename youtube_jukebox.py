import vlc, pafy
from pytube import Playlist
from time import sleep
import time
import threading
import random
import RPi.GPIO as GPIO
import yaml, os
from peripherals import LED, check_button_press

rel_path = os.path.relpath(os.path.dirname(os.path.realpath(__file__)), os.getcwd()) 
gpio_wiring_file = os.path.join(rel_path, 'gpio_wiring.yaml')
themes_file = os.path.join(rel_path, 'Desktop/playlists.yaml')

gpio_map = {}
with open(gpio_wiring_file) as data_file:
    gpio_map = yaml.load(data_file, Loader=yaml.FullLoader)

GPIO.setmode(GPIO.BCM)

led = LED()
led.signal()

class Theme:
    '''
    Theme contains multiple Youtube Playlists URLs.
    At startup, all the video URLs in the Theme Playlists are added into a Media Pool and then randomly selected.
    A Theme has a button from the pannel associated with.
    '''

    def __init__(self, manager, button, name = None):

        self.manager = manager
        self.selected = False
        
        pin = gpio_map.get(button)
        if pin is None:
            print('Button not defined in GPIO wiring.')
        self.button_pin = pin
        self.playlist_urls = []
        self.media_pool_urls = None
        self.queue = []

        self.player = self.manager.player

        '''
        last_played assures that the random selection does not repeat itself.
        '''
        self.last_played = []
        self.last_played_dim = 3

        if name is None:
            self.name = 'Theme For Button {}'.format(button)


    def add_url(self, playlist_url):
        self.playlist_urls.append(playlist_url)


    def remove_url(self, playlist_url):
        if playlist_url in self.playlist_urls:
           self.playlist_urls.remove(playlist_url)
    

    def load_media(self):

        self.media_pool_urls = []

        if len(self.playlist_urls) == 0:
            print('No playlists in theme.', flush = True)

        for playlist_url in self.playlist_urls:
            try:
                playlist = Playlist(playlist_url)
                for url in playlist.video_urls:
                    self.media_pool_urls.append(url)
            except:
                print('Encountered error while processing playlist: {}'.format(playlist_url))
        
        print('Finished loading {} Playlists with a total of {} videos.'.format(len(self.playlist_urls), len(self.media_pool_urls)))


    def get_media(self):

        if self.media_pool_urls is None:
            self.load_media()
        
        if len(self.last_played) > self.last_played_dim:
            self.last_played.pop(0)

        tries = 0
        while tries < 10:
            
            tries +=1
            possible_urls = [i for i in self.media_pool_urls if i not in self.last_played]
            chosen_url = random.choice(possible_urls)

            self.last_played.append(chosen_url)
            print('Chosen media URL: {}'.format(chosen_url), flush = True)

            try:
                media = pafy.new(chosen_url)
                playable_url = media.getbestaudio().url
                return playable_url
            except:
                print('Error getting {}. Removing.'.format(chosen_url))
                self.media_pool_urls.remove(chosen_url)


    def play(self):
        
        while self.selected == True:
            
            check = False
            tries = 0

            while check == False and tries < 5:
                tries +=1
                media_url = self.get_media()
    
                try:
                    Instance = vlc.Instance()
                    Media = Instance.media_new(media_url)
                    Media.get_mrl()
                    self.player.set_media(Media)
                    print('Playing.', flush = True)
                    time.sleep(0.1)
                    self.player.play()
                    check = True
                    sleep(2) 
                except:
                    print('Error playing media on vlc module.')

                stop = False
                while stop == False and check == True and self.player.is_playing():
                    check_button = self.manager.check_buttons()
                    if check_button == True:
                        stop = True
                        self.player.stop()
            

class ThemeManager:
    '''
    Loads all the defined Themes and watches if any button is pressed.
    '''

    def __init__(self):
        self.themes = []
        self.player = vlc.MediaPlayer() 


    def check_button_already_used(self,button):
        pin = gpio_map.get(button)
        if pin is None:
            print('Button not defined in GPIO wiring.')
        for theme in self.themes:
            if theme.button_pin == pin:
                return theme
    

    def add_theme(self, button, name = None):

        theme = Theme(self, button, name)
        existent_theme = self.check_button_already_used(button)
        if not existent_theme is None:
            self.themes.remove(existent_theme)
        GPIO.setup(theme.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.themes.append(theme)

        return theme
    

    def deselect_all(self):
        for theme in self.themes:
            theme.selected = False


    def check_buttons(self):

        for theme in self.themes:
            pressed_time = check_button_press(theme.button_pin, led)
            if pressed_time > 0.2:
                self.deselect_all()
                if pressed_time < 2:
                    theme.selected = True
                return True
        return False


    def run(self):

        while True:
            self.check_buttons()
            for theme in self.themes:
                if theme.selected == True:
                    theme.play()
            time.sleep(0.5)


if __name__ =='__main__':

    with open(themes_file) as data_file:
        themes = yaml.load(data_file, Loader=yaml.FullLoader)

    manager = ThemeManager()
    GPIO.setup(gpio_map.get('led'), GPIO.OUT)
        
    for theme_name, values in themes.items():
        print('Adding theme {}.'.format(theme_name))
        button = values.get('button')

        theme = manager.add_theme(
            button = button,
            name = theme_name)

        playlists_urls = values.get('playlists_urls')
        for playlist_url in playlists_urls:
            theme.add_url(playlist_url)
        
        theme.load_media()
	
    manager.run()




