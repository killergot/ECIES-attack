import asyncio
import logging
import aiohttp
import secrets
from hashlib import sha512
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Util.number import inverse
from Crypto.Hash import HMAC, SHA256
from sympy.ntheory.modular import crt
from src.curve_operation import EllipticCurve
from src.consts import curve_params
from src.logger import init_log

init_log(logging.DEBUG)
log = logging.getLogger(__name__)

SERVER_URL = 'http://45.132.17.192:8080'

# Параметры кривой secp256r1
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = p - 3
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

P = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
     0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

a = None
with open('enc1.txt', 'rb') as f:
    a = f.read()


# Вспомогательные классы и функции

def KDF(K_x):
    hash_result = sha512(str(K_x).encode("utf-8")).digest()
    return hash_result[:32], hash_result[32:]


def construct_payload(x, y, ciphertext, tag):
    # point = b'\x04' + long_to_bytes(x, 32) + long_to_bytes(y, 32)
    point = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
    return point + tag + ciphertext


async def send_request(session, payload, attempt_id):
    try:
        data = aiohttp.FormData()
        data.add_field('file', payload, filename='fake.bin',content_type='application/octet-stream')
        async with session.post(f"{SERVER_URL}/decrypt", data=data) as response:
            if response.status == 200:
                return True
            return False
    except Exception as e:
        log.error(f"Ошибка: {e}")
        return False

d_moduli = []



async def attack(b_i, l_i, R_inv, session):
    print(b_i, l_i, R_inv, sep=',')
    ciphertext = b'\x5F\x5F\x81\xD3\x60\x91\xA7\x63'

    curve = EllipticCurve(b_i)
    found = False
    for j in range(1, l_i):
        K = curve.multiply(R_inv, j)
        if K == (0,1):
            continue
        K_x, _ = K
        _, kev_mac = KDF(K_x)
        hmac = HMAC.new(kev_mac, digestmod=SHA256)
        hmac.update(ciphertext)
        new_tag = hmac.digest()
        payload = construct_payload(R_inv[0], R_inv[1], ciphertext, new_tag)
        success = await send_request(session, payload, f"l_{l_i}_j_{j}")
        if success:
            log.debug(f"l_{l_i}_j_{j}")
            d_moduli.append((l_i, j))
            found = True
            break
    if not found:
        d_moduli.append((l_i, 0))


async def worker(session, curve_param):
    await attack(curve_param[0], curve_param[1], curve_param[2], session)

async def main():
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=100)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for param in curve_params:
            tasks.append(worker(session, param))

        await asyncio.gather(*tasks)

    print(f'{d_moduli = }')


    moduli = [li for li, _ in d_moduli]
    residues = [j % li for li, j in d_moduli]
    d, M = crt(moduli, residues)
    print(f"Восстановленный ключ: {d}, {M = }")


if __name__ == "__main__":
    asyncio.run(main())

