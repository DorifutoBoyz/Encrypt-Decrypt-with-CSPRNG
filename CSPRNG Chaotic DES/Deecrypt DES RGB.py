import numpy as np
from PIL import Image
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad

def logistic_map(length, x0, r=3.99):
    """
    Logistic map for generating pseudo-random sequence.
    """
    x = x0
    sequence = []
    for _ in range(length):
        x = r * x * (1 - x)
        sequence.append(x)
    return np.array(sequence)

def des_decrypt(data, key):
    """
    Decrypt data using DES.
    """
    cipher = DES.new(key, DES.MODE_ECB)
    return unpad(cipher.decrypt(data), DES.block_size)

def chaos_decrypt(image_array, sequence):
    """
    Decrypt image array using chaotic sequence.
    """
    flat_image = image_array.flatten()
    sequence_indices = np.argsort(sequence)
    decrypted_flat = np.zeros_like(flat_image)
    decrypted_flat[sequence_indices] = flat_image
    return decrypted_flat.reshape(image_array.shape)

def image_decryption(input_file, x0_chaos, des_key, output_image_path):
    """
    Decrypt a color image using chaotic map and DES, then save the result.
    """
    # Load encrypted data and image shape
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()

    height = int.from_bytes(encrypted_data[-9:-5], 'big')
    width = int.from_bytes(encrypted_data[-5:-1], 'big')
    channels = encrypted_data[-1]
    encrypted_data = encrypted_data[:-9]

    # Prepare storage for decrypted channels
    decrypted_channels = []
    data_per_channel = len(encrypted_data) // channels

    # Process each color channel
    for channel in range(channels):
        encrypted_channel_data = encrypted_data[channel * data_per_channel:(channel + 1) * data_per_channel]

        # DES decryption
        des_key = des_key[:8]  # Ensure the key is 8 bytes
        decrypted_channel_data = des_decrypt(encrypted_channel_data, des_key)
        decrypted_channel = np.frombuffer(decrypted_channel_data, dtype=np.uint8).reshape((height, width))

        # Chaos decryption
        chaos_sequence = logistic_map(height * width, x0_chaos + channel * 0.01)
        chaos_decrypted_channel = chaos_decrypt(decrypted_channel, chaos_sequence)

        decrypted_channels.append(chaos_decrypted_channel)

    # Combine channels and save as image
    decrypted_image = np.stack(decrypted_channels, axis=-1).astype(np.uint8)
    Image.fromarray(decrypted_image).save(output_image_path)
    print(f"Decrypted image saved to {output_image_path}")

# Parameters
x0 = 0.6  # Initial value for chaos
des_key = b'12345678'  # DES key (8 bytes)
input_file = 'encrypted_color_image.bin'  # Encrypted input file
output_image_path = 'decrypted_color_image.png'  # Output decrypted image path

# Decrypt and save
image_decryption(input_file, x0, des_key, output_image_path)
