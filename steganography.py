from PIL import Image

END_MARKER = b"<<<END>>>"

def encode(image_path, output_path, data_bytes: bytes):
    """Embed bytes into an image using LSB steganography."""
    data_bytes += END_MARKER
    binary_secret = ''.join(format(b, "08b") for b in data_bytes)

    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    if len(binary_secret) > len(pixels) * 3:
        raise ValueError("Data too large to hide in image")

    new_pixels = []
    bit_index = 0

    for r, g, b in pixels:
        r_new = (r & ~1) | int(binary_secret[bit_index]) if bit_index < len(binary_secret) else r
        bit_index += 1 if bit_index < len(binary_secret) else 0

        g_new = (g & ~1) | int(binary_secret[bit_index]) if bit_index < len(binary_secret) else g
        bit_index += 1 if bit_index < len(binary_secret) else 0

        b_new = (b & ~1) | int(binary_secret[bit_index]) if bit_index < len(binary_secret) else b
        bit_index += 1 if bit_index < len(binary_secret) else 0

        new_pixels.append((r_new, g_new, b_new))

    img.putdata(new_pixels)
    img.save(output_path)

def decode(image_path) -> bytes:
    """Extract bytes hidden in image."""
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    binary_data = ""
    for pixel in pixels:
        for val in pixel:
            binary_data += str(val & 1)

    bytes_list = []
    for i in range(0, len(binary_data), 8):
        byte = int(binary_data[i:i+8], 2)
        bytes_list.append(byte)
        if bytes(bytes_list[-len(END_MARKER):]) == END_MARKER:
            return bytes(bytes_list[:-len(END_MARKER)])
    return bytes(bytes_list)
