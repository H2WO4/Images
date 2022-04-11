from PIL import Image

# Define a type shortcut
pixel = tuple[int, int, int, int]

# Open the image
with open("images/testcard_rgba.qoi", 'rb') as img:
	if img.read(4) != b'qoif': raise Exception("Invalid format")

	width = int.from_bytes(img.read(4), 'big', signed=False)
	height = int.from_bytes(img.read(4), 'big', signed=False)

	channels = int.from_bytes(img.read(1), 'big', signed=False)
	colorspace = int.from_bytes(img.read(1), 'big', signed=False)

	pixels: list[int] = []

	cache: list[pixel] = [(0, 0, 0, 255)] * 64
	last: pixel = (0, 0, 0, 255)
	for _ in range(width * height):
		data = img.read(1)
		match data:
			# Case RGB
			case b'\xfe':
				red = int.from_bytes(img.read(1), 'big', signed=False)
				grn = int.from_bytes(img.read(1), 'big', signed=False)
				blu = int.from_bytes(img.read(1), 'big', signed=False)

				px = (red, grn, blu, last[3])
				pixels.extend(px)

			# Case RGBA
			case b'\xff':
				red = int.from_bytes(img.read(1), 'big', signed=False)
				grn = int.from_bytes(img.read(1), 'big', signed=False)
				blu = int.from_bytes(img.read(1), 'big', signed=False)
				alp = int.from_bytes(img.read(1), 'big', signed=False)

				px = (red, grn, blu, alp)
				pixels.extend(px)

			# Case INDEX
			case by if by < b'\x40':
				posToTake = int.from_bytes(by, 'big', signed=False)
				px = cache[posToTake]
				pixels.extend(px)
			
			# Case DIFF
			case by if by < b'\x80':
				dr = ((int.from_bytes(by, 'big') & 0b00110000) >> 4) - 2
				dg = ((int.from_bytes(by, 'big') & 0b00001100) >> 2) - 2
				db = ((int.from_bytes(by, 'big') & 0b00000011) >> 0) - 2

				red = (last[0] + dr) % 256
				grn = (last[1] + dg) % 256
				blu = (last[2] + db) % 256
				px = (red, grn, blu, last[3])
				pixels.extend(px)

			# Case LUMA
			case by if by < b'\xC0':
				by2 = img.read(1)

				dg = (int.from_bytes(by, 'big') & 0b00111111) - 32
				dr2 = ((int.from_bytes(by2, 'big') & 0b11110000) >> 4) - 8
				db2 = ((int.from_bytes(by2, 'big') & 0b00001111) >> 0) - 8

				red = (last[0] + dg + dr2) % 256
				grn = (last[1] + dg) % 256
				blu = (last[2] + dg + db2) % 256
				px = (red, grn, blu, last[3])
				pixels.extend(px)

			# Case RUN
			case by:
				count = int.from_bytes(by, 'big') & 0b00111111

				px = last
				for _ in range(count+1):
					pixels.extend(px)
		
		pos = (px[0] * 3 + px[1] * 5 + px[2] * 7 + px[3] * 11) % 64
		cache[pos] = px
		last = px

	Image.frombytes('RGBA', (256, 256), bytes(pixels)).save('out.png') # type: ignore