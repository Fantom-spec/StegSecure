from PIL import Image

END_MARKER = "<<<END>>>"

def text_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    text = ""
    for c in chars:
        text += chr(int(c, 2))
        if text.endswith(END_MARKER):
            return text.replace(END_MARKER, "")
    return text

# Encode function now works with any string (hex included)
def encode(image_path, output_path, secret_text):
    # append marker
    secret_text += END_MARKER
    # convert to binary
    binary_secret = text_to_binary(secret_text)

    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = list(img.getdata())

    if len(binary_secret) > len(pixels) * 3:
        raise ValueError("Text too large to hide in this image")

    new_pixels = []
    bit_index = 0

    for pixel in pixels:
        r, g, b = pixel
        if bit_index < len(binary_secret):
            r = (r & ~1) | int(binary_secret[bit_index])
            bit_index += 1
        if bit_index < len(binary_secret):
            g = (g & ~1) | int(binary_secret[bit_index])
            bit_index += 1
        if bit_index < len(binary_secret):
            b = (b & ~1) | int(binary_secret[bit_index])
            bit_index += 1
        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save(output_path)
    print("Encrypted text hidden successfully")

def decode(image_path):
    img = Image.open(image_path)
    pixels = list(img.getdata())

    binary_data = ""
    for pixel in pixels:
        for value in pixel:
            binary_data += str(value & 1)

    secret = binary_to_text(binary_data)
    return secret

# ===== Example Usage =====
# Suppose you have a hex string representing encrypted data
# encrypted_hex = "a3f5b2c1d4e6"  # replace with your actual encrypted hex
# encode("input.png", "input.png", encrypted_hex)
#decode(r"memes\\1080ca91-2ebe-4d06-b760-33d49e60eb23.png")
