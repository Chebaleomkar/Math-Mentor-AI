import os
from PIL import Image, ImageDraw, ImageFont
import wave
import struct
import math

# Create test data directory
os.makedirs("test_data", exist_ok=True)

# 1. Create a dummy test image with some math text
img = Image.new('RGB', (200, 100), color = 'white')
d = ImageDraw.Draw(img)
d.text((10,10), "x^2 + y^2 = r^2", fill="black")
img.save('test_data/test_image.png')
print("Created test_data/test_image.png")

# 2. Create a dummy test wav file (a simple sine wave)
with wave.open('test_data/test_audio.wav', 'w') as f:
    f.setnchannels(1) # mono
    f.setsampwidth(2) # 2 bytes per sample
    f.setframerate(16000) # 16kHz
    
    # generate a sine wave
    for i in range(16000 * 2): # 2 seconds
        value = int(32767.0*math.cos(16000.0*math.pi*float(i)/float(16000.0)))
        data = struct.pack('<h', value)
        f.writeframesraw(data)
print("Created test_data/test_audio.wav")
