from ecdsa.ellipticcurve import CurveFp, Point

# Параметры поля
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = p - 3

# Факторизации и порядки
factorization = {
    3:  [2, 3, 7, 13, 37, 97, 113],
    6:  [2, 5, 4003, 16033, 102001],
    18: [2, 7, 29, 349, 13998374731216357]
}
orders = {
    3:  2**4 * 3 * 7 * 13 * 37 * 97 * 113 *
        65364863466230065009299609518518318921279098632127819301704248465833,
    6:  2**2 * 5 *
        4003 * 16033 * 102001 *
        884390526899024919222120216398419141830968591728388637593606029,
    18: 2**3 * 7 * 29 * 349 *
        13998374731216357 *
        14594520227108627509460787496885153005246714980644220773,
}

results = []
threshold = 100  # «малый» делитель ≤100

for b, ls in factorization.items():
    curve = CurveFp(p, a, b)
    N = orders[b]

    # ищем первую валидную точку G
    G = None
    for x in range(1, 1000):
        rhs = (x**3 + a*x + b) % p
        y = pow(rhs, (p + 1)//4, p)
        if (y*y) % p == rhs:
            G = Point(curve, x, y)
            break
    if G is None:
        print(f"❌ не найдена точка G для b={b}")
        continue

    # генерируем P_inv = (N//l) * G для каждого малого l
    for l in ls:
        if l <= threshold:
            P_inv = (N // l) * G
            results.append((b, l, (P_inv.x(), P_inv.y())))

# вывод
for b, l, (x, y) in results:
    print(f"b={b}, l={l}, P_inv=({x}, {y})")
