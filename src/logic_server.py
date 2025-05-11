from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Random import get_random_bytes
from curve_operation import EllipticCurve
from Crypto.Hash import HMAC, SHA256

from random import randint
from hashlib import sha512




ECC = EllipticCurve(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
P = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
         0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
d = 993913066640853197984481546239524653
Q = ECC.multiply(P,d)

def KDF(K_x):
    hash_result = sha512(str(K_x).encode("utf-8")).digest()
    return hash_result[:32], hash_result[32:]



def construct_payload(x, y, c, tag):
    # point = b'\x04' + long_to_bytes(x, 32) + long_to_bytes(y, 32)
    point = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
    return point + tag + c


def ECIES_encrypt(data):
    r = randint(0,2**125)
    R = ECC.multiply(P,r)
    K = ECC.multiply(Q,r)
    sym_key, mac_key = KDF(K[0])
    c = aes_ctr_encrypt(data, sym_key)
    t = get_mac(mac_key,c)
    return construct_payload(R[0],R[1],c,t)



def parse_point(point: bytes):
    point = (int.from_bytes(point[:32], byteorder='big'),int.from_bytes(point[32:], byteorder='big'))
    return point


def ECIES_decrypt(data):
    R = data[1:65]
    t = data[65:97]
    c = data[97:]


    K = parse_point(R)
    K = ECC.multiply(K,d)
    sym_key, mac_key = KDF(K[0])
    t_true = get_mac(mac_key,c)
    if t_true != t:
        print('Плохо')
        return None
    m = aes_ctr_decrypt(c, sym_key)
    return m

def get_mac(key, data):
    hmac = HMAC.new(key, digestmod=SHA256)
    hmac.update(data)
    new_tag = hmac.digest()
    return new_tag



def aes_ctr_encrypt(plaintext: bytes, key: bytes, nonce_len: int = 8) -> bytes:
    """
    Шифрует данные с использованием AES-CTR (PyCryptodome).

    :param plaintext: Исходные данные для шифрования.
    :param key: Ключ (16, 24 или 32 байта для AES-128, AES-192, AES-256).
    :param nonce_len: Длина nonce (обычно 8 байт).
    :return: (nonce, ciphertext) – nonce и зашифрованные данные.
    """
    nonce = get_random_bytes(nonce_len)  # Генерируем nonce (по умолчанию 8 байт)

    # Создаём счётчик (nonce + нулевой счётчик)
    ctr = Counter.new(64, prefix=nonce, initial_value=0)  # 64 бита = 8 байт

    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    ciphertext = cipher.encrypt(plaintext)

    return (nonce + ciphertext)


def aes_ctr_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    Дешифрует данные, зашифрованные AES-CTR (PyCryptodome).

    :param ciphertext: Зашифрованные данные.
    :param key: Ключ (должен совпадать с ключом шифрования).
    :param nonce: Nonce, использованный при шифровании.
    :return: Расшифрованные данные.
    """
    nonce = ciphertext[:8]
    ciphertext = ciphertext[8:]
    # Восстанавливаем счётчик (как при шифровании)
    ctr = Counter.new(64, prefix=nonce, initial_value=0)  # 64 бита = 8 байт

    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    plaintext = cipher.decrypt(ciphertext)

    return plaintext


# Пример использования
if __name__ == "__main__":
    key = 993913066640853197984481546239524653
    key = key.to_bytes(length=32)
    plaintext = b"Hello, world! This is a secret message."

    # Шифруем (nonce = 8 байт)
    ciphertext = aes_ctr_encrypt(plaintext, key, nonce_len=8)
    print("Nonce (8 bytes):", ciphertext[:8].hex())
    print("Ciphertext:", ciphertext.hex())

    # Дешифруем
    decrypted = aes_ctr_decrypt(ciphertext, key)
    print("Decrypted:", decrypted.decode())

    test = ECIES_encrypt(b'test')
    a = ECIES_decrypt(test)
    print(a)