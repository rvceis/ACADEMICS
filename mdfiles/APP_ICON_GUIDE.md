# App Icon Setup Guide

## Icon Created ✓

I've created a solar-themed app icon SVG at:
`frontend/assets/solar-icon.svg`

**Design:**
- Blue gradient background (sky theme)
- Golden sun with rays
- 6 solar panels in grid layout
- Lightning bolt (energy flow indicator)

## Convert SVG to PNG (Choose One Method)

### Method 1: Online Converter (Easiest)
1. Go to: https://svgtopng.com/ or https://cloudconvert.com/svg-to-png
2. Upload: `frontend/assets/solar-icon.svg`
3. Convert to PNG at these sizes:
   - **icon.png**: 1024x1024
   - **adaptive-icon.png**: 1024x1024
   - **splash-icon.png**: 1024x1024
   - **favicon.png**: 48x48
4. Download and replace files in `frontend/assets/`

### Method 2: Use GIMP (Free Desktop App)
1. Install GIMP: `sudo apt install gimp`
2. Open solar-icon.svg in GIMP
3. Export as PNG at required sizes
4. Save to assets folder

### Method 3: Use Inkscape (Command Line)
```bash
# Install inkscape
sudo apt install inkscape

# Convert to all sizes
cd frontend/assets
inkscape solar-icon.svg --export-filename=icon.png --export-width=1024 --export-height=1024
inkscape solar-icon.svg --export-filename=adaptive-icon.png --export-width=1024 --export-height=1024
inkscape solar-icon.svg --export-filename=splash-icon.png --export-width=1024 --export-height=1024
inkscape solar-icon.svg --export-filename=favicon.png --export-width=48 --export-height=48
```

### Method 4: ImageMagick (Command Line)
```bash
# Install ImageMagick
sudo apt install imagemagick

# Convert
cd frontend/assets
convert solar-icon.svg -resize 1024x1024 icon.png
convert solar-icon.svg -resize 1024x1024 adaptive-icon.png
convert solar-icon.svg -resize 1024x1024 splash-icon.png
convert solar-icon.svg -resize 48x48 favicon.png
```

## Quick Inkscape Installation & Conversion

Run these commands:

```bash
# Install inkscape (one-time)
sudo apt install -y inkscape

# Convert all icons
cd /home/akash/Desktop/SOlar_Sharing/frontend/assets
inkscape solar-icon.svg --export-filename=icon.png --export-width=1024 --export-height=1024
inkscape solar-icon.svg --export-filename=adaptive-icon.png --export-width=1024 --export-height=1024
inkscape solar-icon.svg --export-filename=splash-icon.png --export-width=1024 --export-height=1024
inkscape solar-icon.svg --export-filename=favicon.png --export-width=48 --export-height=48

# Verify
ls -lh *.png
```

## Or Skip PNG - Use SVG Directly (Alternative)

Expo also supports SVG icons with `react-native-svg`:

1. Install package:
   ```bash
   cd frontend
   npm install react-native-svg
   ```

2. Update app.json:
   ```json
   "icon": "./assets/solar-icon.svg"
   ```

## Current Status

✅ SVG icon created: `solar-icon.svg`
⏳ PNG conversion needed (use one of the methods above)
✅ ML endpoints added to config
✅ Ready to rebuild APK after icon conversion

## After Converting Icons

Just rebuild the APK:
```bash
cd frontend
npm run build:android:preview
```

The new icon will appear on your phone!
