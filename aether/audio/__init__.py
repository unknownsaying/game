"""
AetherEngine Audio Module
Comprehensive audio system with 3D spatialization, DSP effects,
dynamic mixing, streaming, and professional-grade sound management.

Usage:
    from audio import AudioManager
    from audio import SoundEffect, Reverb, Echo, Chorus
    
    # Initialize audio
    audio_mgr = AudioManager()
    
    # Load and play sounds
    audio_mgr.load_sound("explosion", "assets/audio/sfx/explosion.wav")
    audio_mgr.play("explosion", volume=0.8, position_3d=[100, 200, 0])
    
    # Apply effects
    reverb = Reverb(room_size=0.7, wet_level=0.3)
    audio_mgr.add_bus_effect(AudioChannelGroup.SFX, reverb)
    
    # Control music
    audio_mgr.play_music("assets/audio/music/theme.ogg", volume=0.7, loop=True)
"""

import logging
# Direct imports
from audio import AudioManager, Reverb, Echo

# Module-level access
import audio
audio_mgr = audio.create_audio_system()

# Specific imports
from audio.audio_manager import AudioManager
from audio.sound_effects import Distortion, Compressor
# Configure module logger
logger = logging.getLogger("AetherEngine.Audio")
logger.setLevel(logging.INFO)

# Import core audio manager
from .audio_manager import (
    AudioManager,
    AudioFormat,
    AudioChannelGroup,
    PlaybackState,
    AudioClip,
    AudioBus,
    AudioChannel,
    AudioListener
)

# Import sound effects
from .sound_effects import (
    SoundEffect,
    AudioEffect,
    Reverb,
    Echo,
    Chorus,
    Flanger,
    Distortion,
    EQ,
    Compressor,
    PitchShift,
    AutoWah,
    Vibrato,
    Tremolo,
    BitCrusher,
    RingModulator,
    ConvolutionReverb,
    AudioEffectChain,
    normalize_audio,
    fade_in_out,
    mix_tracks,
    apply_envelope
)

# Define public API
__all__ = [
    # Core
    'AudioManager',
    'AudioFormat',
    'AudioChannelGroup',
    'PlaybackState',
    'AudioClip',
    'AudioBus',
    'AudioChannel',
    'AudioListener',
    
    # Effects Base
    'SoundEffect',
    'AudioEffect',
    
    # DSP Effects
    'Reverb',
    'Echo',
    'Chorus',
    'Flanger',
    'Distortion',
    'EQ',
    'Compressor',
    'PitchShift',
    'AutoWah',
    'Vibrato',
    'Tremolo',
    'BitCrusher',
    'RingModulator',
    'ConvolutionReverb',
    
    # Effect Chain
    'AudioEffectChain',
    
    # Utilities
    'normalize_audio',
    'fade_in_out',
    'mix_tracks',
    'apply_envelope'
]

# Module version
__version__ = "1.0.0"
__author__ = "AetherEngine Team"

# Quick helper to check if audio is available
def is_audio_available() -> bool:
    """Check if audio system can be initialized"""
    try:
        import pygame
        return pygame.mixer.get_init() or True
    except ImportError:
        return False

# Convenience function for quick audio setup
def create_audio_system(frequency: int = 44100, 
                       max_channels: int = 32,
                       enable_3d: bool = True) -> AudioManager:
    """
    Create and initialize an audio manager with common settings.
    
    Args:
        frequency: Sample rate in Hz (22050, 44100, 48000)
        max_channels: Maximum simultaneous sounds
        enable_3d: Enable 3D spatial audio
        
    Returns:
        Initialized AudioManager instance
    """
    audio_mgr = AudioManager(
        frequency=frequency,
        max_channels=max_channels,
        enable_3d=enable_3d
    )
    
    logger.info(f"Audio system created: {frequency}Hz, {max_channels} channels")
    return audio_mgr

# Print module info on import
logger.debug(f"Audio module v{__version__} loaded")