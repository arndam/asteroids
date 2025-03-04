#!/usr/bin/env python3
"""
Sound Generator for Asteroids Game
Creates basic WAV files for the game sounds.

Copyright © 2023 Arne Damvin. All rights reserved.
"""
import wave
import struct
import math
import os
import random

def create_directory():
    """Create sounds directory if it doesn't exist."""
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("Created sounds directory")
    else:
        print("Sounds directory already exists")

def create_fire_sound():
    """Create a laser-like sound for firing bullets."""
    filename = "sounds/fire.wav"
    
    # Audio properties
    framerate = 44100  # samples per second
    duration = 0.2     # seconds
    
    # Create the WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(framerate)
        
        # Generate a descending frequency tone
        for i in range(int(framerate * duration)):
            # Start at a higher frequency and decrease
            freq = 1500 - (i / (framerate * duration) * 1000)
            # Create a sine wave with decreasing amplitude
            value = int(32767 * 0.8 * math.sin(2 * math.pi * freq * i / framerate) * (1 - i / (framerate * duration)))
            packed_value = struct.pack('h', value)
            wav_file.writeframes(packed_value)
    
    print(f"Created {filename}")

def create_explosion_sound():
    """Create an explosion sound for asteroid destruction."""
    filename = "sounds/explode.wav"
    
    # Audio properties
    framerate = 44100  # samples per second
    duration = 0.5     # seconds
    
    # Create the WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(framerate)
        
        # Generate noise with decreasing amplitude
        for i in range(int(framerate * duration)):
            # Random noise
            value = int(32767 * random.uniform(-1, 1) * (1 - i / (framerate * duration)))
            packed_value = struct.pack('h', value)
            wav_file.writeframes(packed_value)
    
    print(f"Created {filename}")

def create_thrust_sound():
    """Create a continuous thrust sound."""
    filename = "sounds/thrust.wav"
    
    # Audio properties
    framerate = 44100  # samples per second
    duration = 1.0     # seconds
    
    # Create the WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(framerate)
        
        # Generate filtered noise for thrust
        for i in range(int(framerate * duration)):
            # Mix noise with a sine wave
            noise = random.uniform(-0.5, 0.5)
            sine = 0.5 * math.sin(2 * math.pi * 100 * i / framerate)
            value = int(32767 * (noise + sine))
            packed_value = struct.pack('h', value)
            wav_file.writeframes(packed_value)
    
    print(f"Created {filename}")

def create_saucer_sound():
    """Create a UFO sound."""
    filename = "sounds/saucer.wav"
    
    # Audio properties
    framerate = 44100  # samples per second
    duration = 1.0     # seconds
    
    # Create the WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(framerate)
        
        # Generate an alternating tone
        for i in range(int(framerate * duration)):
            # Alternate between two frequencies
            freq = 400 if (i // (framerate // 10)) % 2 == 0 else 600
            value = int(32767 * 0.7 * math.sin(2 * math.pi * freq * i / framerate))
            packed_value = struct.pack('h', value)
            wav_file.writeframes(packed_value)
    
    print(f"Created {filename}")

def create_hyperspace_sound():
    """Create a hyperspace teleport sound."""
    filename = "sounds/hyperspace.wav"
    
    # Audio properties
    framerate = 44100  # samples per second
    duration = 0.4     # seconds
    
    # Create the WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(framerate)
        
        # Generate an ascending frequency sweep
        for i in range(int(framerate * duration)):
            # Start at a low frequency and increase
            freq = 200 + (i / (framerate * duration) * 1500)
            # Create a sine wave
            value = int(32767 * 0.8 * math.sin(2 * math.pi * freq * i / framerate))
            packed_value = struct.pack('h', value)
            wav_file.writeframes(packed_value)
    
    print(f"Created {filename}")

def main():
    """Create all sound files."""
    create_directory()
    create_fire_sound()
    create_explosion_sound()
    create_thrust_sound()
    create_saucer_sound()
    create_hyperspace_sound()
    print("All sound files created successfully!")

if __name__ == "__main__":
    main() 