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
    Decrypt an image using chaotic map and DES and save the result.
    """
    # Load encrypted data and shape
    with open(input_file, 'rb') as f:
        # Baca data terenkripsi, tinggi, dan lebar gambar
        encrypted_data = f.read()
        encrypted_image_data = encrypted_data[:-8]
        height = int.from_bytes(encrypted_data[-8:-4], 'big')
        width = int.from_bytes(encrypted_data[-4:], 'big')

    # Debug ukuran data
    print(f"Height: {height}, Width: {width}, Encrypted size: {len(encrypted_image_data)}")

    # DES decryption
    des_key = des_key[:8]  # Ensure the key is 8 bytes
    decrypted_data = des_decrypt(encrypted_image_data, des_key)

    # Pastikan panjang data cocok dengan dimensi gambar
    if len(decrypted_data) != height * width:
        raise ValueError("Decrypted data size does not match the expected image dimensions.")

    decrypted_image = np.frombuffer(decrypted_data, dtype=np.uint8).reshape((height, width))

    # Chaos decryption
    chaos_sequence = logistic_map(decrypted_image.size, x0_chaos)
    decrypted_image = chaos_decrypt(decrypted_image, chaos_sequence)

    # Save decrypted image
    Image.fromarray(decrypted_image).save(output_image_path)
    print(f"Decrypted image saved to {output_image_path}")
# Parameters
x0 = 0.6  # Initial value for chaos
des_key = b'12345678'  # DES key (8 bytes)
input_file = 'encrypted_image.bin'  # Encrypted input file
output_image_path = 'decrypted_image.jpg'  # Output decrypted image path

# Decrypt and save
image_decryption(input_file, x0, des_key, output_image_path)
