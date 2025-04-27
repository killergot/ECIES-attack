import requests

SERVER_URL = 'http://45.132.17.192:8080'


def encrypt_file(file_path):
    url = f"{SERVER_URL}/encrypt"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        encrypted_data = response.content
        print("[+] Успешно зашифровали файл.")
        print(f"[+] Длина зашифрованных данных: {len(encrypted_data)} байт")

        # Распарсим зашифрованные данные
        R = encrypted_data[:65]
        tag = encrypted_data[65:97]
        ciphertext = encrypted_data[97:]

        print(f"    - Длина точки R: {len(R)} байт")
        print(f"    - Длина тега: {len(tag)} байт")
        print(f"    - Длина шифртекста: {len(ciphertext)} байт")

        print(f"    - Точка R (hex): {R.hex()}")
        print(f"    - Тег (hex): {tag.hex()}")
        print(f"    - Первые 32 байта шифртекста (hex): {ciphertext.hex()[:32]}...")

        return encrypted_data
    else:
        print("[-] Ошибка при шифровании:", response.status_code, response.text)
        return None


# Пример использования
encrypted = encrypt_file("test.txt")

def decrypt_file(encrypted_data, save_to_file=None):
    url = f"{SERVER_URL}/decrypt"
    files = {'file': ('encrypted.bin', encrypted_data)}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        decrypted_data = response.content
        print("[+] Успешно расшифровали файл.")
        print(f"[+] Длина расшифрованных данных: {len(decrypted_data)} байт")

        if save_to_file:
            with open(save_to_file, 'wb') as f:
                f.write(decrypted_data)
            print(f"[+] Расшифрованные данные сохранены в: {save_to_file}")

        else:
            print(f"[+] Первые 100 байт расшифрованного файла: {decrypted_data[:100].hex()}...")

        return decrypted_data
    else:
        print("[-] Ошибка при расшифровке:", response.status_code, response.text)
        return None

# Пример использования
decrypt_file(encrypted, save_to_file="decrypted_output.txt")

