"""
setup_free_tools.py

Setup script to install all FREE tools and validate configuration
"""

import os
import sys
import json
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# STEP 1: VALIDATE SYSTEM REQUIREMENTS
# ============================================================================

def check_system_requirements():
    """Check if system has required tools"""
    logger.info("=" * 60)
    logger.info("CHECKING SYSTEM REQUIREMENTS")
    logger.info("=" * 60)
    
    requirements = {
        "Python": check_python(),
        "pip": check_pip(),
        "FFmpeg": check_ffmpeg(),
        "Git": check_git()
    }
    
    print("\n📋 SYSTEM STATUS:")
    for tool, status in requirements.items():
        symbol = "✅" if status else "⚠️"
        print(f"{symbol} {tool}: {'OK' if status else 'MISSING'}")
    
    if not requirements["FFmpeg"]:
        print("\n⚠️  FFmpeg not found. Install with:")
        if sys.platform == "darwin":  # macOS
            print("   brew install ffmpeg")
        elif sys.platform == "linux":
            print("   sudo apt-get install ffmpeg")
        elif sys.platform == "win32":  # Windows
            print("   choco install ffmpeg")
    
    return all(requirements.values())

def check_python():
    return sys.version_info >= (3, 8)

def check_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False

def check_git():
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except:
        return False

# ============================================================================
# STEP 2: INSTALL PYTHON PACKAGES
# ============================================================================

def install_packages():
    """Install all required Python packages"""
    logger.info("\n" + "=" * 60)
    logger.info("INSTALLING PYTHON PACKAGES")
    logger.info("=" * 60)
    
    packages = {
        "Core": [
            "google-generativeai",
            "google-auth-oauthlib",
            "google-api-python-client",
            "requests",
        ],
        "Video Processing": [
            "imageio",
            "imageio-ffmpeg",
            "pydub",
        ],
        "AI Models (Optional - download on demand)": [
            "diffusers",
            "transformers",
            "torch",
            "accelerate",
        ],
        "Audio": [
            "openai-whisper",
            "pysubs2",
        ],
        "GUI (Optional)": [
            "customtkinter",
        ]
    }
    
    total_packages = sum(len(v) for v in packages.values())
    installed = 0
    
    for category, pkg_list in packages.items():
        print(f"\n📦 {category}:")
        for package in pkg_list:
            print(f"   Installing {package}...", end=" ")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", package],
                    timeout=300,
                    capture_output=True
                )
                print("✅")
                installed += 1
            except Exception as e:
                print(f"⚠️  ({str(e)[:30]}...)")
    
    logger.info(f"\n✅ Installed {installed}/{total_packages} packages")
    return installed > 0

# ============================================================================
# STEP 3: SETUP CONFIGURATION
# ============================================================================

def setup_config():
    """Setup configuration file"""
    logger.info("\n" + "=" * 60)
    logger.info("SETTING UP CONFIGURATION")
    logger.info("=" * 60)
    
    config = {
        "GEMINI_API_KEY": "",
        "YOUTUBE_UPLOAD_ENABLED": True,
        "VIDEO_ENGINE": "HuggingFace",  # Free option
        "TTS_ENGINE": "Gemini",  # Free option
        "OUTPUT_DIR": "output",
        "FFMPEG_PATH": "ffmpeg",  # Assume in PATH
    }
    
    print("\n🔧 CONFIGURATION SETUP:")
    
    # Get Gemini API key
    print("\n1️⃣  GEMINI API KEY (FREE)")
    print("   - Go to: https://ai.google.dev")
    print("   - Click 'Get API Key'")
    print("   - Create new API key")
    api_key = input("   Enter your Gemini API Key (or press Enter to skip): ").strip()
    if api_key:
        config["GEMINI_API_KEY"] = api_key
        print("   ✅ Saved")
    else:
        print("   ⚠️  Skipped (required for TTS)")
    
    # YouTube setup
    print("\n2️⃣  YOUTUBE UPLOAD (Optional)")
    print("   - Go to: https://console.cloud.google.com")
    print("   - Create project, enable YouTube Data API v3")
    print("   - Create OAuth 2.0 credentials (Desktop app)")
    print("   - Download as credentials.json")
    print("   - Place in project root")
    has_youtube = os.path.exists("credentials.json")
    print(f"   {'✅ Found credentials.json' if has_youtube else '⚠️  Not found'}")
    
    # Save config
    with open("config_free.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to config_free.json")
    return config

