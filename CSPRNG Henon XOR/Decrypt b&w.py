import numpy as np
from PIL import Image
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
    hasher = hashlib.sha256()
    hasher.update(seed_data.encode())
    random_sequence = []

    for _ in range(length):
        hasher.update(hasher.digest())
        random_byte = hasher.digest()[0]
        random_sequence.append(random_byte)

    return np.array(random_sequence, dtype=np.uint8)

# Fungsi untuk mendekripsi gambar dengan Hénon Map dan CSPRNG
def decrypt_image(encrypted_image_path, a, b, x0, y0, z0):
    # Membaca gambar terenkripsi dan mengubahnya menjadi format grayscale
    encrypted_image = Image.open(encrypted_image_path).convert('L')
    encrypted_image_array = np.array(encrypted_image)
    
    # Menentukan jumlah iterasi yang sesuai
    iterations = encrypted_image_array.size  # Jumlah piksel
    
    # Menghasilkan urutan pseudo-random menggunakan Hénon Map
    x, y, z = henon_map_3d(a, b, x0, y0, z0, iterations)
    
    # Gabungkan hasil Hénon Map menjadi string yang akan digunakan sebagai seed untuk CSPRNG
    seed_data = ''.join(map(str, (x + y + z)[:iterations]))  # Gabungkan hasil Hénon Map
    random_sequence = secure_random_sequence(seed_data, iterations)
    
    # Mendekripsi gambar menggunakan operasi XOR dengan CSPRNG
    decrypted_image_array = np.bitwise_xor(encrypted_image_array, random_sequence.reshape(encrypted_image_array.shape))
    
    # Mengubah array kembali ke gambar
    decrypted_image = Image.fromarray(decrypted_image_array)
    return decrypted_image

# Menyimpan dan menampilkan gambar terdekripsi
encrypted_image_path = './Ex Image/encrypted_image_with_csprng.png'  # Ganti dengan path gambar terenkripsi
a, b = 1.4, 0.3  # Parameter Hénon Map
x0, y0, z0 = 0.1, 0.2, 0.3  # Kondisi awal

decrypted_image = decrypt_image(encrypted_image_path, a, b, x0, y0, z0)
decrypted_image.save('./Ex Image/decrypted_image.png')
decrypted_image.show()