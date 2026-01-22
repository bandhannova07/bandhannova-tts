"""
Audio Processing Utilities
"""
import numpy as np
import soundfile as sf
import librosa
from pydub import AudioSegment
import os
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Audio processing and enhancement utilities"""
    
    @staticmethod
    def normalize_audio(audio_path, target_path=None):
        """
        Normalize audio volume
        
        Args:
            audio_path (str): Input audio file path
            target_path (str): Output audio file path (optional)
            
        Returns:
            str: Path to normalized audio
        """
        if target_path is None:
            target_path = audio_path
        
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Normalize to -3dB
            audio = librosa.util.normalize(audio) * 0.7
            
            # Save
            sf.write(target_path, audio, sr)
            logger.info(f"Audio normalized: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio_path
    
    @staticmethod
    def change_speed(audio_path, speed_factor, output_path):
        """
        Change audio playback speed
        
        Args:
            audio_path (str): Input audio file
            speed_factor (float): Speed multiplier (0.5 = half speed, 2.0 = double speed)
            output_path (str): Output file path
            
        Returns:
            str: Path to processed audio
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Change speed using time stretching
            audio_stretched = librosa.effects.time_stretch(audio, rate=speed_factor)
            
            # Save
            sf.write(output_path, audio_stretched, sr)
            logger.info(f"Speed changed to {speed_factor}x: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error changing speed: {e}")
            return audio_path
    
    @staticmethod
    def change_pitch(audio_path, semitones, output_path):
        """
        Change audio pitch
        
        Args:
            audio_path (str): Input audio file
            semitones (int): Number of semitones to shift (-12 to +12)
            output_path (str): Output file path
            
        Returns:
            str: Path to processed audio
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Change pitch
            audio_shifted = librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)
            
            # Save
            sf.write(output_path, audio_shifted, sr)
            logger.info(f"Pitch shifted by {semitones} semitones: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error changing pitch: {e}")
            return audio_path
    
    @staticmethod
    def convert_format(input_path, output_path, output_format='mp3'):
        """
        Convert audio to different format
        
        Args:
            input_path (str): Input audio file
            output_path (str): Output file path
            output_format (str): Target format (mp3, wav, ogg)
            
        Returns:
            str: Path to converted audio
        """
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(input_path)
            
            # Export in target format
            audio.export(output_path, format=output_format)
            logger.info(f"Converted to {output_format}: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting format: {e}")
            return input_path
    
    @staticmethod
    def enhance_quality(audio_path, output_path=None):
        """
        Enhance audio quality with noise reduction and normalization
        
        Args:
            audio_path (str): Input audio file
            output_path (str): Output file path (optional)
            
        Returns:
            str: Path to enhanced audio
        """
        if output_path is None:
            output_path = audio_path
        
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Apply gentle noise reduction (trim silence)
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Normalize
            audio = librosa.util.normalize(audio) * 0.8
            
            # Save
            sf.write(output_path, audio, sr)
            logger.info(f"Audio enhanced: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error enhancing audio: {e}")
            return audio_path
    
    @staticmethod
    def get_audio_duration(audio_path):
        """
        Get audio duration in seconds
        
        Args:
            audio_path (str): Audio file path
            
        Returns:
            float: Duration in seconds
        """
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=audio, sr=sr)
            return duration
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
            return 0.0
