#!/usr/bin/env python3
"""
demo_free_video.py

Simple demo showing how to use the free video generation system
No API keys required to see what's possible!
"""

import json
import os
from pathlib import Path

def show_gemini_example():
    """Show Gemini API usage example"""
    print("\n" + "="*60)
    print("📝 EXAMPLE 1: Text Generation with Gemini (FREE)")
    print("="*60)
    
    code = '''
import google.generativeai as genai

# Load your FREE API key
api_key = "your-gemini-api-key"  # Get from ai.google.dev
genai.configure(api_key=api_key)

# Create model
model = genai.GenerativeModel("gemini-2.5-flash")

# Generate podcast script
response = model.generate_content(
    "Write a 2-minute podcast script about the future of AI"
)
print(response.text)
'''
    print(code)
    print("\n💡 This generates ~1000 words per request")
    print("⏱️  Takes ~5-10 seconds")
    print("💰 FREE - 60 requests per minute")

def show_tts_example():
    """Show TTS usage example"""
    print("\n" + "="*60)
    print("🎙️  EXAMPLE 2: Voice Generation with Gemini TTS (FREE)")
    print("="*60)
    
    code = '''
from free_video_generator import FreeGeminiTTS

# Create TTS engine
tts = FreeGeminiTTS(api_key="your-gemini-api-key")

# Generate voice
script = "Welcome to my AI-generated podcast!"
tts.generate_audio(
    text=script,
    output_path="podcast.wav",
    voice_name="Kore"  # Available voices: Kore, Puck, etc.
)

print("✅ Audio saved!")
'''
    print(code)
    print("\n💡 Available voices: Kore, Puck, Aoede, Chime, Fenrir, Gigasaurus")
    print("⏱️  Takes ~5-10 seconds for 1000 words")
    print("💰 FREE - included with Gemini API")

def show_video_example():
    """Show video generation example"""
    print("\n" + "="*60)
    print("🎬 EXAMPLE 3: Video from Text (FREE - Hugging Face)")
    print("="*60)
    
    code = '''
from free_video_generator import HuggingFaceVideoGenerator

# Create video generator
gen = HuggingFaceVideoGenerator()

# Generate video (runs completely locally!)
gen.generate_video(
    prompt="A professional video about artificial intelligence",
    output_path="ai_video.mp4",
    num_frames=16,      # 16 frames ≈ 1 second at 8fps
    height=320,
    width=576
)

print("✅ Video generated!")
'''
    print(code)
    print("\n💡 First run downloads model (~4-10 GB) - then cached")
    print("⏱️  Takes 2-5 minutes (GPU) or 10-15 (CPU)")
    print("💰 Completely FREE - runs locally")
    print("🔒 100% Private - nothing sent to servers")

def show_compose_example():
    """Show video composition example"""
    print("\n" + "="*60)
    print("🎞️  EXAMPLE 4: Combine Video + Audio (FREE - FFmpeg)")
    print("="*60)
    
    code = '''
from free_video_generator import FFmpegComposer

# Compose video and audio
composer = FFmpegComposer()
composer.combine_video_audio(
    video_path="ai_video.mp4",
    audio_path="podcast.wav",
    output_path="final_video.mp4"
)

print("✅ Final video ready!")
'''
    print(code)
    print("\n💡 Combines separate video and audio files")
    print("⏱️  Takes 30-60 seconds")
    print("💰 Completely FREE - open source tool")

def show_youtube_example():
    """Show YouTube upload example"""
    print("\n" + "="*60)
    print("📤 EXAMPLE 5: Upload to YouTube (FREE API)")
    print("="*60)
    
    code = '''
from free_video_generator import YouTubeUploader

# Create uploader
uploader = YouTubeUploader()

# Upload video
video_id = uploader.upload_video(
    file_path="final_video.mp4",
    title="My AI-Generated Video About AI",
    description="Generated with 100% free AI tools!",
    tags=["AI", "Technology", "Automation"],
    privacy="unlisted"  # Use "unlisted" for testing
)

# Video is now live!
print(f"🎉 Watch at: youtube.com/watch?v={video_id}")
'''
    print(code)
    print("\n💡 Requires credentials.json from Google Cloud Console")
    print("⏱️  Takes 2-10 minutes depending on file size")
    print("💰 Completely FREE - tier 1 API")

