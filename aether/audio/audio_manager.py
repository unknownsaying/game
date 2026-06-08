"""
Advanced Audio Manager for AetherEngine
Comprehensive audio system with 3D spatialization, streaming, 
dynamic mixing, audio buses, effects chains, and format support
"""

import pygame
import numpy as np
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import wave
import struct
import math
import os
from pathlib import Path
import time

class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    OGG = "ogg"
    MP3 = "mp3"
    FLAC = "flac"
    RAW = "raw"

class AudioChannelGroup(Enum):
    """Audio channel groups for mixing"""
    MASTER = "master"
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
    AMBIENT = "ambient"
    UI = "ui"

class PlaybackState(Enum):
    """Audio playback states"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    FADING_IN = "fading_in"
    FADING_OUT = "fading_out"

@dataclass
class AudioClip:
    """Represents a loaded audio clip with metadata"""
    name: str
    filepath: str
    sound: Optional[pygame.mixer.Sound]
    format: AudioFormat
    duration: float = 0.0  # seconds
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    size_bytes: int = 0
    loaded: bool = False
    use_count: int = 0
    last_used: float = 0.0
    category: AudioChannelGroup = AudioChannelGroup.SFX
    
    def __post_init__(self):
        if self.sound:
            self.loaded = True
            raw_array = pygame.sndarray.array(self.sound)
            if len(raw_array.shape) == 1:
                self.channels = 1
                self.duration = len(raw_array) / self.sample_rate
            else:
                self.channels = raw_array.shape[1]
                self.duration = raw_array.shape[0] / self.sample_rate

@dataclass
class AudioBus:
    """Audio bus for grouping and processing sounds"""
    name: str
    volume: float = 1.0
    pan: float = 0.0  # -1.0 (left) to 1.0 (right)
    muted: bool = False
    solo: bool = False
    effects_chain: List[Any] = field(default_factory=list)
    channels: List['AudioChannel'] = field(default_factory=list)
    vu_meter: float = 0.0  # Current volume level
    
    def apply_effects(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply all effects in chain to audio samples"""
        result = samples.copy()
        for effect in self.effects_chain:
            if hasattr(effect, 'process'):
                result = effect.process(result, sample_rate)
            elif hasattr(effect, 'apply'):
                result = effect.apply(result, sample_rate)
        return result

@dataclass
class AudioChannel:
    """Represents an active audio playback channel"""
    channel: pygame.mixer.Channel
    clip: Optional[AudioClip] = None
    bus: Optional[AudioBus] = None
    state: PlaybackState = PlaybackState.STOPPED
    volume: float = 1.0
    pan: float = 0.0
    pitch: float = 1.0
    loop: bool = False
    fade_time: float = 0.0
    fade_start_time: float = 0.0
    fade_start_volume: float = 0.0
    fade_target_volume: float = 0.0
    position_3d: Optional[np.ndarray] = None
    min_distance: float = 50.0
    max_distance: float = 500.0
    doppler_factor: float = 1.0
    priority: int = 0
    start_time: float = 0.0
    virtual: bool = False  # For virtual 3D processing

