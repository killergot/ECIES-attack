import asyncio
import logging

import aiohttp
import secrets
from hashlib import sha256
from Crypto.Util.number import bytes_to_long, long_to_bytes

from src.logger import init_log

log = logging.getLogger(__name__)


SERVER_URL = 'http://45.132.17.192:8080'

# Параметры кривой secp256r1
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = p - 3
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551


# --- Вспомогательные функции --- #

def is_quadratic_residue(x):
    return pow(x, (p - 1) // 2, p) == 1


def generate_invalid_point():
    while True:
        x = secrets.randbelow(p)
        fake_rhs = (pow(x, 3, p) + a * x + b + 1) % p  # ломаем уравнение кривой
        if is_quadratic_residue(fake_rhs):
            y = pow(fake_rhs, (p + 1) // 4, p)
            if pow(y, 2, p) == fake_rhs:
                return (x, y)


def construct_payload(x, y):
    point_prefix = b'\x04' + long_to_bytes(x, 32) + long_to_bytes(y, 32)
    fake_tag = b'\x00' * 32
    fake_ciphertext = b'\x00' * 16
    payload = point_prefix + fake_tag + fake_ciphertext
    return payload


async def send_decrypt_request(session, payload, attempt_id):
    try:
        data = aiohttp.FormData()
        data.add_field('file', payload, filename='fake.bin', content_type='application/octet-stream')

        async with session.post(f"{SERVER_URL}/decrypt", data=data) as response:
            if response.status == 200:
                content = await response.read()
                print(f"[+] Попытка {attempt_id}: Успешно! Ответ {len(content)} байт.")
                print(f"    - Первые 32 байта: {content[:32].hex()}...")
                log.debug(f"[+] attempt {attempt_id}: success! Response {len(content)} bytes."
                          f"\n {data = }, bytes: {content.hex()}")
                return content
            else:
                print(f"[-] Попытка {attempt_id}: Ошибка {response.status}")
    except Exception as e:
        print(f"[-] Попытка {attempt_id}: Исключение {e}")


async def worker(session, worker_id, total_tasks):
    for i in range(total_tasks):
        x, y = generate_invalid_point()
        payload = construct_payload(x, y)
        await send_decrypt_request(session, payload, f"Worker-{worker_id} Try-{i + 1}")


async def main():
    total_workers = 10  # Количество одновременных воркеров
    tasks_per_worker = 50  # Количество запросов на одного воркера

    timeout = aiohttp.ClientTimeout(total=30)  # Настроим таймаут с запасом
    connector = aiohttp.TCPConnector(limit=100)  # Ограничим число одновременных соединений

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for worker_id in range(total_workers):
            tasks.append(worker(session, worker_id, tasks_per_worker))

        await asyncio.gather(*tasks)


# --- Запуск атаки --- #
if __name__ == "__main__":
    init_log(logging.DEBUG)
    asyncio.run(main())
