"""
huggingface_video_gen.py

FREE Hugging Face video generation without API keys
Uses local models or free inference API
"""

import os
import torch
import logging
from pathlib import Path
from typing import Optional
import json

logger = logging.getLogger(__name__)

# ============================================================================
# FREE HUGGING FACE VIDEO GENERATION
# ============================================================================

class HuggingFaceVideoGenerator:
    """
    FREE video generation using Hugging Face models
    No API keys required! (Uses local models)
    """
    
    def __init__(self, model_name: str = "damo-vilab/text-to-video-ms-1.7b"):
        """
        Initialize with a FREE model from Hugging Face
        
        Available FREE models:
        - damo-vilab/text-to-video-ms-1.7b (✓ BEST for CPU)
        - cerspense/zeroscope_v2_576w (smaller, faster)
        - cerspense/zeroscope_v2_XL (higher quality)
        - stabilityai/stable-video-diffusion-img2vid (image to video)
        """
        self.model_name = model_name
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
    def initialize(self):
        """Load the model (happens on first use)"""
        if self.pipe is None:
            logger.info(f"Loading model: {self.model_name}")
            try:
                from diffusers import DiffusionPipeline
                
                # Download from Hugging Face (completely FREE)
                self.pipe = DiffusionPipeline.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None
                )
                self.pipe = self.pipe.to(self.device)
                logger.info("✓ Model loaded successfully")
                return True
            except ImportError:
                logger.error("Install: pip install diffusers torch transformers")
                return False
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                return False
    
    def generate_video(
        self,
        prompt: str,
        num_frames: int = 24,
        height: int = 320,
        width: int = 576,
        num_inference_steps: int = 30,
        guidance_scale: float = 9.0,
    ) -> Optional[list]:
        """
        Generate video frames from text
        
        Args:
            prompt: Text description (e.g., "A cat playing with a ball")
            num_frames: Number of frames (24 = 1 second at 24fps)
            height: Video height (lower = faster)
            width: Video width (lower = faster)
            num_inference_steps: Quality vs speed (higher = better but slower)
            guidance_scale: How closely to follow the prompt
            
        Returns:
            List of PIL images (video frames)
        """
        if not self.initialize():
            return None
        
        try:
            logger.info(f"Generating video: {prompt}")
            logger.info(f"Settings: {num_frames} frames, {width}x{height}, {num_inference_steps} steps")
            
            # Generate video frames
            with torch.no_grad():
                video_frames = self.pipe(
                    prompt=prompt,
                    num_frames=num_frames,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                ).frames
            
            logger.info(f"✓ Generated {len(video_frames)} frames")
            return video_frames
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return None
    
    def save_video(self, frames: list, output_path: str, fps: int = 12) -> bool:
        """
        Save frames as MP4 video
        
        Args:
            frames: List of PIL images
            output_path: Where to save the MP4
            fps: Frames per second
        """
        if not frames:
            logger.error("No frames to save")
            return False
        
        try:
            import cv2
            import numpy as np
            
            # Convert PIL images to numpy arrays
            frame_array = []
            for frame in frames:
                # Convert PIL to numpy
                frame_np = np.array(frame)
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                frame_array.append(frame_bgr)
            
            # Get video properties from first frame
            height, width = frame_array[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            for frame in frame_array:
                out.write(frame)
            
            out.release()
            logger.info(f"✓ Video saved: {output_path}")
            return True
            
        except ImportError:
            logger.error("Install opencv: pip install opencv-python")
            return False
        except Exception as e:
            logger.error(f"Failed to save video: {e}")
            return False


# ============================================================================
# ALTERNATIVE: FREE HUGGING FACE INFERENCE API (No download needed)
# ============================================================================

class HuggingFaceInferenceAPI:
    """
    FREE Hugging Face Inference API
    Up to 15 requests/minute (free tier)
    No model download needed!
    """
    
    def __init__(self):
        """
        Get FREE HF token from: https://huggingface.co/settings/tokens
        Create a READ token (completely free)
        """
        self.api_key = os.getenv("HF_API_KEY", "")
        if not self.api_key:
            logger.warning("HF_API_KEY not set. Set it: export HF_API_KEY=hf_xxxxx")
    
    def generate_video(self, prompt: str, model: str = "damo-vilab/text-to-video-ms-1.7b") -> Optional[bytes]:
        """
        Generate video using Hugging Face Inference API
        
        Models available:
        - damo-vilab/text-to-video-ms-1.7b (TEXT TO VIDEO)
        - cerspense/zeroscope_v2_576w (TEXT TO VIDEO - Faster)
        - ZeroScope/Zeroscope_v2_XL (TEXT TO VIDEO - Better quality)
        """
        try:
            import requests
            
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            logger.info(f"Calling HF API: {model}")
            response = requests.post(
                url,
                headers=headers,
                json={"inputs": prompt},
                timeout=300
            )
            
            if response.status_code == 200:
                logger.info("✓ Video generated via HF API")
                return response.content
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"HF API request failed: {e}")
            return None


# ============================================================================
# QUICK START EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: LOCAL model (NO API KEY needed, but needs GPU/CPU time)
    print("=" * 60)
    print("OPTION 1: Local Hugging Face Model (No API key needed)")
    print("=" * 60)
    
    gen = HuggingFaceVideoGenerator()
    
    # For testing without GPU, use smaller model:
    # gen.model_name = "cerspense/zeroscope_v2_576w"
    
    frames = gen.generate_video(
        prompt="A beautiful sunset over the ocean",
        num_frames=16,  # 16 frames = ~1.3 seconds at 12fps
        height=320,
        width=576,
        num_inference_steps=20  # Lower for faster generation
    )
    
    if frames:
        gen.save_video(frames, "output_video.mp4", fps=12)
    
    print("\n" + "=" * 60)
    print("OPTION 2: Free HF Inference API")
    print("=" * 60)
    
    # Get API key from: https://huggingface.co/settings/tokens
    hf_api = HuggingFaceInferenceAPI()
    video_bytes = hf_api.generate_video("A dog running in a park")
    
    if video_bytes:
        with open("api_output_video.mp4", "wb") as f:
            f.write(video_bytes)
        logger.info("✓ Saved API generated video")
