import pygame


class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.current_music = None
        self.sounds = {}
        self.load_sound("jump", "jump")
        self.load_sound("coin", "coin")
        self.load_sound("sprout", "sprout")
        self.load_sound("power-up", "power-up")
        self.load_sound("bump", "bump")
        self.load_sound("lost_a_life", "lost_a_life")
        self.load_sound("course_clear", "course_clear")
        self.load_sound("spin", "spin")
        self.load_sound("power_down_pipe", "power_down_pipe")
        self.load_sound("stomp_no_damage", "stomp_no_damage")
        self.load_sound("reserve_drop", "reserve_drop")
        self.load_sound("1up", "1up")
        self.load_sound("dragon_coin", "dragon_coin")
        self.load_sound("reserve_drop", "reserve_drop")

    def load_sound(self, name, filename):
        path = f"assets/sounds/effects/{filename}.wav"
        self.sounds[name] = pygame.mixer.Sound(path)

    def play_music(self, music_name, loops=-1, fade_ms=500):
        filename = f"assets/sounds/music/{music_name}.ogg"
        if self.current_music == filename:
            return

        self.current_music = filename
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)

    def stop_music(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None

    def stop_music_instant(self):
        """Para a música imediatamente, sem fade (ex.: no instante da morte)."""
        pygame.mixer.music.stop()
        self.current_music = None

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def play_sound(self, name):
        # print(self.sounds)
        if name in self.sounds:
            self.sounds[name].play()

    def set_sound_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume)