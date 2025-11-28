from PIL import Image
import struct
import os

class ImageProcessor:
    @staticmethod
    def convert_to_rgb565(image_path):
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize((32, 32), Image.Resampling.LANCZOS)
            
            pixels = list(img.getdata())
            output = bytearray()
            
            for r, g, b in pixels:
                r5 = (r >> 3) & 0x1F
                g6 = (g >> 2) & 0x3F
                b5 = (b >> 3) & 0x1F
                
                rgb565 = (r5 << 11) | (g6 << 5) | b5
                
                output.extend(struct.pack('>H', rgb565))
                
            return bytes(output)
        except Exception as e:
            print(f"Image conversion error: {e}")
            return None
