"""
free_video_generator.py

Standalone module for FREE AI video generation and YouTube upload
Uses:
- Hugging Face Diffusers (FREE, local)
- Gemini API (FREE tier)
- FFmpeg (FREE, open source)
- YouTube Data API v3 (FREE tier)
"""

import os
import logging
import json
import base64
import requests
import pickle
from pathlib import Path
from typing import Optional, Dict, List
import subprocess
import time

# Try to import optional dependencies
try:
    from diffusers import TextToVideoSDPipeline
    import torch
    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False
    logging.warning("Diffusers not installed. Install with: pip install diffusers torch")

try:
    import google.generativeai as genai
    from google.auth.oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False
    logging.warning("Google API libraries not installed")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 1. FREE VIDEO GENERATION (Hugging Face Diffusers - Local)
# ============================================================================

class HuggingFaceVideoGenerator:
    """Generate videos using free Hugging Face Diffusers models (runs locally)"""
    
    def __init__(self):
        if not HAS_DIFFUSERS:
            raise RuntimeError(
                "Diffusers library required. Install with:\n"
                "pip install diffusers transformers accelerate"
            )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        self.pipe = None
    
    def load_model(self, model_id: str = "damo-vilab/text-to-video-ms-4.7b"):
        """
        Load a free text-to-video model
        
        Available free models:
        - "damo-vilab/text-to-video-ms-4.7b" (Recommended - faster)
        - "stabilityai/stable-video-diffusion-img2vid" (needs image input)
        """
        logger.info(f"Loading model: {model_id}")
        try:
            self.pipe = TextToVideoSDPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                variant="fp16" if self.device == "cuda" else None
            )
            self.pipe.to(self.device)
            if self.device == "cuda":
                self.pipe.enable_attention_slicing()
            logger.info("✅ Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_video(self, prompt: str, output_path: str, num_frames: int = 16, height: int = 320, width: int = 576) -> bool:
        """
        Generate a video from text prompt (FREE, runs locally)
        
        Args:
            prompt: Description of video to generate
            output_path: Where to save the video
            num_frames: Number of frames (16 = ~1 second at 16fps)
            height: Video height (default 320)
            width: Video width (default 576)
        
        Returns:
            True if successful
        """
        if not self.pipe:
            self.load_model()
        
        logger.info(f"🎬 Generating video from prompt: {prompt}")
        logger.info(f"   Frames: {num_frames}, Resolution: {width}x{height}")
        
        try:
            with torch.no_grad():
                video_frames = self.pipe(
                    prompt,
                    height=height,
                    width=width,
                    num_frames=num_frames,
                    num_inference_steps=25,
                    guidance_scale=9.0
                ).frames
            
            # Save frames as video using imageio
            import imageio
            output_path = str(output_path).replace('\\', '/')
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            logger.info(f"Saving video to {output_path}")
            imageio.mimwrite(output_path, video_frames[0], fps=8)
            
            logger.info(f"✅ Video saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            return False

# ============================================================================
# 2. FREE TTS AUDIO (Using Gemini TTS API - Free Tier)
# ============================================================================

class FreeGeminiTTS:
    """Generate speech using free Gemini 2.5 TTS API"""
    
    def __init__(self, api_key: str):
        if not HAS_GOOGLE_API:
            raise RuntimeError("google-generativeai not installed. Install with: pip install google-generativeai")
        
        self.api_key = api_key
        genai.configure(api_key=api_key)
        logger.info("✅ Gemini TTS initialized")
    
    def generate_audio(self, text: str, output_path: str, voice_name: str = "Kore") -> bool:
        """
        Generate speech from text using Gemini TTS (FREE)
        
        Available voices:
        - Kore, Puck, Chime, Aoede, Fenrir, Gigasaurus
        - See: https://ai.google.dev/docs/api_features#text_to_speech
        """
        logger.info(f"🎙️ Generating audio with voice: {voice_name}")
        
        try:
            api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"
            
            payload = {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": voice_name
                            }
                        }
                    }
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{api_url}?key={self.api_key}",
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            audio_data = response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            audio_bytes = base64.b64decode(audio_data)
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            logger.info(f"✅ Audio saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            return False

# ============================================================================
# 3. VIDEO + AUDIO COMPOSITION (Using FFmpeg - FREE)
# ============================================================================

class FFmpegComposer:
    """Compose video and audio using free FFmpeg"""
    
    @staticmethod
    def combine_video_audio(video_path: str, audio_path: str, output_path: str) -> bool:
        """Combine video and audio files using FFmpeg"""
        logger.info(f"🎬 Combining video and audio with FFmpeg...")
        
        try:
            cmd = [
                "ffmpeg", "-i", video_path, "-i", audio_path,
                "-c:v", "copy", "-c:a", "aac", "-shortest",
                output_path, "-y"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info(f"✅ Final video saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ FFmpeg composition failed: {e}")
            return False
    
    @staticmethod
    def create_slideshow_from_images(image_dir: str, audio_path: str, output_path: str, duration_per_image: float = 2.0) -> bool:
        """Create video from images with audio"""
        logger.info(f"📸 Creating slideshow from images...")
        
        try:
            images = sorted([f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            if not images:
                logger.error("No images found in directory")
                return False
            
            # Create video from images
            input_pattern = os.path.join(image_dir, f"img_%03d.png")
            video_temp = "temp_slideshow.mp4"
            
            cmd = [
                "ffmpeg", "-framerate", str(1/duration_per_image),
                "-i", input_pattern,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                video_temp, "-y"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            # Add audio
            cmd_audio = [
                "ffmpeg", "-i", video_temp, "-i", audio_path,
                "-c:v", "copy", "-c:a", "aac", "-shortest",
                output_path, "-y"
            ]
            
            result = subprocess.run(cmd_audio, capture_output=True, text=True)
            os.remove(video_temp)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info(f"✅ Slideshow saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Slideshow creation failed: {e}")
            return False

# ============================================================================
# 4. FREE YOUTUBE UPLOAD (YouTube Data API v3 - Free Tier)
# ============================================================================

class YouTubeUploader:
    """Upload videos to YouTube using free API"""
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    TOKEN_FILE = "youtube_token.pickle"
    CREDENTIALS_FILE = "credentials.json"
    
    def __init__(self):
        if not HAS_GOOGLE_API:
            raise RuntimeError("Google API libraries required")
        
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0"""
        logger.info("🔐 Authenticating with YouTube...")
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
                logger.info("✅ Loaded existing token")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if not os.path.exists(self.CREDENTIALS_FILE):
                logger.error(f"❌ {self.CREDENTIALS_FILE} not found!")
                logger.error("Get credentials from: https://console.cloud.google.com")
                raise FileNotFoundError(self.CREDENTIALS_FILE)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.CREDENTIALS_FILE, self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
                logger.info("✅ New token saved")
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("✅ YouTube API authenticated")
    
    def upload_video(self, file_path: str, title: str, description: str = "", tags: List[str] = None, privacy: str = "private") -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            file_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            privacy: "public", "private", or "unlisted"
        
        Returns:
            Video ID if successful, None otherwise
        """
        logger.info(f"📤 Uploading video: {title}")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return None
        
        try:
            body = {
                "snippet": {
                    "title": title[:100],  # Max 100 chars
                    "description": description[:5000],  # Max 5000 chars
                    "tags": tags or [],
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": privacy
                }
            }
            
            media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            logger.info(f"✅ Video uploaded! ID: {video_id}")
            logger.info(f"   View at: https://www.youtube.com/watch?v={video_id}")
            
            return video_id
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return None

# ============================================================================
# 5. COMPLETE PIPELINE
# ============================================================================

class FreeVideoAutomationPipeline:
    """Complete FREE video generation and upload pipeline"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.video_gen = None
        self.tts = FreeGeminiTTS(gemini_api_key)
        self.composer = FFmpegComposer()
        self.uploader = YouTubeUploader()
    
    def generate_and_upload(self, topic: str, script: str, title: str, tags: List[str], privacy: str = "private") -> bool:
        """Complete pipeline: Generate video + audio, compose, and upload"""
        
        output_dir = f"output_{int(time.time())}"
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 1. Generate video
            video_path = os.path.join(output_dir, "video.mp4")
            logger.info("Step 1/4: Generating video...")
            
            self.video_gen = HuggingFaceVideoGenerator()
            video_prompt = f"Professional video about {topic}: {script[:100]}"
            
            if not self.video_gen.generate_video(video_prompt, video_path):
                logger.error("Video generation failed")
                return False
            
            # 2. Generate audio
            audio_path = os.path.join(output_dir, "audio.wav")
            logger.info("Step 2/4: Generating audio...")
            
            if not self.tts.generate_audio(script, audio_path):
                logger.error("Audio generation failed")
                return False
            
            # 3. Combine video and audio
            final_video = os.path.join(output_dir, "final_video.mp4")
            logger.info("Step 3/4: Composing final video...")
            
            if not self.composer.combine_video_audio(video_path, audio_path, final_video):
                logger.error("Video composition failed")
                return False
            
            # 4. Upload to YouTube
            logger.info("Step 4/4: Uploading to YouTube...")
            
            video_id = self.uploader.upload_video(
                final_video,
                title=title,
                description=f"Generated with free AI tools\n\nTopic: {topic}",
                tags=tags,
                privacy=privacy
            )
            
            if video_id:
                logger.info(f"✅ COMPLETE SUCCESS! Video: {video_id}")
                return True
            else:
                logger.error("YouTube upload failed")
                return False
        
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return False

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # You need to set these
    GEMINI_API_KEY = "your-free-gemini-api-key"  # Get from https://ai.google.dev
    
    # Check if we have requirements
    if not HAS_DIFFUSERS:
        print("⚠️  Installing required packages...")
        os.system("pip install diffusers transformers accelerate imageio imageio-ffmpeg")
    
    # Create pipeline
    pipeline = FreeVideoAutomationPipeline(GEMINI_API_KEY)
    
    # Generate and upload
    success = pipeline.generate_and_upload(
        topic="The Future of AI",
        script="AI is transforming the world in incredible ways...",
        title="The Future of AI - Explained",
        tags=["AI", "Technology", "Future", "Explained"],
        privacy="unlisted"  # Use "unlisted" for testing
    )
    
    print("✅ Pipeline completed!" if success else "❌ Pipeline failed")