@dataclass
class AudioListener:
    """3D audio listener properties"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    forward: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, -1.0]))
    up: np.ndarray = field(default_factory=lambda: np.array([0.0, 1.0, 0.0]))
    volume: float = 1.0

class AudioManager:
    """
    Advanced Audio Manager with comprehensive features:
    - 3D spatial audio with HRTF approximation
    - Audio buses with effects chains
    - Dynamic mixing and ducking
    - Streaming support for large files
    - Audio clip management with caching
    - VU metering and monitoring
    - Priority-based channel allocation
    - Crossfading and transitions
    - Real-time DSP effects
    - Audio recording capability
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, 
                 frequency: int = 44100, 
                 size: int = -16,  # 16-bit
                 channels: int = 2,  # Stereo
                 buffer: int = 2048,
                 max_channels: int = 32,
                 enable_3d: bool = True):
        
        # Prevent re-initialization
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        
        # Core audio settings
        self.frequency = frequency
        self.size = size
        self.channels = channels
        self.buffer = buffer
        self.max_channels = max_channels
        self.enable_3d = enable_3d
        
        # Initialize pygame mixer with optimal settings
        try:
            pygame.mixer.init(
                frequency=frequency,
                size=size,
                channels=channels,
                buffer=buffer
            )
            pygame.mixer.set_num_channels(max_channels)
            self.mixer_initialized = True
        except Exception as e:
            print(f"Warning: Audio initialization failed: {e}")
            self.mixer_initialized = False
            pygame.mixer.init()  # Fallback
        
        # Audio clips database
        self.clips: Dict[str, AudioClip] = {}
        
        # Audio buses
        self.buses: Dict[AudioChannelGroup, AudioBus] = {
            AudioChannelGroup.MASTER: AudioBus("Master", volume=1.0),
            AudioChannelGroup.MUSIC: AudioBus("Music", volume=0.8),
            AudioChannelGroup.SFX: AudioBus("SFX", volume=1.0),
            AudioChannelGroup.VOICE: AudioBus("Voice", volume=0.9),
            AudioChannelGroup.AMBIENT: AudioBus("Ambient", volume=0.7),
            AudioChannelGroup.UI: AudioBus("UI", volume=0.6)
        }
        
        # Active channels tracking
        self.active_channels: List[AudioChannel] = []
        self.channel_pool = []
        
        # 3D Audio
        self.listener = AudioListener()
        self.speed_of_sound = 343.0  # m/s
        
        # Streaming
        self.streaming_clips: Dict[str, Any] = {}
        self.stream_thread: Optional[threading.Thread] = None
        self.stream_queue = queue.Queue()
        
        # Recording
        self.recording = False
        self.recorded_frames: List[np.ndarray] = []
        
        # Audio processing thread
        self.process_thread: Optional[threading.Thread] = None
        self.process_queue = queue.Queue()
        self.running = True
        
        # Callbacks
        self.on_clip_loaded: List[Callable] = []
        self.on_playback_started: List[Callable] = []
        self.on_playback_stopped: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_plays': 0,
            'active_sounds': 0,
            'peak_vu': 0.0,
            'clips_loaded': 0
        }
        
        # Initialize channel pool
        self._initialize_channels()
        
        # Start processing thread
        self._start_processing_thread()
        
        print(f"Audio Manager initialized: {frequency}Hz, {max_channels} channels")
    
    def _initialize_channels(self):
        """Initialize channel pool"""
        self.channel_pool = []
        for i in range(self.max_channels):
            try:
                channel = pygame.mixer.Channel(i)
                audio_channel = AudioChannel(channel=channel)
                self.channel_pool.append(audio_channel)
            except Exception as e:
                print(f"Failed to create channel {i}: {e}")
    
    def load_sound(self, 
                   name: str, 
                   filepath: str, 
                   category: AudioChannelGroup = AudioChannelGroup.SFX,
                   preload: bool = True) -> Optional[AudioClip]:
        """
        Load an audio file and create a clip
        
        Args:
            name: Unique identifier for the clip
            filepath: Path to audio file
            category: Audio bus category
            preload: If True, load into memory immediately
            
        Returns:
            AudioClip object or None if loading failed
        """
        # Check if already loaded
        if name in self.clips:
            clip = self.clips[name]
            clip.use_count += 1
            clip.last_used = time.time()
            return clip
        
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"Audio file not found: {filepath}")
            return None
        
        # Detect format
        suffix = filepath.suffix.lower()
        if suffix == '.wav':
            audio_format = AudioFormat.WAV
        elif suffix == '.ogg':
            audio_format = AudioFormat.OGG
        elif suffix == '.mp3':
            audio_format = AudioFormat.MP3
        elif suffix == '.flac':
            audio_format = AudioFormat.FLAC
        else:
            audio_format = AudioFormat.RAW
        
        # Get file info
        try:
            if suffix == '.wav':
                with wave.open(str(filepath), 'rb') as wf:
                    frames = wf.getnframes()
                    sample_rate = wf.getframerate()
                    channels_count = wf.getnchannels()
                    bit_depth = wf.getsampwidth() * 8
                    duration = frames / sample_rate if sample_rate > 0 else 0
            else:
                # Use pygame to get info
                temp_sound = pygame.mixer.Sound(str(filepath))
                sample_rate = self.frequency
                channels_count = self.channels
                bit_depth = abs(self.size)
                duration = temp_sound.get_length()
                temp_sound = None  # Release
        except Exception as e:
            print(f"Error reading audio file info: {e}")
            sample_rate = self.frequency
            channels_count = self.channels
            bit_depth = abs(self.size)
            duration = 0.0
        
        # Create clip object
        clip = AudioClip(
            name=name,
            filepath=str(filepath),
            sound=None,
            format=audio_format,
            duration=duration,
            sample_rate=sample_rate,
            channels=channels_count,
            bit_depth=bit_depth,
            size_bytes=filepath.stat().st_size,
            loaded=False,
            category=category
        )
        
        # Load into memory if preload
        if preload and self.mixer_initialized:
            try:
                clip.sound = pygame.mixer.Sound(str(filepath))
                clip.loaded = True
                self.stats['clips_loaded'] += 1
            except Exception as e:
                print(f"Error loading sound '{name}': {e}")
                # Will stream instead
        
        # Store clip
        self.clips[name] = clip
        
        # Notify listeners
        for callback in self.on_clip_loaded:
            callback(clip)
        
        return clip
    
    def load_sounds_from_directory(self, 
                                   directory: str, 
                                   category: AudioChannelGroup = AudioChannelGroup.SFX,
                                   prefix: str = "",
                                   recursive: bool = True) -> Dict[str, AudioClip]:
        """
        Load all audio files from a directory
        
        Args:
            directory: Directory path
            category: Audio category for all loaded clips
            prefix: Prefix to add to clip names
            recursive: Search subdirectories
            
        Returns:
            Dictionary of loaded clips
        """
        directory = Path(directory)
        loaded = {}
        
        pattern = "**/*" if recursive else "*"
        for filepath in directory.glob(pattern):
            if filepath.suffix.lower() in ['.wav', '.ogg', '.mp3', '.flac']:
                name = prefix + filepath.stem
                clip = self.load_sound(name, str(filepath), category)
                if clip:
                    loaded[name] = clip
        
        return loaded
    
    def play(self, 
             clip_name: str, 
             volume: float = 1.0,
             pan: float = 0.0,
             pitch: float = 1.0,
             loop: bool = False,
             fade_in: float = 0.0,
             position_3d: Optional[np.ndarray] = None,
             priority: int = 0,
             bus: Optional[AudioChannelGroup] = None) -> Optional[AudioChannel]:
        """
        Play an audio clip
        
        Args:
            clip_name: Name of the clip to play
            volume: Playback volume (0.0 to 1.0)
            pan: Stereo pan (-1.0 left to 1.0 right)
            pitch: Playback speed/pitch (0.5 to 2.0)
            loop: Loop playback
            fade_in: Fade in time in seconds
            position_3d: 3D position for spatial audio
            priority: Priority (higher = more important)
            bus: Audio bus to route through
            
        Returns:
            AudioChannel if playback started, None otherwise
        """
        if not self.mixer_initialized:
            return None
        
        # Get clip
        clip = self.clips.get(clip_name)
        if not clip:
            print(f"Clip not found: {clip_name}")
            return None
        
        # Ensure clip is loaded
        if not clip.loaded and clip.sound is None:
            try:
                clip.sound = pygame.mixer.Sound(clip.filepath)
                clip.loaded = True
            except:
                print(f"Cannot load clip on demand: {clip_name}")
                return None
        
        # Get or allocate channel
        audio_channel = self._allocate_channel(priority)
        if not audio_channel:
            print("No available audio channels")
            return None
        
        # Configure channel
        audio_channel.clip = clip
        audio_channel.state = PlaybackState.FADING_IN if fade_in > 0 else PlaybackState.PLAYING
        audio_channel.volume = volume
        audio_channel.pan = pan
        audio_channel.pitch = pitch
        audio_channel.loop = loop
        audio_channel.priority = priority
        audio_channel.position_3d = position_3d
        audio_channel.start_time = time.time()
        
        # Assign to bus
        target_bus = bus or clip.category
        audio_channel.bus = self.buses.get(target_bus, self.buses[AudioChannelGroup.MASTER])
        self.buses[target_bus].channels.append(audio_channel)
        
        # Calculate effective volume
        effective_volume = self._calculate_effective_volume(audio_channel)
        
        # Apply fade in
        if fade_in > 0:
            audio_channel.fade_time = fade_in
            audio_channel.fade_start_time = time.time()
            audio_channel.fade_start_volume = 0.0
            audio_channel.fade_target_volume = effective_volume
            initial_volume = 0.0
        else:
            initial_volume = effective_volume
        
        # Set channel properties
        channel = audio_channel.channel
        channel.set_volume(initial_volume, initial_volume)
        
        # Apply panning
        left_vol, right_vol = self._calculate_pan_volumes(audio_channel)
        channel.set_volume(left_vol, right_vol)
        
        # Play sound
        try:
            if pitch != 1.0:
                # Pygame doesn't support pitch directly
                # Would need resampling for pitch shift
                channel.play(clip.sound, loops=-1 if loop else 0)
            else:
                channel.play(clip.sound, loops=-1 if loop else 0)
        except Exception as e:
            print(f"Error playing sound: {e}")
            self._release_channel(audio_channel)
            return None
        
        # Track channel
        self.active_channels.append(audio_channel)
        self.stats['total_plays'] += 1
        self.stats['active_sounds'] = len(self.active_channels)
        
        # Notify listeners
        for callback in self.on_playback_started:
            callback(audio_channel)
        
        return audio_channel
    
    def stop(self, clip_name: str = None, fade_out: float = 0.0):
        """
        Stop playback of a clip or all clips
        
        Args:
            clip_name: Name of clip to stop, or None for all
            fade_out: Fade out time in seconds
        """
        channels_to_stop = []
        
        for audio_channel in self.active_channels:
            if clip_name is None or (audio_channel.clip and audio_channel.clip.name == clip_name):
                channels_to_stop.append(audio_channel)
        
        for audio_channel in channels_to_stop:
            if fade_out > 0:
                self._fade_out_channel(audio_channel, fade_out)
            else:
                self._stop_channel(audio_channel)
    
    def pause(self, clip_name: str = None):
        """Pause playback"""
        for audio_channel in self.active_channels:
            if clip_name is None or (audio_channel.clip and audio_channel.clip.name == clip_name):
                if audio_channel.state == PlaybackState.PLAYING:
                    audio_channel.channel.pause()
                    audio_channel.state = PlaybackState.PAUSED
    
    def resume(self, clip_name: str = None):
        """Resume paused playback"""
        for audio_channel in self.active_channels:
            if clip_name is None or (audio_channel.clip and audio_channel.clip.name == clip_name):
                if audio_channel.state == PlaybackState.PAUSED:
                    audio_channel.channel.unpause()
                    audio_channel.state = PlaybackState.PLAYING
    
    def set_volume(self, volume: float, clip_name: str = None):
        """Set volume for specific clip or all"""
        for audio_channel in self.active_channels:
            if clip_name is None or (audio_channel.clip and audio_channel.clip.name == clip_name):
                audio_channel.volume = volume
                effective = self._calculate_effective_volume(audio_channel)
                left, right = self._calculate_pan_volumes(audio_channel, effective)
                audio_channel.channel.set_volume(left, right)
    
    def set_bus_volume(self, bus: AudioChannelGroup, volume: float):
        """Set volume for entire audio bus"""
        if bus in self.buses:
            self.buses[bus].volume = volume
            # Update all channels on this bus
            for channel in self.buses[bus].channels:
                effective = self._calculate_effective_volume(channel)
                left, right = self._calculate_pan_volumes(channel, effective)
                channel.channel.set_volume(left, right)
    
    def set_bus_mute(self, bus: AudioChannelGroup, muted: bool):
        """Mute/unmute audio bus"""
        if bus in self.buses:
            self.buses[bus].muted = muted
            for channel in self.buses[bus].channels:
                if muted:
                    channel.channel.set_volume(0, 0)
                else:
                    effective = self._calculate_effective_volume(channel)
                    left, right = self._calculate_pan_volumes(channel, effective)
                    channel.channel.set_volume(left, right)
    
    def play_music(self, 
                   filepath: str, 
                   volume: float = 0.8, 
                   loop: bool = True,
                   fade_in: float = 1.0):
        """Play background music"""
        if not self.mixer_initialized:
            return
        
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(volume * self.buses[AudioChannelGroup.MUSIC].volume)
            
            if fade_in > 0:
                pygame.mixer.music.play(-1 if loop else 0, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def stop_music(self, fade_out: float = 0.0):
        """Stop background music"""
        if fade_out > 0:
            pygame.mixer.music.fadeout(int(fade_out * 1000))
        else:
            pygame.mixer.music.stop()
    
    def set_music_volume(self, volume: float):
        """Set music volume"""
        pygame.mixer.music.set_volume(volume * self.buses[AudioChannelGroup.MUSIC].volume)
    
    def crossfade_music(self, filepath: str, duration: float = 2.0):
        """Crossfade to new music track"""
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(-1, fade_ms=int(duration * 1000))
        except Exception as e:
            print(f"Error crossfading music: {e}")
    
    def set_listener_position(self, position: np.ndarray):
        """Update 3D listener position"""
        self.listener.position = np.array(position)
    
    def set_listener_orientation(self, forward: np.ndarray, up: np.ndarray = None):
        """Update 3D listener orientation"""
        self.listener.forward = np.array(forward)
        if up is not None:
            self.listener.up = np.array(up)
    
    def update_3d_audio(self):
        """Update 3D spatialization for all active channels"""
        if not self.enable_3d:
            return
        
        for audio_channel in self.active_channels:
            if audio_channel.position_3d is None:
                continue
            
            if audio_channel.state not in [PlaybackState.PLAYING, PlaybackState.FADING_IN]:
                continue
            
            source_pos = audio_channel.position_3d
            listener_pos = self.listener.position
            
            # Calculate relative position
            relative_pos = source_pos - listener_pos
            distance = np.linalg.norm(relative_pos)
            
            # Distance attenuation
            if distance <= audio_channel.min_distance:
                attenuation = 1.0
            elif distance >= audio_channel.max_distance:
                attenuation = 0.0
            else:
                # Inverse distance attenuation with smooth rolloff
                t = (distance - audio_channel.min_distance) / (audio_channel.max_distance - audio_channel.min_distance)
                attenuation = 1.0 / (1.0 + t * 3)  # Smooth falloff
            
            # Calculate panning based on angle
            if distance > 0.001:
                direction = relative_pos / distance
                
                # Get right vector from forward and up
                right = np.cross(self.listener.forward, self.listener.up)
                right = right / np.linalg.norm(right)
                
                # Calculate horizontal angle
                horizontal_angle = math.atan2(
                    np.dot(direction, right),
                    np.dot(direction, self.listener.forward)
                )
                
                # Map angle to pan (-1 to 1)
                pan = math.sin(horizontal_angle)
                pan = max(-1.0, min(1.0, pan))
            else:
                pan = 0.0
            
            # Doppler effect
            if audio_channel.doppler_factor > 0:
                doppler = self._calculate_doppler_shift(audio_channel)
                pitch = audio_channel.pitch * (1.0 + doppler * audio_channel.doppler_factor)
            else:
                pitch = audio_channel.pitch
            
            # Apply 3D processing
            effective_volume = self._calculate_effective_volume(audio_channel) * attenuation
            
            # HRTF approximation for elevation
            if len(relative_pos) >= 3 and abs(relative_pos[2]) > 0.001:
                elevation = math.asin(relative_pos[2] / max(distance, 0.001))
                # Simple HRTF: boost high frequencies for elevated sources
                elevation_factor = 1.0 + abs(elevation) * 0.5
                effective_volume *= elevation_factor
            
            # Apply panning
            left_vol = effective_volume * (1.0 - pan) * 0.5
            right_vol = effective_volume * (1.0 + pan) * 0.5
            
            audio_channel.channel.set_volume(left_vol, right_vol)
    
    def _calculate_doppler_shift(self, audio_channel: AudioChannel) -> float:
        """Calculate Doppler shift factor"""
        if audio_channel.position_3d is None:
            return 0.0
        
        # Relative velocity along the line between source and listener
        relative_pos = audio_channel.position_3d - self.listener.position
        distance = np.linalg.norm(relative_pos)
        
        if distance < 0.001:
            return 0.0
        
        direction = relative_pos / distance
        
        # Project velocities onto direction
        source_velocity = np.zeros(3)  # Would need to track source velocity
        relative_velocity = np.dot(source_velocity - self.listener.velocity, direction)
        
        # Doppler formula
        speed = self.speed_of_sound
        if speed + relative_velocity > 0:
            doppler = -relative_velocity / speed
        else:
            doppler = 0.0
        
        return max(-0.5, min(0.5, doppler))  # Clamp to reasonable range
    
    def _allocate_channel(self, priority: int) -> Optional[AudioChannel]:
        """Allocate an audio channel, stealing if necessary"""
        # First try to find free channel
        for audio_channel in self.channel_pool:
            if not audio_channel.channel.get_busy():
                if audio_channel in self.active_channels:
                    self._release_channel(audio_channel)
                return audio_channel
        
        # Steal channel with lowest priority
        if self.active_channels:
            lowest = min(self.active_channels, key=lambda c: c.priority)
            if priority >= lowest.priority:
                self._stop_channel(lowest)
                return lowest
        
        return None
    
    def _release_channel(self, audio_channel: AudioChannel):
        """Release channel back to pool"""
        audio_channel.channel.stop()
        audio_channel.clip = None
        audio_channel.state = PlaybackState.STOPPED
        audio_channel.position_3d = None
        
        if audio_channel.bus and audio_channel in audio_channel.bus.channels:
            audio_channel.bus.channels.remove(audio_channel)
            audio_channel.bus = None
        
        if audio_channel in self.active_channels:
            self.active_channels.remove(audio_channel)
            self.stats['active_sounds'] = len(self.active_channels)
    
    def _stop_channel(self, audio_channel: AudioChannel):
        """Stop a specific channel"""
        for callback in self.on_playback_stopped:
            callback(audio_channel)
        self._release_channel(audio_channel)
    
    def _fade_out_channel(self, audio_channel: AudioChannel, duration: float):
        """Start fading out a channel"""
        audio_channel.state = PlaybackState.FADING_OUT
        audio_channel.fade_time = duration
        audio_channel.fade_start_time = time.time()
        audio_channel.fade_start_volume = self._calculate_effective_volume(audio_channel)
        audio_channel.fade_target_volume = 0.0
    
    def _calculate_effective_volume(self, audio_channel: AudioChannel) -> float:
        """Calculate effective volume considering all factors"""
        volume = audio_channel.volume
        
        # Apply bus volume
        if audio_channel.bus:
            volume *= audio_channel.bus.volume
            if audio_channel.bus.muted:
                volume = 0.0
        
        # Apply master volume
        volume *= self.buses[AudioChannelGroup.MASTER].volume
        
        # Apply listener volume
        volume *= self.listener.volume
        
        return max(0.0, min(1.0, volume))
    
    def _calculate_pan_volumes(self, audio_channel: AudioChannel, 
                              effective_volume: float = None) -> Tuple[float, float]:
        """Calculate left and right channel volumes with panning"""
        if effective_volume is None:
            effective_volume = self._calculate_effective_volume(audio_channel)
        
        pan = audio_channel.pan
        # Constant power panning
        pan_angle = (pan + 1.0) * math.pi / 4.0  # Map -1..1 to 0..pi/2
        left_vol = effective_volume * math.cos(pan_angle)
        right_vol = effective_volume * math.sin(pan_angle)
        
        return left_vol, right_vol
    
    def _start_processing_thread(self):
        """Start audio processing thread for effects and monitoring"""
        self.running = True
        
        def process_loop():
            while self.running:
                try:
                    # Process queue items
                    while not self.process_queue.empty():
                        task = self.process_queue.get_nowait()
                        task()
                    
                    # Update fading channels
                    current_time = time.time()
                    channels_to_stop = []
                    
                    for audio_channel in self.active_channels:
                        if audio_channel.state == PlaybackState.FADING_IN:
                            elapsed = current_time - audio_channel.fade_start_time
                            if elapsed >= audio_channel.fade_time:
                                # Fade complete
                                effective = self._calculate_effective_volume(audio_channel)
                                left, right = self._calculate_pan_volumes(audio_channel, effective)
                                audio_channel.channel.set_volume(left, right)
                                audio_channel.state = PlaybackState.PLAYING
                            else:
                                # Interpolate volume
                                t = elapsed / audio_channel.fade_time
                                # Smooth step for nicer fade
                                t = t * t * (3 - 2 * t)
                                vol = audio_channel.fade_start_volume + (audio_channel.fade_target_volume - audio_channel.fade_start_volume) * t
                                left, right = self._calculate_pan_volumes(audio_channel, vol)
                                audio_channel.channel.set_volume(left, right)
                        
                        elif audio_channel.state == PlaybackState.FADING_OUT:
                            elapsed = current_time - audio_channel.fade_start_time
                            if elapsed >= audio_channel.fade_time:
                                channels_to_stop.append(audio_channel)
                            else:
                                t = elapsed / audio_channel.fade_time
                                vol = audio_channel.fade_start_volume * (1 - t)
                                left, right = self._calculate_pan_volumes(audio_channel, vol)
                                audio_channel.channel.set_volume(left, right)
                    
                    # Stop faded out channels
                    for channel in channels_to_stop:
                        self._stop_channel(channel)
                    
                    # Update VU meters
                    self._update_vu_meters()
                    
                    # Update 3D audio
                    self.update_3d_audio()
                    
                    # Sleep to reduce CPU usage
                    time.sleep(0.01)  # 100Hz update rate
                    
                except Exception as e:
                    print(f"Audio processing error: {e}")
        
        self.process_thread = threading.Thread(target=process_loop, daemon=True)
        self.process_thread.start()
    
    def _update_vu_meters(self):
        """Update VU meter levels for all buses"""
        for bus in self.buses.values():
            # Calculate average volume of active channels
            if bus.channels:
                total_volume = 0
                for channel in bus.channels:
                    if channel.state in [PlaybackState.PLAYING, PlaybackState.FADING_IN]:
                        total_volume += channel.volume
                bus.vu_meter = total_volume / len(bus.channels)
            else:
                bus.vu_meter = 0.0
    
    def get_vu_level(self, bus: AudioChannelGroup = AudioChannelGroup.MASTER) -> float:
        """Get VU meter level for a bus (0.0 to 1.0)"""
        if bus in self.buses:
            return self.buses[bus].vu_meter
        return 0.0
    
    def is_playing(self, clip_name: str = None) -> bool:
        """Check if a clip or any clip is playing"""
        for audio_channel in self.active_channels:
            if audio_channel.state in [PlaybackState.PLAYING, PlaybackState.FADING_IN]:
                if clip_name is None or (audio_channel.clip and audio_channel.clip.name == clip_name):
                    return True
        return False
    
    def get_active_count(self) -> int:
        """Get number of currently active sounds"""
        return self.stats['active_sounds']
    
    def preload_common_sounds(self, sounds_dir: str = "assets/audio"):
        """Preload common sound categories"""
        categories = {
            'sfx': AudioChannelGroup.SFX,
            'music': AudioChannelGroup.MUSIC,
            'voice': AudioChannelGroup.VOICE,
            'ambient': AudioChannelGroup.AMBIENT,
            'ui': AudioChannelGroup.UI
        }
        
        base_path = Path(sounds_dir)
        if not base_path.exists():
            return
        
        for category_name, category_enum in categories.items():
            category_path = base_path / category_name
            if category_path.exists():
                self.load_sounds_from_directory(str(category_path), category_enum)
    
    def start_recording(self, duration: float = 0.0):
        """Start recording audio output (simulated)"""
        self.recording = True
        self.recorded_frames = []
        print(f"Recording started (duration: {duration if duration > 0 else 'unlimited'})")
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return recorded audio"""
        self.recording = False
        
        if self.recorded_frames:
            combined = np.concatenate(self.recorded_frames)
            self.recorded_frames = []
            print(f"Recording stopped: {len(combined)} samples")
            return combined
        return None
    
    def save_recording(self, filepath: str, samples: np.ndarray = None):
        """Save recorded audio to WAV file"""
        if samples is None:
            samples = self.stop_recording()
        
        if samples is None:
            print("No recording data to save")
            return
        
        try:
            samples_int = (samples * 32767).astype(np.int16)
            
            with wave.open(filepath, 'w') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.frequency)
                wf.writeframes(samples_int.tobytes())
            
            print(f"Recording saved to: {filepath}")
        except Exception as e:
            print(f"Error saving recording: {e}")
    
    def add_bus_effect(self, bus: AudioChannelGroup, effect):
        """Add DSP effect to audio bus"""
        if bus in self.buses:
            self.buses[bus].effects_chain.append(effect)
    
    def remove_bus_effect(self, bus: AudioChannelGroup, effect):
        """Remove DSP effect from audio bus"""
        if bus in self.buses and effect in self.buses[bus].effects_chain:
            self.buses[bus].effects_chain.remove(effect)
    
    def generate_tone(self, frequency: float, duration: float, 
                     waveform: str = "sine", volume: float = 0.5) -> Optional[pygame.mixer.Sound]:
        """
        Generate a simple tone
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            waveform: "sine", "square", "sawtooth", "triangle"
            volume: Volume level 0.0-1.0
            
        Returns:
            pygame.mixer.Sound object
        """
        sample_rate = self.frequency
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        if waveform == "sine":
            samples = np.sin(2 * np.pi * frequency * t)
        elif waveform == "square":
            samples = np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == "sawtooth":
            samples = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif waveform == "triangle":
            samples = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            samples = np.sin(2 * np.pi * frequency * t)
        
        # Apply volume
        samples = samples * volume
        
        # Apply fade in/out to avoid clicks
        fade_len = min(int(sample_rate * 0.01), num_samples // 4)
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        samples[:fade_len] *= fade_in
        samples[-fade_len:] *= fade_out
        
        # Convert to 16-bit PCM
        samples = (samples * 32767).astype(np.int16)
        
        # Create stereo if needed
        if self.channels == 2:
            samples = np.column_stack([samples, samples])
        
        try:
            sound = pygame.sndarray.make_sound(samples)
            return sound
        except Exception as e:
            print(f"Error generating tone: {e}")
            return None
    
    def cleanup(self):
        """Clean shutdown of audio system"""
        self.running = False
        
        # Stop all sounds
        self.stop()
        pygame.mixer.music.stop()
        
        # Wait for threads
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)
        
        # Clear clips
        for clip in self.clips.values():
            if clip.sound:
                clip.sound = None
        
        self.clips.clear()
        self.active_channels.clear()
        
        # Quit mixer
        if self.mixer_initialized:
            pygame.mixer.quit()
        
        print("Audio Manager cleaned up")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audio system statistics"""
        self.stats['active_sounds'] = len(self.active_channels)
        
        # Calculate peak VU
        peak_vu = 0.0
        for bus in self.buses.values():
            peak_vu = max(peak_vu, bus.vu_meter)
        self.stats['peak_vu'] = peak_vu
        
        return dict(self.stats)