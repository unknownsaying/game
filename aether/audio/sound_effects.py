"""
Advanced Digital Signal Processing (DSP) Effects
Comprehensive audio effects library for real-time processing
"""

import numpy as np
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass, field
import math
import random
from scipy import signal
from scipy.fft import fft, ifft, fftfreq

class AudioEffect:
    """Base class for all audio effects"""
    
    def __init__(self, name: str = "Effect"):
        self.name = name
        self.enabled = True
        self.wet_dry_mix = 0.5  # 0.0 = dry only, 1.0 = wet only
        self.sample_rate = 44100
    
    def process(self, samples: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        """
        Process audio samples
        
        Args:
            samples: Input audio samples (1D or 2D array)
            sample_rate: Sample rate in Hz
            
        Returns:
            Processed audio samples
        """
        self.sample_rate = sample_rate
        
        if not self.enabled:
            return samples
        
        # Handle mono/stereo
        is_stereo = len(samples.shape) > 1 and samples.shape[1] == 2
        
        if is_stereo:
            left = self._process_channel(samples[:, 0], sample_rate)
            right = self._process_channel(samples[:, 1], sample_rate)
            processed = np.column_stack([left, right])
        else:
            processed = self._process_channel(samples, sample_rate)
        
        # Wet/dry mix
        if self.wet_dry_mix < 1.0:
            result = (1.0 - self.wet_dry_mix) * samples + self.wet_dry_mix * processed
        else:
            result = processed
        
        return result.astype(samples.dtype)
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process a single channel - override in subclasses"""
        return samples
    
    def reset(self):
        """Reset effect state"""
        pass

class Reverb(AudioEffect):
    """
    Advanced reverb effect using Schroeder-Moorer algorithm
    with early reflections and late reverberation
    """
    
    def __init__(self, 
                 room_size: float = 0.5,
                 damping: float = 0.5,
                 wet_level: float = 0.3,
                 dry_level: float = 0.7,
                 width: float = 1.0,
                 freeze_mode: float = 0.0):
        super().__init__("Reverb")
        
        self.room_size = np.clip(room_size, 0.0, 1.0)
        self.damping = np.clip(damping, 0.0, 1.0)
        self.wet_level = wet_level
        self.dry_level = dry_level
        self.width = width
        self.freeze_mode = freeze_mode
        
        # Comb filter parameters
        self.comb_tuning = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617]
        self.allpass_tuning = [556, 441, 341, 225]
        
        # Delay buffers
        self.comb_buffers = [np.zeros(n) for n in self.comb_tuning]
        self.comb_indices = [0] * len(self.comb_tuning)
        
        self.allpass_buffers = [np.zeros(n) for n in self.allpass_tuning]
        self.allpass_indices = [0] * len(self.allpass_tuning)
        
        # State
        self.lowpass_state = 0.0
        self.wet_dry_mix = wet_level / (wet_level + dry_level) if (wet_level + dry_level) > 0 else 0.5
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process samples through reverb network"""
        # Scale delay times based on sample rate
        scale = sample_rate / 44100.0
        
        # Adjust comb filter times
        scaled_comb = [int(t * scale * (0.5 + self.room_size * 0.5)) for t in self.comb_tuning]
        scaled_allpass = [int(t * scale * (0.5 + self.room_size * 0.5)) for t in self.allpass_tuning]
        
        # Ensure minimum delay lengths
        scaled_comb = [max(1, t) for t in scaled_comb]
        scaled_allpass = [max(1, t) for t in scaled_allpass]
        
        # Resize buffers if needed
        for i, size in enumerate(scaled_comb):
            if len(self.comb_buffers[i]) != size:
                self.comb_buffers[i] = np.zeros(size)
                self.comb_indices[i] = 0
        
        for i, size in enumerate(scaled_allpass):
            if len(self.allpass_buffers[i]) != size:
                self.allpass_buffers[i] = np.zeros(size)
                self.allpass_indices[i] = 0
        
        output = np.zeros_like(samples)
        damping_factor = 0.4 * self.damping
        
        for i, sample in enumerate(samples):
            input_sample = sample
            
            # Parallel comb filters
            comb_output = 0.0
            for j in range(len(self.comb_buffers)):
                buf = self.comb_buffers[j]
                idx = self.comb_indices[j]
                
                # Read delayed sample
                delayed = buf[idx]
                
                # Lowpass filter in feedback loop
                self.lowpass_state = delayed + damping_factor * (self.lowpass_state - delayed)
                
                # Write new sample with feedback
                if self.freeze_mode > 0.5:
                    buf[idx] = delayed + input_sample * 0.015
                else:
                    buf[idx] = input_sample + self.lowpass_state * 0.85
                
                # Advance index
                self.comb_indices[j] = (idx + 1) % len(buf)
                
                comb_output += delayed
            
            comb_output *= 0.25  # Scale back
            
            # Series allpass filters
            allpass_input = comb_output
            for j in range(len(self.allpass_buffers)):
                buf = self.allpass_buffers[j]
                idx = self.allpass_indices[j]
                
                delayed = buf[idx]
                
                # Allpass difference equation
                buf[idx] = allpass_input + delayed * 0.5
                allpass_input = delayed - allpass_input * 0.5
                
                self.allpass_indices[j] = (idx + 1) % len(buf)
            
            output[i] = allpass_input
        
        return output

class Echo(AudioEffect):
    """
    Advanced echo/delay effect with multiple taps, 
    feedback, and modulation
    """
    
    def __init__(self,
                 delay_time: float = 0.3,
                 feedback: float = 0.4,
                 mix: float = 0.5,
                 num_echoes: int = 5,
                 stereo_spread: float = 0.5,
                 modulation_rate: float = 0.5,
                 modulation_depth: float = 0.002):
        super().__init__("Echo")
        
        self.delay_time = delay_time  # seconds
        self.feedback = np.clip(feedback, 0.0, 0.95)
        self.mix = mix
        self.num_echoes = num_echoes
        self.stereo_spread = stereo_spread
        self.modulation_rate = modulation_rate
        self.modulation_depth = modulation_depth
        
        # Delay buffers
        self.delay_buffers = None
        self.write_position = 0
        self.sample_counter = 0
        self.wet_dry_mix = mix
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process samples through delay line with modulation"""
        delay_samples = int(self.delay_time * sample_rate)
        
        # Allocate buffer with extra space for modulation
        buffer_size = delay_samples + int(self.modulation_depth * sample_rate * 4) + 1
        
        if(self.delay_buffers is None or len(self.delay_buffers) != buffer_size):
            self.delay_buffers = np.zeros(buffer_size)
            self.write_position = 0
        
        output = np.zeros_like(samples)
        
        for i, sample in enumerate(samples):
            # Calculate modulated delay time
            mod = math.sin(2 * math.pi * self.modulation_rate * self.sample_counter / sample_rate)
            mod *= self.modulation_depth * sample_rate
            
            current_delay = delay_samples + int(mod)
            current_delay = max(1, min(current_delay, buffer_size - 1))
            
            # Read from buffer with interpolation
            read_pos = (self.write_position - current_delay) % buffer_size
            read_pos_floor = int(read_pos)
            read_pos_frac = read_pos - read_pos_floor
            
            read_pos_next = (read_pos_floor + 1) % buffer_size
            
            delayed = (self.delay_buffers[read_pos_floor] * (1 - read_pos_frac) +
                      self.delay_buffers[read_pos_next] * read_pos_frac)
            
            # Write to buffer with feedback
            self.delay_buffers[self.write_position] = sample + delayed * self.feedback
            
            # Advance write position
            self.write_position = (self.write_position + 1) % buffer_size
            
            # Mix
            output[i] = delayed
            self.sample_counter += 1
        
        return output
    
    def reset(self):
        """Reset echo buffer"""
        self.delay_buffers = None
        self.write_position = 0
        self.sample_counter = 0

class Chorus(AudioEffect):
    """
    Chorus effect using multiple modulated delay lines
    Creates rich, ensemble-like sound
    """
    
    def __init__(self,
                 rate: float = 1.2,
                 depth: float = 0.003,
                 mix: float = 0.5,
                 voices: int = 3,
                 spread: float = 0.5):
        super().__init__("Chorus")
        
        self.rate = rate
        self.depth = depth
        self.mix = mix
        self.voices = voices
        self.spread = spread
        
        # Multiple delay lines
        self.delay_buffers = []
        self.phases = []
        self.wet_dry_mix = mix
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process through multiple modulated delays"""
        base_delay = int(0.01 * sample_rate)  # 10ms base delay
        mod_depth = int(self.depth * sample_rate)
        buffer_size = base_delay + mod_depth * 2 + 1
        
        # Initialize buffers
        if len(self.delay_buffers) != self.voices:
            self.delay_buffers = [np.zeros(buffer_size) for _ in range(self.voices)]
            self.phases = [2 * math.pi * i / self.voices for i in range(self.voices)]
        
        output = np.zeros_like(samples)
        
        for i, sample in enumerate(samples):
            voice_output = 0.0
            
            for v in range(self.voices):
                # Update phase
                self.phases[v] += 2 * math.pi * self.rate / sample_rate
                if self.phases[v] > 2 * math.pi:
                    self.phases[v] -= 2 * math.pi
                
                # Calculate modulated delay
                mod = math.sin(self.phases[v]) * mod_depth * (1.0 + v * self.spread * 0.5)
                delay = base_delay + int(mod)
                delay = max(1, min(delay, buffer_size - 1))
                
                # Read from buffer
                buf = self.delay_buffers[v]
                write_pos = i % buffer_size
                read_pos = (write_pos - delay) % buffer_size
                
                voice_output += buf[read_pos]
                
                # Write to buffer
                buf[write_pos] = sample
            
            output[i] = voice_output / self.voices
        
        return output

class Flanger(AudioEffect):
    """
    Flanger effect - similar to chorus but with feedback
    Creates sweeping, jet-like sounds
    """
    
    def __init__(self,
                 rate: float = 0.5,
                 depth: float = 0.002,
                 feedback: float = 0.7,
                 mix: float = 0.5):
        super().__init__("Flanger")
        
        self.rate = rate
        self.depth = depth
        self.feedback = np.clip(feedback, -0.95, 0.95)
        self.mix = mix
        
        self.delay_buffer = None
        self.phase = 0.0
        self.feedback_sample = 0.0
        self.wet_dry_mix = mix
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process through modulated delay with feedback"""
        base_delay = int(0.005 * sample_rate)  # 5ms
        mod_depth = int(self.depth * sample_rate)
        buffer_size = base_delay + mod_depth * 2 + 1
        
        if self.delay_buffer is None or len(self.delay_buffer) != buffer_size:
            self.delay_buffer = np.zeros(buffer_size)
        
        output = np.zeros_like(samples)
        
        for i, sample in enumerate(samples):
            # Update LFO
            self.phase += 2 * math.pi * self.rate / sample_rate
            if self.phase > 2 * math.pi:
                self.phase -= 2 * math.pi
            
            # Calculate modulated delay
            mod = math.sin(self.phase) * mod_depth
            delay = base_delay + int(mod)
            delay = max(1, min(delay, buffer_size - 1))
            
            # Read from buffer
            write_pos = i % buffer_size
            read_pos = (write_pos - delay) % buffer_size
            delayed = self.delay_buffer[read_pos]
            
            # Write with feedback
            self.delay_buffer[write_pos] = sample + self.feedback * self.feedback_sample
            
            # Update feedback
            self.feedback_sample = delayed * 0.7 + self.feedback_sample * 0.3
            
            output[i] = delayed
        
        return output

class Distortion(AudioEffect):
    """
    Distortion/overdrive effect with various clipping algorithms
    """
    
    def __init__(self,
                 drive: float = 5.0,
                 tone: float = 0.5,
                 mix: float = 0.5,
                 mode: str = "hard"):
        super().__init__("Distortion")
        
        self.drive = drive
        self.tone = tone
        self.mix = mix
        self.mode = mode
        
        # Tone filter state
        self.lp_state = 0.0
        self.hp_state = 0.0
        self.wet_dry_mix = mix
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply distortion to samples"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        # Pre-gain
        gain = 1.0 + self.drive * 10.0
        
        for i, sample in enumerate(samples):
            # Apply gain
            x = sample * gain
            
            # Clipping algorithm
            if self.mode == "hard":
                # Hard clipping
                x = np.clip(x, -1.0, 1.0)
            elif self.mode == "soft":
                # Soft clipping (tanh)
                x = np.tanh(x)
            elif self.mode == "tube":
                # Tube-like asymmetric clipping
                if x > 0:
                    x = np.tanh(x * 0.8)
                else:
                    x = np.tanh(x * 1.2) * 0.8
            elif self.mode == "fuzz":
                # Square wave fuzz
                x = np.sign(x) * (1 - np.exp(-abs(x)))
            
            # Tone control (simple RC filter)
            tone_freq = self.tone * 5000.0 + 500.0
            rc = 1.0 / (2 * np.pi * tone_freq)
            dt = 1.0 / sample_rate
            alpha = dt / (rc + dt)
            
            self.lp_state += alpha * (x - self.lp_state)
            output[i] = self.lp_state
        
        return output

class EQ(AudioEffect):
    """
    Multi-band equalizer using cascaded biquad filters
    """
    
    def __init__(self,
                 low_gain: float = 0.0,
                 mid_gain: float = 0.0,
                 high_gain: float = 0.0,
                 low_freq: float = 200.0,
                 mid_freq: float = 1000.0,
                 high_freq: float = 5000.0):
        super().__init__("EQ")
        
        self.low_gain = low_gain
        self.mid_gain = mid_gain
        self.high_gain = high_gain
        self.low_freq = low_freq
        self.mid_freq = mid_freq
        self.high_freq = high_freq
        
        # Filter states
        self.low_state = np.zeros(2)
        self.mid_state = np.zeros(4)
        self.high_state = np.zeros(2)
        self.wet_dry_mix = 1.0  # EQ is always 100% wet
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply three-band EQ"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        dt = 1.0 / sample_rate
        
        # Calculate filter coefficients
        # Low shelf
        w0 = 2 * np.pi * self.low_freq
        low_a = w0 * dt / (2 + w0 * dt)
        
        # High shelf  
        w0 = 2 * np.pi * self.high_freq
        high_a = 2 / (2 + w0 * dt)
        
        for i, sample in enumerate(samples):
            # Low shelf
            self.low_state[0] += low_a * (sample - self.low_state[0])
            low = self.low_state[1] + low_a * (self.low_state[0] - self.low_state[1])
            self.low_state[1] = low
            
            # Mid bandpass (2nd order)
            w0 = 2 * np.pi * self.mid_freq
            q = 0.707
            alpha = math.sin(w0 * dt) / (2 * q)
            
            # Simplified mid processing (state variable filter)
            bp = sample - self.mid_state[0] - self.mid_state[1] * q
            self.mid_state[0] += w0 * dt * self.mid_state[1]
            self.mid_state[1] += w0 * dt * bp
            mid = self.mid_state[1]
            
            # High shelf
            high = sample - low
            
            # Mix bands
            output[i] = (sample + 
                        low * (pow(10, self.low_gain/20) - 1) +
                        mid * (pow(10, self.mid_gain/20) - 1) +
                        high * (pow(10, self.high_gain/20) - 1))
        
        return np.clip(output, -1.0, 1.0)

class Compressor(AudioEffect):
    """
    Dynamic range compressor with soft knee
    """
    
    def __init__(self,
                 threshold: float = -20.0,  # dB
                 ratio: float = 4.0,
                 attack: float = 0.005,     # seconds
                 release: float = 0.1,      # seconds
                 makeup_gain: float = 0.0):  # dB
        super().__init__("Compressor")
        
        self.threshold = threshold
        self.ratio = ratio
        self.attack = attack
        self.release = release
        self.makeup_gain = makeup_gain
        
        # State
        self.envelope = 0.0
        self.wet_dry_mix = 1.0
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply compression"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        attack_coeff = math.exp(-1.0 / (sample_rate * self.attack))
        release_coeff = math.exp(-1.0 / (sample_rate * self.release))
        
        threshold_linear = pow(10, self.threshold / 20)
        makeup_linear = pow(10, self.makeup_gain / 20)
        
        for i, sample in enumerate(samples):
            # Level detection (RMS-like)
            level = abs(sample)
            
            # Envelope follower
            if level > self.envelope:
                self.envelope = attack_coeff * self.envelope + (1 - attack_coeff) * level
            else:
                self.envelope = release_coeff * self.envelope + (1 - release_coeff) * level
            
            # Gain reduction
            if self.envelope > threshold_linear:
                # Above threshold
                db_over = 20 * math.log10(self.envelope / threshold_linear)
                gain_reduction_db = db_over * (1 - 1/self.ratio)
                gain_reduction = pow(10, -gain_reduction_db / 20)
            else:
                gain_reduction = 1.0
            
            # Apply gain
            output[i] = sample * gain_reduction * makeup_linear
        
        return np.clip(output, -1.0, 1.0)

class PitchShift(AudioEffect):
    """
    Pitch shifting using phase vocoder technique
    """
    
    def __init__(self, semitones: float = 0.0):
        super().__init__("PitchShift")
        self.semitones = semitones
        self.wet_dry_mix = 1.0
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Shift pitch by resampling and time-stretching"""
        if self.semitones == 0:
            return samples
        
        # Pitch shift factor
        factor = 2.0 ** (self.semitones / 12.0)
        
        # Simple implementation: linear interpolation resampling
        old_len = len(samples)
        new_len = int(old_len / factor)
        
        if new_len < 1:
            return np.zeros(1)
        
        # Create time arrays
        old_indices = np.linspace(0, old_len - 1, new_len)
        
        # Interpolate
        shifted = np.interp(old_indices, np.arange(old_len), samples)
        
        # If we need to match length, stretch/compress
        if len(shifted) != old_len:
            indices = np.linspace(0, len(shifted) - 1, old_len)
            shifted = np.interp(indices, np.arange(len(shifted)), shifted)
        
        return shifted

class AutoWah(AudioEffect):
    """
    Auto-wah/envelope filter effect
    Creates "wah-wah" sound based on input amplitude
    """
    
    def __init__(self,
                 sensitivity: float = 0.5,
                 resonance: float = 0.5,
                 min_freq: float = 200.0,
                 max_freq: float = 2000.0):
        super().__init__("AutoWah")
        
        self.sensitivity = sensitivity
        self.resonance = resonance
        self.min_freq = min_freq
        self.max_freq = max_freq
        
        # Filter state
        self.lp = 0.0
        self.bp = 0.0
        self.hp = 0.0
        self.envelope = 0.0
        self.wet_dry_mix = 0.7
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply auto-wah effect"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        env_attack = math.exp(-1.0 / (sample_rate * 0.01))
        env_release = math.exp(-1.0 / (sample_rate * 0.05))
        
        for i, sample in enumerate(samples):
            # Envelope follower
            level = abs(sample)
            if level > self.envelope:
                self.envelope = env_attack * self.envelope + (1 - env_attack) * level
            else:
                self.envelope = env_release * self.envelope + (1 - env_release) * level
            
            # Map envelope to frequency
            env_scaled = self.envelope * self.sensitivity * 5
            freq = self.min_freq + (self.max_freq - self.min_freq) * min(1.0, env_scaled)
            
            # State variable filter
            f = 2 * math.sin(math.pi * freq / sample_rate)
            q = 1.0 - self.resonance * 0.95
            
            self.hp = sample - self.lp - q * self.bp
            self.bp += f * self.hp
            self.lp += f * self.bp
            
            output[i] = self.bp * 2
            
        return output

class Vibrato(AudioEffect):
    """
    Vibrato effect - periodic pitch modulation
    """
    
    def __init__(self,
                 rate: float = 5.0,
                 depth: float = 0.003,
                 waveform: str = "sine"):
        super().__init__("Vibrato")
        
        self.rate = rate
        self.depth = depth
        self.waveform = waveform
        self.phase = 0.0
        self.wet_dry_mix = 1.0
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply vibrato using modulated delay"""
        max_delay = int(self.depth * sample_rate * 2) + 1
        buffer = np.zeros(max_delay)
        output = np.zeros_like(samples, dtype=np.float64)
        
        write_pos = 0
        
        for i, sample in enumerate(samples):
            # LFO
            self.phase += 2 * math.pi * self.rate / sample_rate
            if self.phase > 2 * math.pi:
                self.phase -= 2 * math.pi
            
            # Modulation amount
            if self.waveform == "sine":
                mod = math.sin(self.phase)
            elif self.waveform == "triangle":
                mod = 2 * abs(self.phase / math.pi - 1) - 1
            elif self.waveform == "square":
                mod = 1.0 if self.phase < math.pi else -1.0
            else:
                mod = math.sin(self.phase)
            
            delay = int(self.depth * sample_rate * (1 + mod * 0.5))
            delay = max(1, min(delay, max_delay - 1))
            
            read_pos = (write_pos - delay) % max_delay
            output[i] = buffer[read_pos]
            
            buffer[write_pos] = sample
            write_pos = (write_pos + 1) % max_delay
        
        return output

class Tremolo(AudioEffect):
    """
    Tremolo effect - periodic amplitude modulation
    """
    
    def __init__(self,
                 rate: float = 5.0,
                 depth: float = 0.5,
                 waveform: str = "sine",
                 stereo_phase: float = 0.0):
        super().__init__("Tremolo")
        
        self.rate = rate
        self.depth = depth
        self.waveform = waveform
        self.stereo_phase = stereo_phase
        self.phase = 0.0
        self.wet_dry_mix = 1.0
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply amplitude modulation"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        for i, sample in enumerate(samples):
            self.phase += 2 * math.pi * self.rate / sample_rate
            if self.phase > 2 * math.pi:
                self.phase -= 2 * math.pi
            
            # LFO waveform
            if self.waveform == "sine":
                lfo = math.sin(self.phase)
            elif self.waveform == "triangle":
                lfo = 2 * abs(self.phase / math.pi - 1) - 1
            elif self.waveform == "square":
                lfo = 1.0 if self.phase < math.pi else -1.0
            else:
                lfo = math.sin(self.phase)
            
            # Modulate amplitude
            amplitude = 1.0 - self.depth * (1.0 - (lfo + 1.0) / 2.0)
            output[i] = sample * amplitude
        
        return output

class BitCrusher(AudioEffect):
    """
    Bit crusher - reduces bit depth and sample rate
    Creates lo-fi, retro game sounds
    """
    
    def __init__(self,
                 bit_depth: int = 8,
                 downsample_factor: int = 1):
        super().__init__("BitCrusher")
        
        self.bit_depth = max(1, min(16, bit_depth))
        self.downsample_factor = max(1, downsample_factor)
        
        self.held_sample = 0.0
        self.sample_count = 0
        self.wet_dry_mix = 0.8
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply bit crushing and downsampling"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        # Calculate quantization levels
        levels = 2 ** self.bit_depth
        quantize_step = 2.0 / levels
        
        for i, sample in enumerate(samples):
            # Downsample
            self.sample_count += 1
            if self.sample_count >= self.downsample_factor:
                self.held_sample = sample
                self.sample_count = 0
            
            # Quantize (reduce bit depth)
            quantized = quantize_step * np.floor(self.held_sample / quantize_step + 0.5)
            
            output[i] = quantized
        
        return output

class RingModulator(AudioEffect):
    """
    Ring modulator - multiplies signal with carrier frequency
    Creates metallic, bell-like sounds
    """
    
    def __init__(self,
                 frequency: float = 440.0,
                 mix: float = 0.5,
                 waveform: str = "sine"):
        super().__init__("RingModulator")
        
        self.frequency = frequency
        self.mix = mix
        self.waveform = waveform
        self.phase = 0.0
        self.wet_dry_mix = mix
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply ring modulation"""
        output = np.zeros_like(samples, dtype=np.float64)
        
        for i, sample in enumerate(samples):
            self.phase += 2 * math.pi * self.frequency / sample_rate
            if self.phase > 2 * math.pi:
                self.phase -= 2 * math.pi
            
            # Carrier signal
            if self.waveform == "sine":
                carrier = math.sin(self.phase)
            elif self.waveform == "square":
                carrier = 1.0 if math.sin(self.phase) > 0 else -1.0
            elif self.waveform == "triangle":
                carrier = 2 * abs(self.phase / math.pi - 1) - 1
            else:
                carrier = math.sin(self.phase)
            
            output[i] = sample * carrier
        
        return output

class ConvolutionReverb(AudioEffect):
    """
    Convolution reverb using impulse responses
    """
    
    def __init__(self, impulse_response: np.ndarray = None):
        super().__init__("ConvolutionReverb")
        self.impulse_response = impulse_response
        self.wet_dry_mix = 0.3
    
    def load_impulse(self, filepath: str, sample_rate: int = 44100):
        """Load impulse response from file"""
        try:
            import wave
            with wave.open(filepath, 'r') as wf:
                n_frames = wf.getnframes()
                data = wf.readframes(n_frames)
                ir = np.frombuffer(data, dtype=np.int16).astype(np.float64) / 32768.0
                
                if wf.getnchannels() == 2:
                    # Convert to mono
                    ir = ir.reshape(-1, 2).mean(axis=1)
                
                self.impulse_response = ir
                print(f"Loaded impulse response: {len(ir)} samples")
        except Exception as e:
            print(f"Error loading impulse response: {e}")
    
    def _process_channel(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply convolution with impulse response"""
        if self.impulse_response is None or len(self.impulse_response) == 0:
            return samples
        
        # Perform convolution using FFT for efficiency
        try:
            conv_length = len(samples) + len(self.impulse_response) - 1
            
            # FFT sizes (power of 2)
            fft_size = 1
            while fft_size < conv_length:
                fft_size *= 2
            
            # FFT of both signals
            signal_fft = fft(samples, fft_size)
            ir_fft = fft(self.impulse_response, fft_size)
            
            # Multiply in frequency domain
            result_fft = signal_fft * ir_fft
            
            # Inverse FFT
            result = np.real(ifft(result_fft))
            
            # Trim to original length
            return result[:len(samples)]
        except:
            # Fallback to direct convolution for short IRs
            return np.convolve(samples, self.impulse_response, mode='same')

class AudioEffectChain:
    """
    Chain multiple audio effects together
    """
    
    def __init__(self):
        self.effects: List[AudioEffect] = []
        self.master_volume = 1.0
    
    def add_effect(self, effect: AudioEffect):
        """Add effect to chain"""
        self.effects.append(effect)
    
    def remove_effect(self, effect: AudioEffect):
        """Remove effect from chain"""
        if effect in self.effects:
            self.effects.remove(effect)
    
    def insert_effect(self, index: int, effect: AudioEffect):
        """Insert effect at specific position"""
        self.effects.insert(index, effect)
    
    def process(self, samples: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        """Process audio through all effects in chain"""
        result = samples
        for effect in self.effects:
            if effect.enabled:
                result = effect.process(result, sample_rate)
        
        # Apply master volume
        result *= self.master_volume
        
        return result
    
    def bypass_all(self):
        """Bypass all effects"""
        for effect in self.effects:
            effect.enabled = False
    
    def enable_all(self):
        """Enable all effects"""
        for effect in self.effects:
            effect.enabled = True
    
    def reset_all(self):
        """Reset all effects"""
        for effect in self.effects:
            effect.reset()
    
    def get_effect_by_name(self, name: str) -> Optional[AudioEffect]:
        """Find effect by name"""
        for effect in self.effects:
            if effect.name.lower() == name.lower():
                return effect
        return None


# Utility functions for audio processing
def normalize_audio(samples: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    """Normalize audio to target peak level"""
    peak = np.max(np.abs(samples))
    if peak > 0:
        return samples * (target_peak / peak)
    return samples

def fade_in_out(samples: np.ndarray, 
                fade_in_duration: float = 0.01,
                fade_out_duration: float = 0.01,
                sample_rate: int = 44100) -> np.ndarray:
    """Apply fade in and fade out to avoid clicks"""
    result = samples.copy()
    fade_in_samples = int(fade_in_duration * sample_rate)
    fade_out_samples = int(fade_out_duration * sample_rate)
    
    if fade_in_samples > 0:
        fade_in = np.linspace(0, 1, min(fade_in_samples, len(result)))
        result[:len(fade_in)] *= fade_in
    
    if fade_out_samples > 0:
        fade_out = np.linspace(1, 0, min(fade_out_samples, len(result)))
        result[-len(fade_out):] *= fade_out
    
    return result

def mix_tracks(tracks: List[np.ndarray], volumes: List[float] = None) -> np.ndarray:
    """Mix multiple audio tracks together"""
    if not tracks:
        return np.array([])
    
    max_length = max(len(track) for track in tracks)
    mixed = np.zeros(max_length)
    
    for i, track in enumerate(tracks):
        volume = volumes[i] if volumes and i < len(volumes) else 1.0
        mixed[:len(track)] += track * volume
    
    # Prevent clipping
    peak = np.max(np.abs(mixed))
    if peak > 1.0:
        mixed /= peak
    
    return mixed

def apply_envelope(samples: np.ndarray, 
                   attack: float = 0.01,
                   decay: float = 0.1,
                   sustain: float = 0.7,
                   release: float = 0.2,
                   sample_rate: int = 44100) -> np.ndarray:
    """Apply ADSR envelope to audio"""
    total_samples = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)
    
    envelope = np.zeros(total_samples)
    
    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    if decay_samples > 0:
        end_attack = attack_samples
        end_decay = end_attack + decay_samples
        envelope[end_attack:end_decay] = np.linspace(1, sustain, decay_samples)
    
    # Sustain
    if sustain_samples > 0:
        end_decay = attack_samples + decay_samples
        end_sustain = end_decay + sustain_samples
        envelope[end_decay:end_sustain] = sustain
    
    # Release
    if release_samples > 0:
        end_sustain = total_samples - release_samples
        envelope[end_sustain:] = np.linspace(sustain, 0, release_samples)
    
    return samples * envelope