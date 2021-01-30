import os, glob, time
import vlc

movies_dir = '/home/vlad/Desktop/Movies/'
extensions = ['mkv', 'mp4', 'avi', 'wmv', 'mov']


def play_most_recent():
    movies = glob.glob(movies_dir + '*')

    if len(movies):
        last_movie = (max(movies, key=os.path.getctime))

        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(last_movie, '*' + ext)))

        if len(files):
            movie_file = files[0]
            print('Playing movie {}.'.format(os.path.basename(movie_file)))
	    
            os.system('vlc --fullscreen {}'.format(movie_file)
            
        else:

            print('No movie file found in {}.'.format(os.path.basename(last_movie)))

            os.remove(last_movie)
            play_most_recent()

    else:

        print('No movies found in {}.'.format(movies_dir))


if __name__ == '__main__':
    play_most_recent()
    

'''
            player = vlc.MediaPlayer(movie_file)
            
            player.play()
            player.toggle_fullscreen()
            time.sleep(5)
            while player.is_playing():
               time.sleep(5)
           
            player = Instance.media_player_new()
            Media = Instance.media_new(movie_file)
            player.set_media(Media)
            player.play() 
'''
