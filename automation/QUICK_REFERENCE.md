# ⚡ QUICK REFERENCE CARD

## 🔥 TL;DR - Get Started in 5 Minutes

### **1. Run Setup (2 minutes)**
```bash
python setup_free_tools.py
```

### **2. Get API Key (1 minute)**
- Visit: https://ai.google.dev
- Click: Get API Key
- Copy & paste into setup

### **3. Try First Video (2 minutes)**
```bash
python -c "
from free_video_generator import FreeGeminiTTS
tts = FreeGeminiTTS('YOUR-API-KEY')
tts.generate_audio('Hello world', 'test.wav')
print('✅ Done!')
"
```

---

## 📊 Free Tier Limits

| Service | Free Tier | Cost if Exceeded |
|---------|-----------|-----------------|
| Gemini API | 60 req/min, unlimited/day | $0.075 per 1M tokens |
| YouTube API | Unlimited uploads | Same as Google Cloud |
| Video Models | Runs locally | N/A |
| Storage | Your system | N/A |

**Real-world**: ~2+ videos per day, completely free

---

## 🎬 Code Snippets (Copy-Paste Ready)

### **Generate Text Script**
```python
import google.generativeai as genai

genai.configure(api_key="YOUR-KEY")
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Write podcast script about AI")
print(response.text)
```

### **Generate Voice**
```python
from free_video_generator import FreeGeminiTTS

tts = FreeGeminiTTS("YOUR-KEY")
tts.generate_audio("Your text here", "output.wav", voice_name="Kore")
```

### **Generate Video**
```python
from free_video_generator import HuggingFaceVideoGenerator

gen = HuggingFaceVideoGenerator()
gen.generate_video("Video about AI", "video.mp4", num_frames=16)
```

### **Combine Video + Audio**
```python
from free_video_generator import FFmpegComposer

FFmpegComposer.combine_video_audio("video.mp4", "audio.wav", "final.mp4")
```

### **Upload to YouTube**
```python
from free_video_generator import YouTubeUploader

uploader = YouTubeUploader()
uploader.upload_video("final.mp4", "My Video Title", privacy="unlisted")
```

---

## 📁 Project Structure

```
/automation/
├── main.py                          # GUI (your original)
├── api_clients.py                   # API clients (updated)
├── pipeline.py                      # Processing pipeline (updated)
├── config.py                        # Config handler (original)
├── free_video_generator.py          # ⭐ NEW - All FREE tools
├── setup_free_tools.py              # ⭐ NEW - Automated setup
├── test_free_setup.py               # ⭐ NEW - Validation
├── demo_free_video.py               # ⭐ NEW - Examples
├── COMPLETE_GUIDE.md                # ⭐ NEW - Full docs
├── FREE_RESOURCES_GUIDE.md          # ⭐ NEW - All resources
├── QUICK_REFERENCE.md               # ⭐ This file
├── config_free.json                 # ⭐ NEW - Your config
├── credentials.json                 # ⭐ YouTube API (if needed)
└── requirements.txt                 # Dependencies
```

---

## 🆓 ALL FREE TOOLS USED

```
✅ Gemini 2.5 Flash      - Text generation (60 req/min free)
✅ Gemini TTS             - Voice generation (free tier)
✅ Hugging Face Diffusers - Video generation (local, free)
✅ FFmpeg                 - Video composition (open source)
✅ YouTube Data API v3    - Upload to YouTube (free tier)
✅ Python                 - Programming language (open source)
```

**Total Cost: $0/month**

---

## 🎯 Your First Video (Step-by-Step)

```
1. python setup_free_tools.py
   └─ Installs packages, asks for API key

2. Get API key from https://ai.google.dev
   └─ Takes 1 minute, completely free

3. python demo_free_video.py
   └─ Shows all examples

4. Run this:
   python free_video_generator.py
   └─ Creates sample video

5. Upload to YouTube:
   Edit the script at bottom of free_video_generator.py
   Update with your topic, script, title
   Run it!
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named 'diffusers'" | `pip install diffusers transformers` |
| "FFmpeg not found" | See COMPLETE_GUIDE.md for install instructions |
| "API key invalid" | Regenerate from ai.google.dev |
| "Rate limited" | Wait 1 minute, then retry |
| "CUDA out of memory" | Use CPU (slower) or reduce num_frames |

---

## 🔗 Important Links

```
Gemini API Key:        https://ai.google.dev
YouTube API Setup:     https://console.cloud.google.com
Hugging Face Models:   https://huggingface.co/models
FFmpeg Download:       https://ffmpeg.org/download.html
Python Download:       https://python.org
```

---

## 💡 Pro Tips

1. **First time slow?** Models download on first run (~10 min), then cached
2. **No GPU?** Code works on CPU, just slower (15-30 min per video)
3. **Want faster?** GPU (CUDA) makes it 5-10x faster
4. **Testing first?** Use `privacy="unlisted"` for YouTube
5. **Many videos?** Run setup once, use for unlimited videos

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] Setup script run successfully
- [ ] Gemini API key obtained
- [ ] Test script passed all checks
- [ ] Generated first audio (TTS)
- [ ] Generated first video (Diffusers)
- [ ] Composed video + audio
- [ ] (Optional) YouTube credentials setup
- [ ] Uploaded first video to YouTube

---

## 🚀 Next Steps

1. **Explore**: Run `python demo_free_video.py`
2. **Learn**: Read COMPLETE_GUIDE.md
3. **Create**: Modify free_video_generator.py with your content
4. **Share**: Upload to YouTube!

---

## 📞 Support

- **Documentation**: COMPLETE_GUIDE.md
- **All Tools**: FREE_RESOURCES_GUIDE.md
- **Examples**: demo_free_video.py
- **Testing**: test_free_setup.py
- **Troubleshooting**: COMPLETE_GUIDE.md (section at bottom)

---

**Status**: ✅ 100% Ready to Use
**Cost**: $0
**Setup Time**: ~15 minutes
**Time to First Video**: ~30 minutes

🎬 **Happy creating!**
