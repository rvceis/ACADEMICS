#!/usr/bin/env python3
"""
test_huggingface_setup.py

Test if Hugging Face video generation setup works
NO API KEYS REQUIRED - Tests local models
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60)
    
    required = {
        'torch': 'PyTorch (GPU acceleration)',
        'diffusers': 'Hugging Face Diffusers',
        'transformers': 'Transformers library',
        'cv2': 'OpenCV (video saving)',
        'PIL': 'Pillow (image handling)',
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"✓ {package:<15} ({description})")
        except ImportError:
            print(f"✗ {package:<15} ({description}) - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:\n  pip install {' '.join(missing)}")
        return False
    
    print("\n✓ All dependencies installed!")
    return True


def check_storage():
    """Check if there's enough storage for models"""
    print("\n" + "="*60)
    print("CHECKING STORAGE")
    print("="*60)
    
    try:
        import shutil
        stat = shutil.disk_usage("/")
        
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
        
        print(f"Total: {total_gb:.1f} GB")
        print(f"Free:  {free_gb:.1f} GB")
        
        if free_gb < 15:
            print(f"\n⚠️  WARNING: Models need ~10GB. You have {free_gb:.1f}GB free")
            return False
        
        print(f"\n✓ Sufficient storage ({free_gb:.1f}GB free)")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not check storage: {e}")
        return True


def check_gpu():
    """Check if GPU is available"""
    print("\n" + "="*60)
    print("CHECKING GPU")
    print("="*60)
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✓ CUDA Available")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
            return True
        else:
            print("⚠️  No GPU detected (will use CPU - slower)")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check GPU: {e}")
        return False


def test_model_download():
    """Test if we can download a small model"""
    print("\n" + "="*60)
    print("TESTING MODEL DOWNLOAD")
    print("="*60)
    
    try:
        from diffusers import DiffusionPipeline
        import torch
        
        print("Attempting to download small test model...")
        print("This might take a few minutes on first run...")
        
        # Use the smallest model for testing
        model_id = "cerspense/zeroscope_v2_576w"
        print(f"Model: {model_id}")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # This will download the model
        pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        
        print(f"✓ Model downloaded successfully!")
        print(f"  Device: {device}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Check internet connection")
        print(f"  - Check storage space (need ~10GB)")
        print(f"  - Try again later (HF servers might be busy)")
        return False


def test_video_generation():
    """Test actual video generation (quick test)"""
    print("\n" + "="*60)
    print("TESTING VIDEO GENERATION")
    print("="*60)
    
    try:
        from huggingface_video_gen import HuggingFaceVideoGenerator
        
        print("Generating test video (8 frames, low resolution)...")
        print("This will take 30s-5min depending on your hardware...")
        
        gen = HuggingFaceVideoGenerator()
        
        frames = gen.generate_video(
            prompt="A simple scene",
            num_frames=8,  # Very small for testing
            height=320,
            width=576,
            num_inference_steps=20  # Low quality for speed
        )
        
        if frames:
            print(f"✓ Generated {len(frames)} frames")
            
            # Try saving
            if gen.save_video(frames, "test_video.mp4", fps=12):
                print("✓ Video saved successfully!")
                
                # Check file size
                size_mb = os.path.getsize("test_video.mp4") / (1024*1024)
                print(f"  File size: {size_mb:.1f}MB")
                
                # Clean up
                os.remove("test_video.mp4")
                print("✓ Test complete!")
                return True
        
        print("❌ Video generation failed")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_youtube_setup():
    """Check if YouTube credentials are configured"""
    print("\n" + "="*60)
    print("CHECKING YOUTUBE SETUP")
    print("="*60)
    
    if os.path.exists("credentials.json"):
        print("✓ credentials.json found")
        return True
    else:
        print("⚠️  credentials.json not found")
        print("\nTo set up YouTube uploads:")
        print("  1. Go to: https://console.cloud.google.com/")
        print("  2. Create a project")
        print("  3. Enable YouTube Data API v3")
        print("  4. Create OAuth 2.0 credentials (Desktop)")
        print("  5. Download as credentials.json")
        print("  6. Place credentials.json in this directory")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" HUGGING FACE VIDEO GENERATION SETUP TEST")
    print(" (NO API KEYS REQUIRED)")
    print("="*70)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Storage", check_storage),
        ("GPU", check_gpu),
        ("Model Download", test_model_download),
        ("YouTube Setup", check_youtube_setup),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<25} {status}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    # Recommendations
    print("\n" + "="*70)
    print(" RECOMMENDATIONS")
    print("="*70)
    
    if results.get("Dependencies"):
        print("✓ Ready to generate videos!")
        print("\nQuick start:")
        print("  python huggingface_video_gen.py")
    else:
        print("❌ Please fix missing dependencies first")
    
    if not results.get("GPU"):
        print("\n⚠️  GPU not detected - videos will be slower")
        print("   Recommendation: Use smaller model or fewer frames")
    
    if not results.get("YouTube Setup"):
        print("\n⚠️  YouTube not configured yet")
        print("   Optional: Set up if you want to auto-upload")
    
    print("\n" + "="*70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
