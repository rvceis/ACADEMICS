"""
HUGGING FACE FREE INTEGRATION GUIDE
====================================

All completely FREE - No API keys required for local models!
"""

# ==============================================================================
# HOW TO USE HUGGING FACE - 3 OPTIONS
# ==============================================================================

"""
OPTION 1: LOCAL MODEL (RECOMMENDED FOR NO API KEY)
===================================================

✓ Completely FREE
✓ No API key needed
✓ Works offline
✗ Needs GPU (or slower on CPU)

Installation:
    pip install diffusers torch transformers pillow opencv-python

Code:
    from huggingface_video_gen import HuggingFaceVideoGenerator
    
    gen = HuggingFaceVideoGenerator()
    frames = gen.generate_video(
        "A cat playing with yarn",
        num_frames=24,
        height=480,
        width=768
    )
    gen.save_video(frames, "cat_video.mp4")
"""

"""
OPTION 2: FREE HUGGING FACE INFERENCE API
===========================================

✓ No model download (uses HF servers)
✓ FREE (limited to 15 requests/minute)
✗ Needs API token (free to get)
✗ Internet required
✗ Slower response time

Get FREE API token:
    1. Go to https://huggingface.co/settings/tokens
    2. Click "New token"
    3. Create a READ-only token (select "Read" permission)
    4. Copy the token

Setup:
    export HF_API_KEY="hf_xxxxxxxxxxxxx"

Code:
    from huggingface_video_gen import HuggingFaceInferenceAPI
    
    api = HuggingFaceInferenceAPI()
    video_bytes = api.generate_video("A dog running in park")
    with open("dog_video.mp4", "wb") as f:
        f.write(video_bytes)
"""

"""
OPTION 3: IMAGE TO VIDEO (Also FREE!)
======================================

✓ Convert still images to videos
✓ FREE models available
✓ No API key needed

Models:
    - stabilityai/stable-video-diffusion-img2vid-xt (Best quality)
    - stabilityai/stable-video-diffusion-img2vid (Faster)

This is PERFECT for:
    - Converting YouTube thumbnails to short videos
    - Adding motion to static images
    - Creating video montages
"""

# ==============================================================================
# YOUTUBE INTEGRATION
# ==============================================================================

"""
YOUTUBE UPLOAD (Also using FREE API!)
======================================

✓ YouTube Data API v3 is FREE
✓ 10,000 quota units per day (usually enough for 10-20 uploads)
✓ Free to set up

Setup:
    1. Go to https://console.cloud.google.com/
    2. Create new project
    3. Enable YouTube Data API v3
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download JSON file as credentials.json

Code to upload:
    from pipeline import YouTubeUploader
    
    uploader = YouTubeUploader(credentials_file="credentials.json")
    uploader.upload_video(
        video_path="cat_video.mp4",
        title="Amazing AI Cat Video",
        description="Generated with AI using Hugging Face",
        tags=["AI", "video", "cat"]
    )
"""

# ==============================================================================
# COMPLETE WORKFLOW (NO API KEYS!)
# ==============================================================================

"""
Step 1: Install dependencies
    pip install diffusers torch transformers pillow opencv-python google-auth-oauthlib google-auth-httplib2 google-api-python-client

Step 2: Generate video (LOCAL, no API key)
    from huggingface_video_gen import HuggingFaceVideoGenerator
    
    gen = HuggingFaceVideoGenerator()
    frames = gen.generate_video(
        "A beautiful landscape with mountains and river",
        num_frames=30,
        height=720,
        width=1280,
        num_inference_steps=50
    )
    gen.save_video(frames, "nature_video.mp4", fps=24)

Step 3: Upload to YouTube (using FREE credentials)
    # You'll do OAuth login once, then it saves the token
    from pipeline import YouTubeUploader
    
    uploader = YouTubeUploader(credentials_file="credentials.json")
    uploader.upload_video(
        video_path="nature_video.mp4",
        title="AI Generated Nature Video",
        description="Created using Hugging Face",
        tags=["nature", "AI", "video"]
    )
"""

# ==============================================================================
# FREE MODELS COMPARISON
# ==============================================================================

"""
Model Selection Guide:

BEST FOR CPU (Smallest/Fastest):
    - cerspense/zeroscope_v2_576w
    - Good quality, 576x320 resolution
    - ~2-3 minutes per video on CPU
    - Perfect for testing

BALANCED (Medium GPU/CPU):
    - damo-vilab/text-to-video-ms-1.7b ⭐ RECOMMENDED
    - Good quality, 576x320 resolution
    - ~30 seconds on GPU, ~3-5 minutes on CPU
    - Most reliable

HIGH QUALITY (GPU Recommended):
    - cerspense/zeroscope_v2_XL
    - Better quality, slower
    - Higher resolution possible
    - Needs good GPU

IMAGE TO VIDEO (Also great!):
    - stabilityai/stable-video-diffusion-img2vid
    - Turn any image into moving video
    - Quick and creative
"""

# ==============================================================================
# COST BREAKDOWN
# ==============================================================================

"""
Total Cost for this setup: $0 ✓

✓ Hugging Face local models: FREE
✓ Hugging Face Inference API: FREE (15 req/min)
✓ YouTube Data API: FREE (10K units/day)
✓ Google OAuth: FREE
✓ All libraries: Open source and FREE

No payment methods needed!
No credit cards required!
No hidden costs!
"""

# ==============================================================================
# TROUBLESHOOTING
# ==============================================================================

"""
Problem: "No space left on device"
Solution: Models are large (~5-10GB). Check storage with: df -h

Problem: "Out of memory" on GPU
Solution: Reduce num_frames, height, width, or use smaller model

Problem: "CUDA out of memory"
Solution: 
    1. Use CPU instead (slower but works)
    2. Use smaller model
    3. Reduce resolution

Problem: HF Inference API rate limited
Solution: Wait 1 minute or use local model instead

Problem: YouTube upload failed
Solution: Check if credentials.json exists and is valid
"""

# ==============================================================================
# NEXT STEPS
# ==============================================================================

"""
1. Install required packages
2. Get YouTube credentials (free, one-time setup)
3. Run huggingface_video_gen.py to test video generation
4. Run pipeline.py to upload to YouTube
5. Done! Completely free workflow!
"""
