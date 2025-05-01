from Crypto.Util.number import inverse
from typing import Tuple


class EllipticCurve:
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    a = p - 3
    def __init__(self, b: int):
        self.b = b

    def doub(self, P : Tuple[int,int]) -> Tuple[int,int]:
        x,y = P
        if x == 0 and y == 1:
            return x, y
        k = ((3 * pow(x, 2) + self.a) * inverse(2 * y, self.p)) % self.p
        res_x = (pow(k, 2) - 2 * x) % self.p
        res_y = (k * (x - res_x) - y) % self.p
        return res_x, res_y

    def add(self, P: Tuple[int,int], Q: Tuple[int,int]) -> Tuple[int,int]:
        x1,y1 = P
        x2,y2 = Q
        if x1 == 0 and y1 == 1:
            return x2, y2
        elif x2 == 0 and y2 == 1:
            return x1, y1
        elif x1 == x2 and y1 == y2:
            return self.doub(P)
        elif x1 == x2:
            return 0, 1

            # Наклон линии
        k = (((y2 - y1) % self.p) * inverse(((x2 - x1) % self.p), self.p)) % self.p
        res_x = (pow(k, 2) - x1 - x2) % self.p
        res_y = (k * (x1 - res_x) - y1) % self.p

        return res_x, res_y

    def multiply(self, P: Tuple[int,int], k: int) -> Tuple[int,int]:
        x,y = P
        if k == 0:
            return 0, 1
        elif k == 1:
            return x, y
        elif k == 2:
            return self.doub(P)

        res_x, res_y = 0, 1
        for bit in bin(k)[2:]:
            res_x, res_y = self.doub((res_x, res_y))
            if bit == "1":
                res_x, res_y = self.add((res_x, res_y), (x, y))

        return res_x, res_y


if __name__ == '__main__':
      # 7594621085251130298067615681075696635795
      # 1000000000000000000000000000000000000
    d = 181880515828151775623529011735461115006532


    P = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
         0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
    Q = (0xbec1519f1752a10c462f801d4c7359c1d4f21e8ec486a3b7affff8072eb313,
         0x7407f5ab9e17ab8a6fc18581974d2b77f8c3c2795087b7364cd5d70ed0a7fb89)

    curve = EllipticCurve(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
    print(curve.multiply(P,d))
    print(Q)
    import math
    print(math.log10(181880515828151775623529011735461115006532))