import vlc, pafy
from time import sleep
import time
import threading
import random
import RPi.GPIO as GPIO
import yaml, os
from peripherals import LED, check_button_press

rel_path = os.path.relpath(os.path.dirname(os.path.realpath(__file__)), os.getcwd()) 
gpio_wiring_file = os.path.join(rel_path, 'gpio_wiring.yaml')
playlists_file = os.path.join(rel_path, 'Desktop/playlists.yaml')

print(playlists_file)

gpio_map = {}
with open(gpio_wiring_file) as data_file:
    gpio_map = yaml.load(data_file, Loader=yaml.FullLoader)

GPIO.setmode(GPIO.BCM)

led = LED()

class Playlist:

    def __init__(self, manager, button, name = None):

        self.manager = manager
        self.selected = False
        
        pin = gpio_map.get(button)
        if pin is None:
            print('Button not defined in GPIO wiring.')
        self.button_pin = pin
        self.urls = []
        self.loaded_media = []
        self.queue = []

        self.last_media_title = None

        if name is None:
            self.name = 'Playlist For Button {}'.format(button)

    def add_url(self, playlist_url):
        self.urls.append(playlist_url)

    def remove_url(self, playlist_url):
        if playlist_url in self.urls:
            self.urls.remove(playlist_url)
    
    def get_media(self):
        
        if len(self.urls) == 0:
            print('No defined playlists.', flush = True)

        check = False
        tries = 0
        while check == False and tries < 10:
            tries += 1
            playlist_url = random.choice(self.urls)
            print('Chosen playlist URL: {}'.format(playlist_url), flush = True)

            try:
                playlist = pafy.get_playlist(playlist_url) 
                media = random.choice(playlist['items'])

                try:
                    media_url = media['pafy'].getbestaudio().url
                    media_title = media['pafy'].title

                    print('Selected media title: {}'.format(media_title))

                    if media_title != self.last_media_title:
                        check = True
                        self.last_media_title = media_title
                        return media_url
                    else:
                        print('No same consecutive media. Rechoosing.')
                except:
                    media_url = None
                    print('Error getting media from URL: {}'.format(media_url))
                
            except:
                print('Error getting playlist from URL {}'.format(playlist_url))

        return None


    def play(self):

        while self.selected == True:
            player = vlc.Instance().media_player_new()

            check = False
            tries = 0

            while check == False and tries < 5:
                tries +=1
                media_url = self.get_media()
    
                try:
                    Instance = vlc.Instance()
                    Media = Instance.media_new(media_url)
                    Media.get_mrl()
                    player.set_media(Media)
                    print('Playing.', flush = True)
                    player.play()
                    check = True
                    sleep(2) 
                except:
                    print('Error playing media on vlc module.')

                stop = False
                while stop == False and check == True and player.is_playing():
                    
                    check_button = self.manager.check_buttons()
                    if check_button == True:
                        stop = True
                        player.stop()
                        time.sleep(1)
                    time.sleep(0.3)
            

class PlaylistManager:

    def __init__(self):
        self.playlists = []

    def check_button_already_used(self,button):
        pin = gpio_map.get(button)
        if pin is None:
            print('Button not defined in GPIO wiring.')
        for playlist in self.playlists:
            if playlist.button_pin == pin:
                return playlist
    
    def add_playlist(self, button, name = None):

        playlist = Playlist(self, button, name)
        existent_playlist = self.check_button_already_used(button)
        if not existent_playlist is None:
            self.playlists.remove(existent_playlist)
        GPIO.setup(playlist.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.playlists.append(playlist)

        return playlist
    
    def deselect_all(self):
        for playlist in self.playlists:
            playlist.selected = False

    def check_buttons(self):

        for playlist in self.playlists:
            pressed_time = check_button_press(playlist.button_pin, led)
            if pressed_time > 0.2:
                self.deselect_all()
                if pressed_time < 2:
                    playlist.selected = True
                return True
        return False

    def run(self):

        while True:
            self.check_buttons()
            for playlist in self.playlists:
                if playlist.selected == True:
                    playlist.play()
            time.sleep(0.5)


if __name__ =='__main__':

    with open(playlists_file) as data_file:
        playlists = yaml.load(data_file, Loader=yaml.FullLoader)

    manager = PlaylistManager()

    GPIO.setup(gpio_map.get('led'), GPIO.OUT)
        
    for playlist_name, values in playlists.items():
        print('Adding playlist {}.'.format(playlist_name))
        button = values.get('button')

        playlist = manager.add_playlist(
            button = button,
            name = playlist_name
        )

        playlists_urls = values.get('playlists_urls')
        for playlist_url in playlists_urls:
            playlist.add_url(playlist_url)
   

    manager.run()


