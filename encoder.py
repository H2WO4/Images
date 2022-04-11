from PIL import Image

pixel = tuple[int, int, int] | tuple[int, int, int, int]


with Image.open("test.png").convert('RGBA') as img:
	outbytes: list[bytes] = [b'0b11111111', b'0x00', b'0x00', b'0x00', b'0xFF']
	data: list[pixel] = img.getdata() # type: ignore

	cache: list[pixel] = [(0, 0, 0)] * 64
	i: int = 0
	for px in data:
		match outbytes[i]:
			case b'0b11111111':
				print((outbytes[i+1], outbytes[i+2], outbytes[i+3]))
			
			case _:
				pass