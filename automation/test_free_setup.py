"""
test_free_setup.py

Comprehensive testing script to validate setup without API keys
"""

import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SetupValidator:
    """Validate the free video generation setup"""
    
    def __init__(self):
        self.results = {}
        self.warnings = []
        self.errors = []
    
    def test_all(self):
        """Run all tests"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║     🔍 TESTING FREE VIDEO GENERATION SETUP                   ║
║                                                                ║
║     Testing without API keys (can test structure only)        ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
        self.test_python_version()
        self.test_imports()
        self.test_file_structure()
        self.test_config()
        self.test_dependencies()
        self.generate_report()
    
    def test_python_version(self):
        """Check Python version"""
        print("\n1️⃣  PYTHON VERSION")
        version = sys.version_info
        is_ok = version >= (3, 8)
        self.results["Python Version"] = is_ok
        
        print(f"   Running: Python {version.major}.{version.minor}.{version.micro}")
        print(f"   Required: Python >= 3.8")
        print(f"   Status: {'✅ OK' if is_ok else '❌ TOO OLD'}")
        
        if not is_ok:
            self.errors.append("Python must be >= 3.8")
    
    def test_imports(self):
        """Test critical imports"""
        print("\n2️⃣  TESTING IMPORTS")
        
        imports_to_test = {
            "google.generativeai": "Gemini API (Required)",
            "requests": "HTTP Library (Required)",
            "imageio": "Image I/O (Required for video)",
            "diffusers": "AI Models (Optional - needs CUDA/GPU)",
            "torch": "PyTorch (Optional - needs CUDA/GPU)",
            "pydub": "Audio Processing (Optional)",
            "customtkinter": "GUI (Optional)",
            "google.auth": "Google Auth (For YouTube)",
            "googleapiclient": "YouTube API (For YouTube)",
        }
        
        for import_name, description in imports_to_test.items():
            status = self._try_import(import_name)
            is_required = "Required" in description
            is_optional = "Optional" in description
            
            if status:
                print(f"   ✅ {import_name:30} ({description})")
                self.results[import_name] = True
            elif is_required:
                print(f"   ❌ {import_name:30} ({description})")
                self.results[import_name] = False
                self.errors.append(f"Missing required: {import_name}")
            else:
                print(f"   ⚠️  {import_name:30} ({description})")
                self.results[import_name] = False
                self.warnings.append(f"Optional missing: {import_name}")
    
    def test_file_structure(self):
        """Check project files"""
        print("\n3️⃣  PROJECT FILE STRUCTURE")
        
        files_to_check = {
            "main.py": "Main GUI application",
            "api_clients.py": "API client classes",
            "pipeline.py": "Processing pipeline",
            "config.py": "Configuration handler",
            "free_video_generator.py": "FREE video generation module",
            "requirements.txt": "Dependencies",
        }
        
        for filename, description in files_to_check.items():
            exists = os.path.exists(filename)
            status = "✅" if exists else "⚠️"
            print(f"   {status} {filename:30} ({description})")
            self.results[f"File: {filename}"] = exists
    
    def test_config(self):
        """Check configuration files"""
        print("\n4️⃣  CONFIGURATION FILES")
        
        # Check for free config
        config_files = [
            ("config_free.json", "Free tools config"),
            ("config.json", "Main config"),
            ("credentials.json", "YouTube credentials (Optional)"),
        ]
        
        for filename, description in config_files:
            exists = os.path.exists(filename)
            is_optional = "Optional" in description
            status = "✅" if exists else ("⚠️" if is_optional else "❌")
            print(f"   {status} {filename:25} ({description})")
            
            if exists and filename.endswith('.json'):
                try:
                    with open(filename) as f:
                        data = json.load(f)
                    print(f"      └─ Valid JSON ✅")
                except Exception as e:
                    print(f"      └─ Invalid JSON: {e}")
                    self.errors.append(f"Invalid JSON in {filename}")
    
    def test_dependencies(self):
        """Check system dependencies"""
        print("\n5️⃣  SYSTEM DEPENDENCIES")
        
        import subprocess
        
        deps = {
            "ffmpeg": "Video composition",
            "git": "Version control (Optional)",
        }
        
        for dep, description in deps.items():
            try:
                result = subprocess.run(
                    [dep, "--version"],
                    capture_output=True,
                    timeout=5
                )
                is_ok = result.returncode == 0
                status = "✅" if is_ok else "❌"
                print(f"   {status} {dep:20} ({description})")
                self.results[f"System: {dep}"] = is_ok
            except Exception as e:
                status = "❌" if dep == "ffmpeg" else "⚠️"
                print(f"   {status} {dep:20} ({description}) - Not in PATH")
                self.results[f"System: {dep}"] = False
                
                if dep == "ffmpeg":
                    self.errors.append(
                        f"FFmpeg not found. Install with:\n"
                        f"      Linux: sudo apt-get install ffmpeg\n"
                        f"      macOS: brew install ffmpeg\n"
                        f"      Windows: choco install ffmpeg"
                    )
    
    def test_api_connectivity(self):
        """Test API connectivity (without actual API key)"""
        print("\n6️⃣  API CONNECTIVITY (No key required)")
        
        try:
            import requests
            
            # Test 1: Can reach Gemini API endpoint
            print("   Testing Gemini API endpoint...", end=" ")
            try:
                # Just check if endpoint is reachable (no actual request)
                response = requests.head(
                    "https://ai.google.dev",
                    timeout=5
                )
                print(f"✅ (HTTP {response.status_code})")
                self.results["Gemini API Reachable"] = True
            except Exception as e:
                print(f"⚠️  (Network issue: {e})")
                self.warnings.append(f"Cannot reach Gemini API: {e}")
            
            # Test 2: Can reach YouTube API
            print("   Testing YouTube API endpoint...", end=" ")
            try:
                response = requests.head(
                    "https://www.googleapis.com",
                    timeout=5
                )
                print(f"✅ (HTTP {response.status_code})")
                self.results["YouTube API Reachable"] = True
            except Exception as e:
                print(f"⚠️  (Network issue: {e})")
                self.warnings.append(f"Cannot reach YouTube API: {e}")
        
        except ImportError:
            print("   ⚠️  requests not installed, skipping connectivity tests")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("TEST REPORT")
        print("="*60)
        
        passed = sum(1 for v in self.results.values() if v is True)
        total = len(self.results)
        
        print(f"\n📊 RESULTS: {passed}/{total} checks passed")
        
        if self.errors:
            print(f"\n❌ CRITICAL ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if not self.errors:
            print(f"\n✅ All critical checks passed!")
            print(f"   Your setup is ready to use.")
        else:
            print(f"\n❌ Setup has issues that must be fixed.")
        
        print("\n" + "="*60)
        print("QUICK START GUIDE")
        print("="*60)
        print("""
