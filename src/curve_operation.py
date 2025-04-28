from Crypto.Util.number import inverse


class EllipticCurve:
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    a = p - 3
    def __init__(self, b: int):
        self.b = b

    def doub(self, P : tuple[int,int]) -> tuple[int,int]:
        x,y = P
        if x == 0 and y == 1:
            return x, y
        k = ((3 * pow(x, 2) + self.a) * inverse(2 * y, self.p)) % self.p
        res_x = (pow(k, 2) - 2 * x) % self.p
        res_y = (k * (x - res_x) - y) % self.p
        return res_x, res_y

    def add(self, P: tuple[int,int], Q: tuple[int,int]) -> tuple[int,int]:
        x1,x2 = P
        y1,y2 = Q
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

    def multiply(self, P: tuple[int,int], k: int) -> tuple[int,int]:
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


# 1000000000000000000000000000000000000
curve_params  = [(1, 71, (36736174255430481322464234874556528245203675859399413306108823132070684213726,
71216636841328212438673497139478287243103393296160619745025773562518613953888)),
(3, 7, (86861948779320723735809409166338661013924870073533153401405380363591285609445 ,
92959093380773739239256843672796491295827279525897738876018216604059003433908)),
(3, 13, (103036411228144032028317979289017837935011730613883144548126938746409368311935 ,
48489375743398105900530688649564883692387604260644442869328533348008113953260)),
(3, 37, (6829338390266237482283310246665103308891228336319477318479644522260556056309 ,
41090420942805220562393108111996992853311669414049431247759332665206023742070)),
(4, 179, (83229040458127123746763986781924855834855773376892353224964588596517159218446 ,
89598705492901877225454412430249165727296653092812945717144067107278708102557)),
(6, 5, (39750170337003670022494616352462194843889127399495951655079750874966815322615 ,
65141808569782695839169856395194564992307712545138211871768272355352435143036)),
(10, 17, (28441888532776736443884565435952912890996156064275160816382945068056727079366 ,
62774884647663948051590459932614506163828928024892425144614982360172294976753))]

if __name__ == '__main__':
    d = 3_133_632_712
    P = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
         0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
    Q = (0xbec1519f1752a10c462f801d4c7359c1d4f21e8ec486a3b7affff8072eb313,
         0x7407f5ab9e17ab8a6fc18581974d2b77f8c3c2795087b7364cd5d70ed0a7fb89)

    curve = EllipticCurve(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
    print(curve.multiply(P,d))
    print(Q)