# ============================================================================
# STEP 4: VALIDATE SETUP
# ============================================================================

def validate_setup():
    """Validate everything is working"""
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATING SETUP")
    logger.info("=" * 60)
    
    checks = {
        "config_free.json exists": os.path.exists("config_free.json"),
        "google-generativeai installed": check_package("google.generativeai"),
        "imageio installed": check_package("imageio"),
        "FFmpeg available": check_ffmpeg(),
    }
    
    print("\n✔️  VALIDATION RESULTS:")
    passed = 0
    for check, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check}")
        if status:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(checks)}")
    return passed == len(checks)

def check_package(package_name):
    """Check if Python package is installed"""
    try:
        __import__(package_name.split('.')[0])
        return True
    except ImportError:
        return False

# ============================================================================
# STEP 5: QUICK TEST
# ============================================================================

def quick_test():
    """Run a quick test"""
    logger.info("\n" + "=" * 60)
    logger.info("QUICK FUNCTIONALITY TEST")
    logger.info("=" * 60)
    
    print("\n🧪 Testing imports...")
    
    # Test 1: Gemini API
    print("   Testing Gemini API...", end=" ")
    try:
        import google.generativeai as genai
        config = json.load(open("config_free.json"))
        if config.get("GEMINI_API_KEY"):
            genai.configure(api_key=config["GEMINI_API_KEY"])
            print("✅")
        else:
            print("⚠️  (no API key)")
    except Exception as e:
        print(f"❌ ({e})")
    
    # Test 2: FFmpeg
    print("   Testing FFmpeg...", end=" ")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅")
    except:
        print("❌")
    
    # Test 3: Image I/O
    print("   Testing imageio...", end=" ")
    try:
        import imageio
        print("✅")
    except:
        print("❌")
    
    print("\n✅ Quick test completed")

# ============================================================================
# MAIN SETUP FLOW
# ============================================================================

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║        🎬 FREE AI VIDEO GENERATION SETUP                      ║
║                                                                ║
║  This script will:                                            ║
║  ✓ Check system requirements                                 ║
║  ✓ Install FREE Python packages                              ║
║  ✓ Setup configuration                                       ║
║  ✓ Validate installation                                     ║
║  ✓ Run quick tests                                           ║
║                                                                ║
║  Total Cost: $0 (all free tools)                            ║
║  Time: ~10-15 minutes                                        ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Step 1: Check requirements
        if not check_system_requirements():
            print("\n⚠️  Some system requirements missing. Install FFmpeg and try again.")
        
        # Step 2: Install packages
        input("\n\n📦 Press Enter to install Python packages...")
        install_packages()
        
        # Step 3: Setup config
        input("\n\n🔧 Press Enter to setup configuration...")
        setup_config()
        
        # Step 4: Validate
        input("\n\n✔️  Press Enter to validate setup...")
        if validate_setup():
            print("\n🎉 Setup successful!")
        else:
            print("\n⚠️  Some checks failed. Review above and fix issues.")
        
        # Step 5: Quick test
        input("\n\n🧪 Press Enter to run quick tests...")
        quick_test()
        
        print("""
        
╔════════════════════════════════════════════════════════════════╗
║                 ✅ SETUP COMPLETE!                            ║
║                                                                ║
║  Next Steps:                                                  ║
║  1. Review config_free.json                                  ║
║  2. Set GEMINI_API_KEY if not done yet                       ║
║  3. Run: python free_video_generator.py                      ║
║                                                                ║
║  For YouTube uploads:                                         ║
║  - Download credentials.json from Google Cloud Console       ║
║  - Place in project root                                     ║
║  - Generator will prompt for auth on first upload            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
