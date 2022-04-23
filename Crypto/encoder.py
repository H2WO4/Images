import sys
from PIL import Image

# Define a type shortcut
pixel = tuple[int, int, int, int]
pixelL = list[int]

# Check for correct number of args
if len(sys.argv) not in (2, 3): raise Exception("Invalid number of arguments")

# Load the input image
with Image.open(sys.argv[1]).convert('RGBA') as inImg:
    # If a output image was given
    outDataT: list[pixel]
    if len(sys.argv) == 3:
        # Open the output image
        with Image.open(sys.argv[2]).convert('RGBA') as outImg:
            # If the output image is of an incorrect size, stop the program
            if (inImg.height * 2 != outImg.height) or (inImg.width * 2 != outImg.width):
                raise ValueError("Output image is not double the size of input image")
            
            outDataT: list[pixel] = outImg.getdata() # type: ignore
    else:
        # Create a new image of the right size
        outDataT: list[pixel] = [(255, 255, 255, 255) for _ in range(inImg.height * inImg.width * 4)]

    inData: list[pixel] = inImg.getdata() # type: ignore
    outData: list[pixelL] = [list(px) for px in outDataT]

    # For each pixel of the input image
    for i, px in enumerate(inData):
        x, y = i % inImg.width, i // inImg.height
        for j, channel in enumerate(px):
            # Extract pairs of 2 bits
            val1 = (channel & 0b11000000) >> 6
            val2 = (channel & 0b00110000) >> 4
            val3 = (channel & 0b00001100) >> 2
            val4 = (channel & 0b00000011) >> 0

            # Hides them in a square of 4 pixels
            outData[(x * 2 + 0) + (y * 2 + 0) * inImg.height * 2][j] = (outData[(x * 2 + 0) + (y * 2 + 0) * inImg.height * 2][j] & 0b11111100) | val1
            outData[(x * 2 + 1) + (y * 2 + 0) * inImg.height * 2][j] = (outData[(x * 2 + 1) + (y * 2 + 0) * inImg.height * 2][j] & 0b11111100) | val2
            outData[(x * 2 + 0) + (y * 2 + 1) * inImg.height * 2][j] = (outData[(x * 2 + 0) + (y * 2 + 1) * inImg.height * 2][j] & 0b11111100) | val3
            outData[(x * 2 + 1) + (y * 2 + 1) * inImg.height * 2][j] = (outData[(x * 2 + 1) + (y * 2 + 1) * inImg.height * 2][j] & 0b11111100) | val4
    
    # Convert the data back to an image
    outDataT = [tuple(px) for px in outData]
    endImg = Image.new('RGBA', (inImg.height * 2, inImg.width * 2))
    endImg.putdata(outDataT) # type: ignore

    # Output the image
    endImg.save('Crypto/out.png')
