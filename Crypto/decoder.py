import sys
from PIL import Image

# Define a type shortcut
pixel = tuple[int, int, int, int]

# Check for correct number of args
if len(sys.argv) != 2: raise Exception("Invalid number of arguments")

with Image.open(sys.argv[1]).convert('RGBA') as inImg:
    if inImg.width % 2 == 1 or inImg.height % 2 == 1:
        raise ValueError("Input image is of invalid size")

    outImg = Image.new('RGBA', (inImg.width // 2, inImg.height // 2))
    
    for i in range(outImg.width * outImg.height):
        x, y = i % outImg.width, i // outImg.height

        val = [0, 0, 0, 0]
        for j in range(4):
            px1: pixel = inImg.getpixel((x * 2 + 0, y * 2 + 0)) # type: ignore
            px2: pixel = inImg.getpixel((x * 2 + 1, y * 2 + 0)) # type: ignore
            px3: pixel = inImg.getpixel((x * 2 + 0, y * 2 + 1)) # type: ignore
            px4: pixel = inImg.getpixel((x * 2 + 1, y * 2 + 1)) # type: ignore

            val[j] |= (px1[j] & 0b00000011 ) << 6
            val[j] |= (px2[j] & 0b00000011 ) << 4
            val[j] |= (px3[j] & 0b00000011 ) << 2
            val[j] |= (px4[j] & 0b00000011 ) << 0
        
        val = tuple(val)

        outImg.putpixel((x, y), val)
    
    outImg.save('Crypto/out2.png')