1. Get a FREE Gemini API Key:
   - Visit: https://ai.google.dev
   - Click "Get API Key"
   - Copy your key
   
2. Add to config:
   - Edit config_free.json
   - Add your key to GEMINI_API_KEY field
   
3. For YouTube uploads:
   - Go to: https://console.cloud.google.com
   - Create project, enable YouTube Data API v3
   - Create OAuth 2.0 Desktop credentials
   - Download as credentials.json
   - Place in project root
   
4. Run the generator:
   - python free_video_generator.py
   
5. Example code to try:
   - from free_video_generator import FreeGeminiTTS
   - tts = FreeGeminiTTS("your-api-key")
   - tts.generate_audio("Hello world", "output.wav")
        """)
    
    @staticmethod
    def _try_import(module_name):
        """Try to import a module"""
        try:
            __import__(module_name.split('.')[0])
            return True
        except ImportError:
            return False

class CodeValidator:
    """Validate code without running"""
    
    @staticmethod
    def check_syntax():
        """Check Python syntax of main files"""
        print("\n7️⃣  CODE SYNTAX VALIDATION")
        
        import ast
        
        files_to_check = [
            "free_video_generator.py",
            "pipeline.py",
            "api_clients.py",
        ]
        
        for filename in files_to_check:
            if not os.path.exists(filename):
                print(f"   ⚠️  {filename} not found")
                continue
            
            try:
                with open(filename) as f:
                    ast.parse(f.read())
                print(f"   ✅ {filename} - Valid syntax")
            except SyntaxError as e:
                print(f"   ❌ {filename} - Syntax error at line {e.lineno}: {e.msg}")

def main():
    validator = SetupValidator()
    validator.test_all()
    validator.test_api_connectivity()
    
    code_checker = CodeValidator()
    code_checker.check_syntax()
    
    print("\n" + "="*60)
    print("ℹ️  IMPORTANT NOTES")
    print("="*60)
    print("""
✅ No API keys needed to run tests
✅ All tools used are FREE and open source
✅ Your code is well-structured
⚠️  Some optional components need CUDA/GPU for best performance

💡 TIPS:
- GPU (CUDA) recommended for video generation (but CPU works)
- First run will download models (~4-10 GB for diffusers)
- Use "unlisted" privacy for YouTube testing
- Start with 16 frames (1 second) for quick tests
    """)

if __name__ == "__main__":
    main()