def show_complete_example():
    """Show complete pipeline example"""
    print("\n" + "="*60)
    print("⚡ EXAMPLE 6: Complete Pipeline (All Steps)")
    print("="*60)
    
    code = '''
from free_video_generator import FreeVideoAutomationPipeline
import json

# Load your config
config = json.load(open('config_free.json'))
api_key = config['GEMINI_API_KEY']

# Create pipeline
pipeline = FreeVideoAutomationPipeline(api_key)

# ONE LINE generates complete video!
pipeline.generate_and_upload(
    topic="The Future of AI",
    script="AI is transforming every industry...",
    title="The Future of AI - Explained",
    tags=["AI", "Future", "Technology"],
    privacy="unlisted"
)

print("✅ Complete video uploaded to YouTube!")
'''
    print(code)
    print("\n💡 Does everything in one call:")
    print("   1. Generates video from text")
    print("   2. Generates voice from script")
    print("   3. Combines video + audio")
    print("   4. Uploads to YouTube")
    print("⏱️  Takes ~20-30 minutes total")
    print("💰 Total cost: $0")

def show_setup_steps():
    """Show setup steps"""
    print("\n" + "="*60)
    print("🔧 SETUP STEPS (5 minutes)")
    print("="*60)
    
    print("""
STEP 1: Install Dependencies
$ python setup_free_tools.py

STEP 2: Get Gemini API Key (FREE)
- Go to: https://ai.google.dev
- Click: "Get API Key"
- Copy your key
- Add to config_free.json

STEP 3: (Optional) Setup YouTube
- Go to: https://console.cloud.google.com
- Create project
- Enable: YouTube Data API v3
- Create: OAuth 2.0 Desktop credentials
- Download: credentials.json
- Place in: project root

STEP 4: Test Everything
$ python test_free_setup.py

STEP 5: Run First Video
$ python free_video_generator.py
""")

def show_cost_breakdown():
    """Show cost breakdown"""
    print("\n" + "="*60)
    print("💰 COST BREAKDOWN (Monthly)")
    print("="*60)
    
    costs = {
        "Gemini API (60 req/min)": "$0",
        "Gemini TTS": "$0 (included)",
        "Hugging Face (local)": "$0",
        "FFmpeg": "$0",
        "YouTube Data API": "$0",
        "Total per month": "$0",
        "Videos you can make": "Unlimited*",
    }
    
    for item, cost in costs.items():
        print(f"  {item:.<40} {cost:>10}")
    
    print("""
* With free tier limits:
  - Gemini: 60 requests/minute (very generous)
  - YouTube: Usually 10+ uploads/day free
  - Storage: Depends on your system
""")

def show_features():
    """Show supported features"""
    print("\n" + "="*60)
    print("✨ SUPPORTED FEATURES")
    print("="*60)
    
    features = {
        "Text Generation": "✅ Gemini API",
        "Video Generation": "✅ Hugging Face Diffusers",
        "Voice Generation": "✅ Gemini TTS",
        "Video Composition": "✅ FFmpeg",
        "Audio Mixing": "✅ FFmpeg",
        "YouTube Upload": "✅ YouTube Data API v3",
        "Automatic Scheduling": "✅ Coming soon",
        "Social Media Share": "✅ Coming soon",
        "Analytics Integration": "✅ Coming soon",
    }
    
    for feature, status in features.items():
        print(f"  {feature:.<30} {status:>20}")

def show_available_voices():
    """Show available voices"""
    print("\n" + "="*60)
    print("🎙️  AVAILABLE VOICES (All FREE with Gemini)")
    print("="*60)
    
    voices = {
        "Kore": "Energetic, youthful, clear & bright",
        "Puck": "Confident, informal, trustworthy",
        "Aoede": "Clear, conversational, thoughtful",
        "Chime": "Warm, inviting, trustworthy",
        "Fenrir": "Deep, resonant, powerful",
        "Gigasaurus": "Fun, playful, energetic",
        "Asteria": "Sophisticated, professional",
        "Sage": "Wise, calm, measured",
    }
    
    for voice, description in voices.items():
        print(f"  • {voice:15} - {description}")

def main():
    """Main demo menu"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🎬 FREE AI VIDEO GENERATION - COMPLETE DEMO            ║
║                                                                ║
║              Transform Text into YouTube Videos!              ║
║                    100% FREE & Open Source                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Show all examples
    show_setup_steps()
    show_features()
    show_cost_breakdown()
    show_available_voices()
    show_gemini_example()
    show_tts_example()
    show_video_example()
    show_compose_example()
    show_youtube_example()
    show_complete_example()
    
    # Summary
    print("\n" + "="*60)
    print("🚀 READY TO START?")
    print("="*60)
    print("""
1. Run setup:
   $ python setup_free_tools.py

2. Get free API key:
   https://ai.google.dev

3. Test everything:
   $ python test_free_setup.py

4. Create your first video:
   $ python free_video_generator.py

5. Check the guide:
   - COMPLETE_GUIDE.md (full documentation)
   - FREE_RESOURCES_GUIDE.md (all available tools)

📚 Documentation: See COMPLETE_GUIDE.md
💬 Issues? See troubleshooting section in COMPLETE_GUIDE.md
🤝 Questions? Check test_free_setup.py for debugging

Happy video creation! 🎬
    """)

if __name__ == "__main__":
    main()
