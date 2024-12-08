import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import time
import matplotlib.pyplot as plt

# Logistic Map
def logistic_map(length, x0, r=3.99):
    x = x0
    sequence = []
    for _ in range(length):
        x = r * x * (1 - x)
        sequence.append(x)
    return np.array(sequence)

# DES Encryption
def des_encrypt(data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(pad(data, DES.block_size))

# DES Decryption
def des_decrypt(data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    return unpad(cipher.decrypt(data), DES.block_size)

# Encryption
def encrypt_image(image_path, x0, des_key, output_file):
    image = Image.open(image_path).convert('L')
    image_array = np.array(image)
    chaos_sequence = logistic_map(image_array.size, x0)
    flat_image = image_array.flatten()
    sequence_indices = np.argsort(chaos_sequence)
    encrypted_flat = flat_image[sequence_indices]

    des_key = des_key[:8]
    encrypted_data = des_encrypt(encrypted_flat.tobytes(), des_key)

    with open(output_file, 'wb') as f:
        f.write(encrypted_data)
        f.write(image_array.shape[0].to_bytes(4, 'big'))
        f.write(image_array.shape[1].to_bytes(4, 'big'))

    encrypted_image = Image.fromarray(encrypted_flat.reshape(image_array.shape))
    return encrypted_image, image_array, encrypted_flat.reshape(image_array.shape)

# Decryption
def decrypt_image(input_file, x0, des_key):
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()
        encrypted_image_data = encrypted_data[:-8]
        height = int.from_bytes(encrypted_data[-8:-4], 'big')
        width = int.from_bytes(encrypted_data[-4:], 'big')

    des_key = des_key[:8]
    decrypted_data = des_decrypt(encrypted_image_data, des_key)
    decrypted_image = np.frombuffer(decrypted_data, dtype=np.uint8).reshape((height, width))

    chaos_sequence = logistic_map(decrypted_image.size, x0)
    sequence_indices = np.argsort(chaos_sequence)
    decrypted_flat = np.zeros_like(decrypted_image.flatten())
    decrypted_flat[sequence_indices] = decrypted_image.flatten()

    return Image.fromarray(decrypted_flat.reshape((height, width))), decrypted_image.flatten(), decrypted_flat.reshape((height, width))

# Metrics Calculation
def calculate_metrics(original, encrypted):
    original_array = np.array(original, dtype=np.uint8)
    encrypted_array = np.array(encrypted, dtype=np.uint8)

    # NPCR
    diff_pixels = np.sum(original_array != encrypted_array)
    total_pixels = original_array.size
    npcr = (diff_pixels / total_pixels) * 100

    # UACI
    diff_intensity = np.abs(original_array.astype(int) - encrypted_array.astype(int))
    uaci = np.mean(diff_intensity) / 255 * 100

    # Entropy
    histogram, _ = np.histogram(encrypted_array.flatten(), bins=256, range=(0, 256))
    histogram = histogram / histogram.sum()
    entropy = -np.sum(histogram * np.log2(histogram + np.finfo(float).eps))

    return npcr, uaci, entropy

def plot_histograms(original, encrypted):
    original_array = np.array(original).flatten()
    encrypted_array = np.array(encrypted).flatten()

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(original_array, bins=256, range=(0, 256), color='blue', alpha=0.7)
    plt.title("Original Image Histogram")
    plt.subplot(1, 2, 2)
    plt.hist(encrypted_array, bins=256, range=(0, 256), color='red', alpha=0.7)
    plt.title("Encrypted Image Histogram")
    plt.tight_layout()
    plt.show()

# UI
def create_des_ui():
    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg")])
        if file_path:
            entry_file.delete(0, tk.END)
            entry_file.insert(0, file_path)
            load_image(file_path, img_preview)

    def load_image(file_path, label):
        img = Image.open(file_path)
        img.thumbnail((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk

    def encrypt_action():
        image_path = entry_file.get()
        x0 = float(entry_x0.get())
        des_key = entry_key.get().encode()
        output_file = "encrypted_image_des.bin"

        if len(des_key) != 8:
            messagebox.showerror("Error", "DES Key must be 8 bytes!")
            return

        try:
            start_time = time.time()
            encrypted_img, original_array, encrypted_array = encrypt_image(image_path, x0, des_key, output_file)
            encrypted_img.save("encrypted_image_preview.png")
            load_image("encrypted_image_preview.png", img_result)
            end_time = time.time()
            npcr, uaci, entropy = calculate_metrics(original_array, encrypted_array)
            log.set(
                f"Encryption completed in {end_time - start_time:.2f} seconds.\n"
                f"NPCR: {npcr:.2f}% | UACI: {uaci:.2f}% | Entropy: {entropy:.2f} bits."
            )
            plot_histograms(original_array, encrypted_array)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decrypt_action():
        input_file = "encrypted_image_des.bin"
        x0 = float(entry_x0.get())
        des_key = entry_key.get().encode()

        try:
            start_time = time.time()
            decrypted_img, encrypted_array, decrypted_array = decrypt_image(input_file, x0, des_key)
            decrypted_img.save("decrypted_image_preview.png")
            load_image("decrypted_image_preview.png", img_result)
            end_time = time.time()
            original_image = np.array(Image.open(entry_file.get()).convert('L'))
            accuracy = np.mean(decrypted_array == original_image) * 100
            log.set(f"Decryption completed in {end_time - start_time:.2f} seconds.\n"
                    f"Decryption Accuracy: {accuracy:.2f}%.")
            plot_histograms(original_image, decrypted_array)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Main UI
    root = tk.Tk()
    root.title("DES Encryption & Decryption")

    # File Selection
    tk.Label(root, text="Select Image File:").grid(row=0, column=0, padx=5, pady=5)
    entry_file = tk.Entry(root, width=40)
    entry_file.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=5, pady=5)

    # Parameters
    tk.Label(root, text="Logistic Map X0:").grid(row=1, column=0, padx=5, pady=5)
    entry_x0 = tk.Entry(root, width=10)
    entry_x0.insert(0, "0.6")
    entry_x0.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(root, text="DES Key (8 bytes):").grid(row=2, column=0, padx=5, pady=5)
    entry_key = tk.Entry(root, width=10)
    entry_key.insert(0, "12345678")
    entry_key.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Encryption & Decryption
    tk.Button(root, text="Encrypt", command=encrypt_action).grid(row=3, column=0, padx=5, pady=10)
    tk.Button(root, text="Decrypt", command=decrypt_action).grid(row=3, column=1, padx=5, pady=10)

    # Image Preview
    img_preview = tk.Label(root)
    img_preview.grid(row=4, column=0, columnspan=3, pady=10)

    # Result Image
    img_result = tk.Label(root)
    img_result.grid(row=5, column=0, columnspan=3, pady=10)

    # Log Output
    log = tk.StringVar()
    tk.Label(root, textvariable=log).grid(row=6, column=0, columnspan=3, pady=10)

    root.mainloop()

create_des_ui()
