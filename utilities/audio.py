# PWM Audio player for Interstate 75 W
# Plays tones with attack/decay envelopes for realistic chime sounds

from machine import Pin, PWM
from time import sleep_ms
import json

# Configuration - which GPIO pin has a speaker/buzzer connected
try:
    from config import AUDIO_PIN
except ImportError:
    AUDIO_PIN = 2  # Default to GP2

# Persistent settings file
SETTINGS_FILE = "audio_settings.json"


def _load_settings():
    """Load audio settings from persistent storage"""
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"enabled": True}


def _save_settings(settings):
    """Save audio settings to persistent storage"""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Audio: failed to save settings: {e}")


class AudioPlayer:
    """PWM-based audio player with envelope shaping"""

    def __init__(self, pin=None):
        self.pin_num = pin if pin is not None else AUDIO_PIN
        self.pwm = None
        # Load enabled state from persistent storage
        settings = _load_settings()
        self._enabled = settings.get("enabled", True)
        print(f"Audio: initialized, enabled={self._enabled}")

    def _init_pwm(self):
        """Initialize PWM on the audio pin"""
        if self.pwm is None:
            self.pwm = PWM(Pin(self.pin_num))

    def _cleanup_pwm(self):
        """Clean up PWM"""
        if self.pwm:
            self.pwm.duty_u16(0)
            self.pwm.deinit()
            self.pwm = None

    def _play_tone_with_envelope(self, freq, duration_ms):
        """
        Play a tone with attack/decay envelope for realistic chime sound.

        Args:
            freq: Frequency in Hz
            duration_ms: Total duration in milliseconds
        """
        self.pwm.freq(freq)

        # Quick attack (~35ms)
        attack_time = 35
        steps = 15
        for i in range(steps):
            self.pwm.duty_u16(int((i / steps) * 32768))
            sleep_ms(attack_time // steps)

        # Long decay - exponential falloff
        decay_time = duration_ms - attack_time
        steps = 60
        for i in range(steps):
            t = i / steps
            # Approximate bell/chime envelope curve
            level = (1 - t) ** 1.5
            self.pwm.duty_u16(int(level * 32768))
            sleep_ms(decay_time // steps)

        self.pwm.duty_u16(0)

    def play_tone(self, frequency, duration_ms):
        """
        Play a simple tone (no envelope).

        Args:
            frequency: Tone frequency in Hz
            duration_ms: Duration in milliseconds
        """
        if not self._enabled:
            return

        self._init_pwm()
        try:
            self.pwm.freq(frequency)
            self.pwm.duty_u16(32768)  # 50% duty cycle
            sleep_ms(duration_ms)
        finally:
            self._cleanup_pwm()

    def play_bing_bong(self):
        """Play a realistic bing-bong doorbell chime"""
        if not self._enabled:
            print("Audio: disabled, skipping bing-bong")
            return

        print("Audio: playing bing-bong")
        self._init_pwm()
        try:
            # D5 down to B4 - minor third interval (like real doorbells)
            self._play_tone_with_envelope(587, 750)   # Bing (D5)
            sleep_ms(225)                              # Gap
            self._play_tone_with_envelope(494, 670)   # Bong (B4)
        finally:
            self._cleanup_pwm()

    def enable(self):
        """Enable audio playback and save setting"""
        self._enabled = True
        _save_settings({"enabled": True})
        print("Audio: enabled")

    def disable(self):
        """Disable audio playback and save setting"""
        self._enabled = False
        self._cleanup_pwm()
        _save_settings({"enabled": False})
        print("Audio: disabled")

    def toggle(self):
        """Toggle audio enabled state and return new state"""
        if self._enabled:
            self.disable()
        else:
            self.enable()
        return self._enabled

    @property
    def enabled(self):
        return self._enabled


# Global audio player instance
_player = None

def get_player():
    """Get the global audio player instance"""
    global _player
    if _player is None:
        _player = AudioPlayer()
    return _player

def play_notification():
    """Play the notification sound for new flights"""
    player = get_player()
    player.play_bing_bong()
