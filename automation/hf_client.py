"""
hf_client.py

Provides a simple Hugging Face client for text->video using the
Hugging Face Inference API (free tier) with a local diffusers fallback.

Usage:
    from hf_client import HuggingFaceClient
    client = HuggingFaceClient(api_key=None)  # reads HF_API_KEY env var
    client.text_to_video(prompt, out_path)
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "damo-vilab/text-to-video-ms-1.7b"):
        self.api_key = api_key or os.getenv("HF_API_KEY", "")
        self.model = model

    def _call_inference_api(self, prompt: str, timeout: int = 300) -> Optional[bytes]:
        if not self.api_key:
            logger.info("HF_API_KEY not set; skipping Inference API call.")
            return None
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}
        try:
            logger.info(f"Calling Hugging Face Inference API for model {self.model}")
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp.content
            else:
                logger.error(f"HF Inference API error {resp.status_code}: {resp.text}")
                return None
        except Exception as e:
            logger.error(f"HF Inference API request failed: {e}")
            return None

    def _local_generate(self, prompt: str, out_path: str, num_frames: int = 16, height: int = 320, width: int = 576, steps: int = 20) -> bool:
        try:
            import torch
            from diffusers import DiffusionPipeline
            from PIL import Image
            logger.info("Using local diffusers pipeline as fallback (this will download model weights).")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            pipe = DiffusionPipeline.from_pretrained(self.model, torch_dtype=torch.float16 if device=="cuda" else torch.float32)
            pipe = pipe.to(device)
            # Not all TF models expose a .frames interface; attempt a simple call
            logger.info("Generating frames (local)...")
            out = pipe(prompt=prompt, num_frames=num_frames, height=height, width=width, num_inference_steps=steps)
            frames = getattr(out, "frames", None) or out.get("frames") if isinstance(out, dict) else None
            if not frames:
                logger.error("Local model did not return frames. Aborting local generation.")
                return False
            # Save frames to temp video using ffmpeg (via image files)
            import cv2
            import numpy as np
            tmp_images = []
            for i, f in enumerate(frames):
                if isinstance(f, Image.Image):
                    arr = np.array(f.convert("RGB"))
                else:
                    arr = np.array(f)
                tmp_images.append(arr)
            height, width = tmp_images[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            outv = cv2.VideoWriter(out_path, fourcc, 12, (width, height))
            for fr in tmp_images:
                outv.write(cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
            outv.release()
            logger.info(f"Saved local-generated video to {out_path}")
            return True
        except ImportError as e:
            logger.error(f"Missing local dependencies for diffusers fallback: {e}")
            return False
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            return False

    def text_to_video(self, prompt: str, out_path: str, resolution: str = "832*480") -> bool:
        """
        Generate a video for the given prompt and save to out_path.
        Tries HF Inference API first (if `HF_API_KEY` is set), otherwise falls back to local diffusers.
        """
        # Try Inference API
        content = self._call_inference_api(prompt)
        if content:
            try:
                with open(out_path, "wb") as f:
                    f.write(content)
                logger.info(f"Saved HF Inference API video to {out_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to write HF API response to file: {e}")

        # Fallback: local generation
        # Parse resolution
        try:
            if "*" in resolution:
                w, h = resolution.split("*")
                width, height = int(w), int(h)
            else:
                parts = resolution.split("x")
                width, height = int(parts[0]), int(parts[1])
        except Exception:
            width, height = 576, 320

        return self._local_generate(prompt, out_path, num_frames=16, height=height, width=width, steps=20)
