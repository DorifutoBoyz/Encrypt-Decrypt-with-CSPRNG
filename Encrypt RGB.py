import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import secrets
import hashlib

# Fungsi untuk 3D Hénon Map
def henon_map_3d(a, b, x0, y0, z0, iterations):
    x, y, z = np.zeros(iterations), np.zeros(iterations), np.zeros(iterations)
    x[0], y[0], z[0] = x0, y0, z0

    for i in range(1, iterations):
        x[i] = a - y[i-1]**2 - b * z[i-1]
        y[i] = x[i-1]
        z[i] = y[i-1]
    
    return x, y, z

# Fungsi untuk menghasilkan urutan acak yang aman secara kriptografis menggunakan CSPRNG
def secure_random_sequence(seed_data, length):
    # Menggunakan hashlib untuk menghasilkan urutan acak yang aman berdasarkan data awal
    hasher = hashlib.sha256()
    hasher.update(seed_data.encode())  # Data kunci atau entropy yang diambil dari Hénon Map
    random_sequence = []

    for _ in range(length):
        hasher.update(hasher.digest())  # Update hash untuk menghasilkan byte baru
        random_byte = hasher.digest()[0]  # Ambil byte pertama
        random_sequence.append(random_byte)

    return np.array(random_sequence, dtype=np.uint8)

# Fungsi untuk mengenkripsi gambar dengan Hénon Map dan CSPRNG
def encrypt_image(image_path, a, b, x0, y0, z0):
    # Membaca gambar dan mengubahnya menjadi format RGB
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)
    
    # Menentukan jumlah iterasi yang sesuai
    iterations = image_array.size  # Jumlah piksel (3 kali jumlah piksel untuk RGB)
    
    # Menghasilkan urutan pseudo-random menggunakan Hénon Map
    x, y, z = henon_map_3d(a, b, x0, y0, z0, iterations)
    
    # Gabungkan hasil Hénon Map menjadi string yang akan digunakan sebagai seed untuk CSPRNG
    seed_data = ''.join(map(str, (x + y + z)[:iterations]))  # Gabungkan hasil Hénon Map
    random_sequence = secure_random_sequence(seed_data, iterations)
    
    # Mengenkripsi gambar menggunakan operasi XOR dengan CSPRNG
    encrypted_image_array = np.bitwise_xor(image_array, random_sequence.reshape(image_array.shape))
    
    # Mengubah array kembali ke gambar
    encrypted_image = Image.fromarray(encrypted_image_array)
    return encrypted_image

# Menyimpan dan menampilkan gambar terenkripsi
image_path = './Ex Image/cihuy.png'  # Ganti dengan path gambar yang ingin dienkripsi
a, b = 1.4, 0.3  # Parameter Hénon Map
x0, y0, z0 = 0.1, 0.2, 0.3  # Kondisi awal

encrypted_image = encrypt_image(image_path, a, b, x0, y0, z0)
encrypted_image.save('./Ex Image/encrypted_image_with_csprng.png')
encrypted_image.show()
