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
    Encrypt an image using chaotic map and DES and save the result.
    """
    # Load the image and convert to grayscale
    image = Image.open(image_path).convert('L')
    image_array = np.array(image)

    # Generate chaotic sequence
    chaos_sequence = logistic_map(image_array.size, x0_chaos)
    
    # Chaos encryption
    chaos_encrypted_image = chaos_encrypt(image_array, chaos_sequence)
    
    # DES encryption
    des_key = des_key[:8]  # Ensure the key is 8 bytes
    encrypted_data = des_encrypt(chaos_encrypted_image.tobytes(), des_key)

    # Save encrypted data and shape
    with open(output_file, 'wb') as f:
        f.write(encrypted_data)
        f.write(image_array.shape[0].to_bytes(4, 'big'))
        f.write(image_array.shape[1].to_bytes(4, 'big'))

    print(f"Encrypted data saved to {output_file}")

# Parameters
x0 = 0.6  # Initial value for chaos
des_key = b'12345678'  # DES key (8 bytes)
image_path = './Ex Image/cihuy.png'  # Input image path
output_file = 'encrypted_image.bin'  # Output encrypted file

# Encrypt and save
image_encryption(image_path, x0, des_key, output_file)
