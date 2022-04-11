from PIL import Image
import sys
# https://qoiformat.org/qoi-specification.pdf

# Define a type shortcut
pixel = tuple[int, int, int, int]

# Check for correct number of args
if len(sys.argv) != 2: raise Exception("Invalid number of arguments")

# Open the image
with open(sys.argv[1], 'rb') as img:
	# Verify magic string
	if img.read(4) != b'qoif': raise Exception("Invalid format")

	# Get dimensions
	width = int.from_bytes(img.read(4), 'big', signed=False)
	height = int.from_bytes(img.read(4), 'big', signed=False)

	# Get channels and colorspace
	channels = int.from_bytes(img.read(1), 'big', signed=False)
	colorspace = int.from_bytes(img.read(1), 'big', signed=False)

	# Initialize the output list, the cache and last pixel value
	pixels: list[int] = []
	cache: list[pixel] = [(0, 0, 0, 255)] * 64
	last: pixel = (0, 0, 0, 255)

	# Repeat for each pixel
	i = 0
	while i < width * height:
		# Read a byte and interpret it
		data = img.read(1)
		match data:
			# QOI_OP_RGB
			case b'\xfe':
				# Read the 3 next bytes as RGB
				red = int.from_bytes(img.read(1), 'big', signed=False)
				grn = int.from_bytes(img.read(1), 'big', signed=False)
				blu = int.from_bytes(img.read(1), 'big', signed=False)

				# Reuse the last alpha value
				px = (red, grn, blu, last[3])
				# Add the data
				pixels.extend(px)

			# QOI_OP_RGBA
			case b'\xff':
				# Read the 3 next bytes as RGBA
				red = int.from_bytes(img.read(1), 'big', signed=False)
				grn = int.from_bytes(img.read(1), 'big', signed=False)
				blu = int.from_bytes(img.read(1), 'big', signed=False)
				alp = int.from_bytes(img.read(1), 'big', signed=False)

				px = (red, grn, blu, alp)
				# Add the data
				pixels.extend(px)

			# QOI_OP_INDEX
			case by if by < b'\x40':
				# Interpret the byte as int
				posToTake = int.from_bytes(by, 'big', signed=False)

				# Look for the correct pixel in the cache
				px = cache[posToTake]
				# Add the data
				pixels.extend(px)
			
			# QOI_OP_DIFF
			case by if by < b'\x80':
				# Read the 3 parts of the byte as DR, DG, DB
				# Encoded with a bias of +2 so need to correct for the bias
				dr = ((int.from_bytes(by, 'big') & 0b00110000) >> 4) - 2
				dg = ((int.from_bytes(by, 'big') & 0b00001100) >> 2) - 2
				db = ((int.from_bytes(by, 'big') & 0b00000011) >> 0) - 2

				# Apply the difference and the wraparound
				red = (last[0] + dr) % 256
				grn = (last[1] + dg) % 256
				blu = (last[2] + db) % 256

				# Reuse the last alpha value
				px = (red, grn, blu, last[3])
				# Add the data
				pixels.extend(px)

			# QOI_OP_LUMA
			case by if by < b'\xC0':
				# Read the next byte
				by2 = img.read(1)

				# Read the first byte as DG
				dg = (int.from_bytes(by, 'big') & 0b00111111) - 32
				# Read the next byte as DG - DR, DG - DB
				dr2 = ((int.from_bytes(by2, 'big') & 0b11110000) >> 4) - 8
				db2 = ((int.from_bytes(by2, 'big') & 0b00001111) >> 0) - 8

				# Apply the difference and the wraparound
				red = (last[0] + dg + dr2) % 256
				grn = (last[1] + dg) % 256
				blu = (last[2] + dg + db2) % 256

				# Reuse the last alpha value
				px = (red, grn, blu, last[3])
				# Add the data
				pixels.extend(px)

			# QOI_OP_RUN
			case by:
				# Interpret the byte as int
				n = int.from_bytes(by, 'big') & 0b00111111

				# Correctly 'substract' the number of bytes that need to be read
				i += n

				# Add the last byte n times
				px = last
				for _ in range(n+1):
					pixels.extend(px)
		
		# Hash this pixel
		pos = (px[0] * 3 + px[1] * 5 + px[2] * 7 + px[3] * 11) % 64
		# Put it in the cache
		cache[pos] = px
		# Set the last read pixel as this one
		last = px

		# Increment the number of bytes read
		i += 1

	# Check that the bytestream end is correct
	if img.read() != b'\x00\x00\x00\x00\x00\x00\x00\x01': raise Exception("Invalid file ending")

	# Save the decoded image as PNG
	Image.frombytes('RGBA', (width, height), bytes(pixels)).save('out.png') # type: ignore