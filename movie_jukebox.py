import os, glob, time, json, yaml, time, threading
import PTN
import shutil
from peripherals import LED, check_button_press
import RPi.GPIO as GPIO

extensions = ['mkv', 'mp4', 'avi', 'wmv', 'mov']

rel_path = os.path.relpath(os.path.dirname(os.path.realpath(__file__)), os.getcwd()) 
gpio_wiring_file = os.path.join(rel_path, 'gpio_wiring.yaml')
themes_file = os.path.join(rel_path, 'Desktop/playlists.yaml')
movies_dir = os.path.join(rel_path, 'Desktop/Movies/')
processed_movies_file = os.path.join(rel_path, 'processed_movies.json')


gpio_map = {}
with open(gpio_wiring_file) as data_file:
    gpio_map = yaml.load(data_file, Loader=yaml.FullLoader)

GPIO.setmode(GPIO.BCM)

led = LED()

try:
    with open(processed_movies_file) as json_file:
        processed_movies = json.load(json_file)
except:
    processed_movies = {}


def format_filename(filename):
    return filename.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def get_movie_files(movie_dir):
    
    cwd = os.getcwd()
    os.chdir(movie_dir)

    movie_files = []
    for ext in extensions:
        movie_files.extend(glob.glob('*.' + ext))
    
    srt_files = glob.glob('*.srt')
    os.chdir(cwd)

    movie_file = None
    srt_file = None

    if len(movie_files):
        movie_file = os.path.join(movie_dir, movie_files[0])
        if len(srt_files):
            srt_file = os.path.join(movie_dir, srt_files[0])
    
    return movie_file, srt_file


def format_movie(movie_dir):

    movie_file, srt_file = get_movie_files(movie_dir)
    
    if not movie_file is None:
        info = PTN.parse(os.path.basename(movie_file))

        name = info.get('title')
        year = info.get('year')
        ext = '.' + os.path.basename(movie_file).split('.')[-1]

        if not year is None and year != 'None':
            name += ' ({})'.format(year)

        os.rename(movie_file, os.path.join(os.path.dirname(movie_file), name + ext))

        if srt_file is None:
            os.system('python3 open_subtitles_download.py ' + movie_dir + '/')
        else:
            os.rename(srt_file, os.path.join(os.path.dirname(srt_file), name + '.srt'))
        
        os.rename(movie_dir, os.path.join(os.path.dirname(movie_dir), name))

        processed_movies[name] = True
        with open(processed_movies_file, 'w') as outfile:
            json.dump(processed_movies, outfile)
 

def check_local_movies():

    movie_dirs = glob.glob(movies_dir + '*')

    for movie_dir in movie_dirs:
        movie_name = os.path.basename(movie_dir)
        if processed_movies.get(movie_name) is None:
            format_movie(movie_dir)


def play_most_recent():
    
    check_local_movies()

    movie_dirs = glob.glob(movies_dir + '*')

    if len(movie_dirs):
        
        last_movie = (max(movie_dirs, key=os.path.getctime))
        movie_file, srt_file = get_movie_files(last_movie)


        if not movie_file is None:
            command = 'mplayer -fs -ao oss'
            if not srt_file is None:
                command += ' -sub {}'.format(format_filename(srt_file))
            command += ' {}'.format(format_filename(movie_file))
            
            os.system(command)

        else:
            print('No movie file found in {}.'.format(os.path.basename(last_movie)))
            shutil.rmtree(last_movie)
            play_most_recent()

    else:
        print('No movies found in {}.'.format(movies_dir))


if __name__ == '__main__':
    
    pin = gpio_map.get('front_button_6')
    if pin is None:
        print('Button not defined in GPIO wiring.')
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    while True:
        pressed_time = check_button_press(pin, led)
        if pressed_time > 0.2:
            play_most_recent()
    
