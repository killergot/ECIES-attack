from sage.all import *

p = 211
F = GF(p)

min_divisors = 5   # сколько простых делителей минимально
found = []

for a in F:
    for b in F:
        try:
            E = EllipticCurve(F, [a, b])
            if not E.is_smooth():
                continue
            n = E.order()
            prime_divs = list(factor(n))
            if len(prime_divs) >= min_divisors:
                print(f"Кривая: y^2 = x^3 + {a}x + {b} над GF({p})")
                print(f"Порядок: {n} = {factor(n)}")
                found.append((E, n))
        except (ArithmeticError, ZeroDivisionError):
            continue