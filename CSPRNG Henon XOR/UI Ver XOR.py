import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import hashlib
import time
import matplotlib.pyplot as plt

# Hénon Map 3D
def henon_map_3d(a, b, x0, y0, z0, iterations):
    x, y, z = np.zeros(iterations), np.zeros(iterations), np.zeros(iterations)
    x[0], y[0], z[0] = x0, y0, z0
    for i in range(1, iterations):
        x[i] = a - y[i-1]**2 - b * z[i-1]
        y[i] = x[i-1]
        z[i] = y[i-1]
    return x, y, z

# Secure Random Sequence with CSPRNG
def secure_random_sequence(seed_data, length):
    hasher = hashlib.sha256()
    hasher.update(seed_data.encode())
    random_sequence = []
    for _ in range(length):
        hasher.update(hasher.digest())
        random_byte = hasher.digest()[0]
        random_sequence.append(random_byte)
    return np.array(random_sequence, dtype=np.uint8)

# Encryption
def encrypt_image(image_path, a, b, x0, y0, z0):
    image = Image.open(image_path).convert('L')
    image_array = np.array(image)
    iterations = image_array.size

    x, y, z = henon_map_3d(a, b, x0, y0, z0, iterations)
    seed_data = ''.join(map(str, (x + y + z)[:iterations]))
    random_sequence = secure_random_sequence(seed_data, iterations)

    encrypted_image_array = np.bitwise_xor(image_array, random_sequence.reshape(image_array.shape))
    encrypted_image = Image.fromarray(encrypted_image_array)
    return encrypted_image, image_array, encrypted_image_array

# Decryption
def decrypt_image(encrypted_image_path, a, b, x0, y0, z0):
    encrypted_image = Image.open(encrypted_image_path).convert('L')
    encrypted_image_array = np.array(encrypted_image)
    iterations = encrypted_image_array.size

    x, y, z = henon_map_3d(a, b, x0, y0, z0, iterations)
    seed_data = ''.join(map(str, (x + y + z)[:iterations]))
    random_sequence = secure_random_sequence(seed_data, iterations)

    decrypted_image_array = np.bitwise_xor(encrypted_image_array, random_sequence.reshape(encrypted_image_array.shape))
    decrypted_image = Image.fromarray(decrypted_image_array)
    return decrypted_image, encrypted_image_array, decrypted_image_array

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

# Histogram Comparison
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
def create_henon_ui():
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
        a, b = float(entry_a.get()), float(entry_b.get())
        x0, y0, z0 = float(entry_x0.get()), float(entry_y0.get()), float(entry_z0.get())
        output_file = "./Ex Image/encrypted_image_henon.png"

        try:
            start_time = time.time()
            encrypted_img, original_array, encrypted_array = encrypt_image(image_path, a, b, x0, y0, z0)
            encrypted_img.save(output_file)
            load_image(output_file, img_result)
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
        encrypted_image_path = "./Ex Image/encrypted_image_henon.png"
        a, b = float(entry_a.get()), float(entry_b.get())
        x0, y0, z0 = float(entry_x0.get()), float(entry_y0.get()), float(entry_z0.get())
        output_file = "./Ex Image/decrypted_image_henon.png"
        original_image_path = entry_file.get()

        try:
            start_time = time.time()
            decrypted_img, encrypted_array, decrypted_array = decrypt_image(
                encrypted_image_path, a, b, x0, y0, z0
            )
            decrypted_img.save(output_file)
            load_image(output_file, img_result)
            end_time = time.time()
            original_img = np.array(Image.open(original_image_path).convert('L'))
            accuracy = np.mean(decrypted_array == original_img) * 100
            log.set(f"Decryption completed in {end_time - start_time:.2f} seconds.\n"
                    f"Decryption Accuracy: {accuracy:.2f}%.")
            plot_histograms(original_img, decrypted_array)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Main UI
    root = tk.Tk()
    root.title("Hénon Map Encryption & Decryption")

    # File Selection
    tk.Label(root, text="Select Image File:").grid(row=0, column=0, padx=5, pady=5)
    entry_file = tk.Entry(root, width=40)
    entry_file.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=5, pady=5)

    # Parameters
    tk.Label(root, text="Hénon Map A:").grid(row=1, column=0, padx=5, pady=5)
    entry_a = tk.Entry(root, width=10)
    entry_a.insert(0, "1.4")
    entry_a.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(root, text="Hénon Map B:").grid(row=2, column=0, padx=5, pady=5)
    entry_b = tk.Entry(root, width=10)
    entry_b.insert(0, "0.3")
    entry_b.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(root, text="Initial X0:").grid(row=3, column=0, padx=5, pady=5)
    entry_x0 = tk.Entry(root, width=10)
    entry_x0.insert(0, "0.1")
    entry_x0.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    tk.Label(root, text="Initial Y0:").grid(row=4, column=0, padx=5, pady=5)
    entry_y0 = tk.Entry(root, width=10)
    entry_y0.insert(0, "0.2")
    entry_y0.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    tk.Label(root, text="Initial Z0:").grid(row=5, column=0, padx=5, pady=5)
    entry_z0 = tk.Entry(root, width=10)
    entry_z0.insert(0, "0.3")
    entry_z0.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    # Encryption & Decryption
    tk.Button(root, text="Encrypt", command=encrypt_action).grid(row=6, column=0, padx=5, pady=10)
    tk.Button(root, text="Decrypt", command=decrypt_action).grid(row=6, column=1, padx=5, pady=10)

    # Image Preview
    img_preview = tk.Label(root)
    img_preview.grid(row=7, column=0, columnspan=3, pady=10)

    # Result Image
    img_result = tk.Label(root)
    img_result.grid(row=8, column=0, columnspan=3, pady=10)

    # Log Output
    log = tk.StringVar()
    tk.Label(root, textvariable=log).grid(row=9, column=0, columnspan=3, pady=10)

    root.mainloop()

create_henon_ui()
