import os
import pygame
import random
import threading
import time
from wcwidth import wcswidth

CONFIG_FILE = "simmusicplayer.cfg"

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
        # Start a background thread to monitor playback.
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
        self.select_music_dir()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(self.music_dir)

    def select_music_dir(self):
        while True:
            path = input("Enter music folder path: ").strip().strip('" ')
            if os.path.isdir(path):
                self.music_dir = path
                return
            print("Invalid path. Try again.")

    def load_music(self):
        exts = ('.mp3', '.wav', '.ogg')
        self.playlist = [f for f in os.listdir(self.music_dir)
                         if f.lower().endswith(exts)]
        if not self.playlist:
            print("No playable music files found in the directory.")
            exit()

    def play(self, index=None):
        if index is not None:
            self.current_index = index
        track_path = os.path.join(self.music_dir, self.playlist[self.current_index])
        pygame.mixer.music.load(track_path)
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
        if len(self.playlist) > 1:
            new_index = self.current_index
            while new_index == self.current_index:
                new_index = random.randint(0, len(self.playlist) - 1)
            self.play(new_index)
        else:
            self.play()

    def select_song(self):
        for i, song in enumerate(self.playlist):
            print(f" {i+1:02d}. {song}")
        try:
            choice = int(input("Select track number: "))
            if 1 <= choice <= len(self.playlist):
                self.play(choice - 1)
            else:
                print("Invalid track number!")
                input("Press Enter to continue...")
        except ValueError:
            print("Please enter a valid number!")
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
        status = "▶ Playing" if not self.paused else "⏸ Paused"
        track = self.truncate(self.playlist[self.current_index], 28)
        lines = [
            f"Current Track: {track}",
            f"Status: {status}",
            "",
            "Commands:",
            "[P] Play/Pause  [N] Next",
            "[B] Previous    [L] Playlist",
            "[R] Random Play [S] Select Track",
            "[Q] Quit"
        ]
        all_text = lines + [title]
        max_width = max(wcswidth(line) for line in all_text) + 4

        def print_border(left, fill, right):
            print(f"{left}{fill * (max_width - 2)}{right}")

        print_border("┌", "─", "┐")
        print(f"│{title.center(max_width - 2)}│")
        print_border("├", "─", "┤")
        for line in lines:
            line_width = wcswidth(line)
            spaces = max_width - 2 - line_width
            print(f"│{line}{' ' * spaces}│")
        print_border("└", "─", "┘")

    def truncate(self, text, width):
        result = ""
        total = 0
        for c in text:
            ch_width = max(wcswidth(c), 0)
            if total + ch_width > width:
                result += "..."
                break
            result += c
            total += ch_width
        return result

    def monitor_playback(self):
        # Monitor music playback in a background thread.
        while True:
            try:
                if not self.paused and not pygame.mixer.music.get_busy():
                    self.next_track()
            except Exception as e:
                print(f"Exception in monitor_playback: {e}")
            time.sleep(1)

    def run(self):
        self.load_config()
        self.load_music()
        self.play()
        while True:
            self.draw_ui()
            cmd = input("Enter command: ").strip().lower()
            if cmd in self.commands:
                self.commands[cmd]()
            else:
                print("Unknown command.")

if __name__ == "__main__":
    MusicPlayer().run()
