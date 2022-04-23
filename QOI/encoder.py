import sys
from PIL import Image
# https://qoiformat.org/qoi-specification.pdf

# Define a type shortcut
pixel = tuple[int, int, int, int]

# Check for correct number of args
if len(sys.argv) != 2: raise Exception("Invalid number of arguments")

# Open the image
with Image.open(sys.argv[1]).convert('RGBA') as img:
	pixels: bytearray = bytearray()
	data: list[pixel] = img.getdata() # type: ignore

	cache: list[pixel] = [(0, 0, 0, 255)] * 64
	last: pixel = (0, 0, 0, 255)

	for px in data:
		match px:
			# QOI_OP_RUN
			case _ if px == last:
				try:
					prev = pixels[-1]
					if 0xC0 <= prev < 0xFD \
					and (pixels[-2] & 0b11000000) != 0x80 \
					and pixels[-4] != 0xFE \
					and pixels[-5] != 0xFF:
						pixels[-1] += 1
					else:
						pixels.append(0xC0)
				
				except IndexError:
					pixels.append(0xC0)
			
			# QOI_OP_INDEX
			case _ if px in cache:
				pixels.append(cache.index(px))
			
			# QOI_OP_DIFF
			case (r, g, b, a) if a == last[3] \
			and (r - last[0]) % 256 in (0, 1, 254, 255) \
			and (g - last[1]) % 256 in (0, 1, 254, 255) \
			and (b - last[2]) % 256 in (0, 1, 254, 255):
				dr = ((r - last[0]) + 2) % 256
				dg = ((g - last[1]) + 2) % 256
				db = ((b - last[2]) + 2) % 256
				pixels.append(0x40 | (dr << 4) | (dg << 2) | (db << 0))
			
			# QOI_OP_RGB
			case (r, g, b, a) if a == last[3]:
				pixels.extend((0xFE, r, g, b))

			# QOI_OP_RGBA
			case (r, g, b, a):
				pixels.extend((0xFF, r, g, b, a))
		
		# Hash this pixel
		pos = (px[0] * 3 + px[1] * 5 + px[2] * 7 + px[3] * 11) % 64
		# Put it in the cache
		cache[pos] = px
		# Set the last read pixel as this one
		last = px
	
	with open("QOI/out.qoi", 'wb') as f:
		f.write(b'qoif')
		f.write(img.height.to_bytes(4, 'big'))
		f.write(img.width.to_bytes(4, 'big'))
		f.write(b'\x04\x00')
		f.write(pixels)
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x01')