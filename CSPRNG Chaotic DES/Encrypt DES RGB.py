import numpy as np
from PIL import Image
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad

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

def chaos_encrypt(image_array, sequence):
    """
    Encrypt image array using chaotic sequence.
    """
    flat_image = image_array.flatten()
    sequence_indices = np.argsort(sequence)
    encrypted_flat = flat_image[sequence_indices]
    return encrypted_flat.reshape(image_array.shape)

def des_encrypt(data, key):
    """
    Encrypt data using DES.
    """
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(pad(data, DES.block_size))

def image_encryption(image_path, x0_chaos, des_key, output_file):
    """
    Encrypt a color image using chaotic map and DES, then save the result.
    """
    # Load the image
    image = Image.open(image_path)
    image_array = np.array(image)

    # Prepare storage for encrypted data
    encrypted_data_list = []
    height, width, channels = image_array.shape

    # Process each color channel
    for channel in range(channels):
        # Generate chaotic sequence for this channel
        chaos_sequence = logistic_map(height * width, x0_chaos + channel * 0.01)

        # Chaos encryption for the channel
        channel_data = image_array[:, :, channel]
        chaos_encrypted_channel = chaos_encrypt(channel_data, chaos_sequence)

        # DES encryption for the channel
        des_key = des_key[:8]  # Ensure the key is 8 bytes
        encrypted_channel_data = des_encrypt(chaos_encrypted_channel.tobytes(), des_key)
        encrypted_data_list.append(encrypted_channel_data)

    # Save encrypted data and image shape
    with open(output_file, 'wb') as f:
        for encrypted_channel_data in encrypted_data_list:
            f.write(encrypted_channel_data)
        f.write(height.to_bytes(4, 'big'))
        f.write(width.to_bytes(4, 'big'))
        f.write(channels.to_bytes(1, 'big'))

    print(f"Encrypted data saved to {output_file}")

# Parameters
x0 = 0.6  # Initial value for chaos
des_key = b'12345678'  # DES key (8 bytes)
image_path = './Ex Image/cihuy.png'  # Input image path
output_file = 'encrypted_color_image.bin'  # Output encrypted file

# Encrypt and save
image_encryption(image_path, x0, des_key, output_file)
