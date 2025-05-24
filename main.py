import os
import pygame
import random
import threading
import time
from wcwidth import wcswidth

CONFIG_FILE = "musicplayer.cfg"

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_index = 0
        self.paused = True
        self.music_dir = ""
        self.playlist = []
        self.commands = {
            'p': self.toggle_pause,
            'n': self.next_track,
            'b': self.prev_track,
            'l': self.show_list,
            'r': self.random_track,  
            's': self.select_song,   
            'q': self.quit
        }
        
        self.monitor_thread = threading.Thread(target=self.monitor_playback, daemon=True)
        self.monitor_thread.start()

    def load_config(self):
        # Load the music directory from the configuration file.
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                path = f.read().strip()
            if os.path.isdir(path):
                self.music_dir = path
                return
        # If the config file does not exist or the path is invalid, ask for input.
        self.select_music_dir()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(self.music_dir)

    def select_music_dir(self):
        while True:
            path = input("Enter music folder path: ").strip().strip('"')
            if os.path.isdir(path):
                self.music_dir = path
                return
            print("Invalid path, please enter again.")

    def load_music(self):
        exts = ('.mp3', '.wav', '.ogg')
        self.playlist = [f for f in os.listdir(self.music_dir)
                         if f.lower().endswith(exts)]
        if not self.playlist:
            print("No playable music files found in the directory.")
            exit()

    def play(self, index=None):
        if index is None:
            index = self.current_index
        pygame.mixer.music.load(os.path.join(self.music_dir, self.playlist[index]))
        pygame.mixer.music.play()
        self.paused = False

    def toggle_pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def next_track(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def random_track(self):
        # Randomly select a track with an index different from the current one and play
        if len(self.playlist) > 1:
            new_index = self.current_index
            while new_index == self.current_index:
                new_index = random.randint(0, len(self.playlist) - 1)
            self.current_index = new_index
        self.play()

    def select_song(self):
        print("\nPlaylist:")
        for i, song in enumerate(self.playlist):
            print(f" {i+1:02d}. {song}")
        try:
            choice = int(input("\nEnter track number to play: "))
            if 1 <= choice <= len(self.playlist):
                self.current_index = choice - 1
                self.play()
            else:
                print("Invalid track number!")
                input("Press Enter to continue...")
        except ValueError:
            print("Input is not a valid number!")
            input("Press Enter to continue...")

    def show_list(self):
        print("\nPlaylist:")
        for i, song in enumerate(self.playlist):
            print(f" {i+1:02d}. {song}")
        input("\nPress Enter to return...")

    def quit(self):
        pygame.mixer.music.stop()
        print("Thank you for using, bye!")
        exit()

    def draw_ui(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        title = "sim musicplayer v1.0"
        status = f"{'▶' if not self.paused else '⏸'} {'Playing' if not self.paused else 'Paused'}"
        lines = [
            f"Current Track: {self.truncate(self.playlist[self.current_index], 28)}",
            f"Status: {status}",
            "",
            "Commands:",
            "[P] Play/Pause  [N] Next",
            "[B] Previous    [L] Playlist",
            "[R] Random Play [S] Select Track",
            "[Q] Quit"
        ]

        # Dynamically calculate the UI width
        max_width = max(wcswidth(l) for l in lines + [title]) + 4
        border = lambda c: print(f"{c}{'─'*(max_width-2)}{c}")

        border('┌')
        print(f"│{title.center(max_width-2)}│")
        border('├')
        for line in lines:
            padded = f" {self.pad_line(line, max_width-4)} "
            print(f"│{padded}│")
        border('└')

    def truncate(self, text, width):
        total, res = 0, []
        for c in text:
            w = max(wcswidth(c), 0)
            if total + w > width: break
            total += w
            res.append(c)
        return ''.join(res) + '　'*((width - total)//2)

    def pad_line(self, text, width):
        # Remove invalid characters
        text = ''.join(c for c in text if wcswidth(c) > 0)
        curr = wcswidth(text)
        full_space = '　' * ((width - curr) // 2)
        half_space = ' ' * ((width - curr) % 2)
        return text + full_space + half_space

    def monitor_playback(self):
        """Monitor music playback in a background thread. If the track has finished playing (and not paused),
        automatically play the next track."""
        while True:
            # Automatically switch to the next track.
            if not self.paused and not pygame.mixer.music.get_busy():
                # Automatically play the next track
                self.next_track()
            time.sleep(1)

    def run(self):
        self.load_config()
        self.load_music()
        self.play()
        while True:
            self.draw_ui()
            cmd = input("Enter command: ").strip().lower()
            if handler := self.commands.get(cmd):
                handler()
            else:
                print("Invalid command.")

if __name__ == "__main__":
    MusicPlayer().run()
