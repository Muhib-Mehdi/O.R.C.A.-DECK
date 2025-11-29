from PIL import Image

class ImageProcessor:
    @staticmethod
    def convert_to_rgb565(image_path):
        """Convert an image to RGB565 format for the display"""
        try:
            # Open and resize image to 32x32
            img = Image.open(image_path)
            img = img.resize((32, 32), Image.Resampling.LANCZOS)
            img = img.convert('RGB')
            
            # Convert to RGB565 format
            raw_data = bytearray()
            for y in range(32):
                for x in range(32):
                    r, g, b = img.getpixel((x, y))
                    
                    # Convert to RGB565
                    r5 = (r >> 3) & 0x1F
                    g6 = (g >> 2) & 0x3F
                    b5 = (b >> 3) & 0x1F
                    
                    # Combine into 16-bit value
                    rgb565 = (r5 << 11) | (g6 << 5) | b5
                    
                    # Store as big-endian (MSB first)
                    raw_data.append((rgb565 >> 8) & 0xFF)
                    raw_data.append(rgb565 & 0xFF)
            
            return raw_data
        except Exception as e:
            print(f"Error converting image: {e}")
            return None
