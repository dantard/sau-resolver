#!/usr/bin/python3

import sys
import numbers



import numpy as np
from matplotlib import pyplot as plt
import control as co
import sympy as sp
import math
from sympy import *
import builtins as __builtin__
verbose = True
blocking = True

import matplotlib
matplotlib.use('TkAgg')

def set_verbose(val):
    global verbose
    verbose = val


def set_blocking(val):
    global blocking
    blocking = val


def print(*args, **kwargs):
    if verbose:
        __builtin__.print(*args, **kwargs)


def text_to_tf(fdt):
    expr = sp.parse_expr(fdt.replace("^", "**"))
    num = expr.as_numer_denom()[0]
    den = expr.as_numer_denom()[1]
    num = float(num) if num.is_Number else [float(x) for x in sp.poly(num).all_coeffs()]
    den = float(den) if den.is_Number else [float(x) for x in sp.poly(den).all_coeffs()]
    return co.tf(num, den)


def asynt(poly):
    poly = poly.replace("^", "**")
    poly = sp.parse_expr(poly)
    num = poly.as_numer_denom()[0]
    den = poly.as_numer_denom()[1]

    num_roots = solve(num)
    den_roots = solve(den)

    numb_asynt = len(den_roots) - len(num_roots)

    print("Número de asíntotas: {:d}".format(numb_asynt))
    if numb_asynt > 0:
        sum = 0
        for i in num_roots:
            sum -= sp.re(i).evalf()
        for i in den_roots:
            sum += sp.re(i).evalf()
        poc = sum / numb_asynt
        print("Punto de contacto: s={:.3g}".format(poc))
        angles = []
        for i in range(numb_asynt):
            angles.append(180 * (2 * i + 1) / numb_asynt)
        print("Ángulos: {}".format(angles))
        return numb_asynt, poc, angles
    else:
        return 0, 0, 0


def valid_zone(ts, s_perc, tp, xmax, ymax, verb=True):
    if s_perc > 0:
        zeta = -math.log(s_perc / 100) / math.sqrt(math.pi * math.pi + math.log(s_perc / 100) * math.log(s_perc / 100))
        angle = math.acos(zeta)
    else:
        angle = 0
    zwn = 4 / ts if ts > 0 else 0
    wd = math.pi / tp if tp != 0 else 0

    ymax = max(ymax, wd + 5)

    plt.figure(1)
    plt.ion()
    axes = plt.gca()
    x1, x2 = axes.get_xlim()
    xmax = max(xmax, zwn + 5, -x1)

    if angle > 0:
        verb and print("S% <= {:.4g} %".format(s_perc))
        y_max_angle = xmax * math.tan(angle)
        x_cross_wd = math.fabs(wd) / math.tan(angle)
        xmax = max(xmax, x_cross_wd + 5)
        ymax = max(ymax, y_max_angle + 5)

        if zwn > 0:
            verb and print("Ts <= {:.4g} s".format(ts))
            y_zwn = zwn * math.tan(angle)
            if wd >= 0:
                verb and print("Tp >= {:.4g} s".format(tp))
                if wd == 0 or wd > y_max_angle or x_cross_wd > xmax:
                    plt.fill_between([-zwn, -xmax], [-y_zwn, -y_max_angle], [y_zwn, y_max_angle], alpha=0.5)
                else:
                    if x_cross_wd < zwn:
                        plt.fill_between([-zwn, -xmax], [-wd, -wd], [wd, wd], alpha=0.5)
                    else:
                        plt.fill_between([-zwn, -x_cross_wd, -xmax], [-y_zwn, -wd, -wd], [y_zwn, wd, wd], alpha=0.5)
            else:
                verb and print("Tp <= {:.4g} s".format(-tp))
                wd = -wd
                if wd > y_max_angle or x_cross_wd > xmax:
                    pass
                elif x_cross_wd > zwn:
                    plt.fill_between([-x_cross_wd, -xmax], [wd, wd], [wd, y_max_angle], alpha=0.5)
                    plt.fill_between([-x_cross_wd, -xmax], [-wd, -wd], [-wd, -y_max_angle], alpha=0.5)
                else:
                    plt.fill_between([-zwn, -xmax], [wd, wd], [y_zwn, y_max_angle], alpha=0.5)
                    plt.fill_between([-zwn, -xmax], [-wd, -wd], [-y_zwn, -y_max_angle], alpha=0.5)
        else:
            if wd > 0:
                verb and print("Tp >= {:.4g} s".format(-tp))
                if x_cross_wd > xmax:
                    plt.fill_between([0, -xmax], [0, y_max_angle], [0, -y_max_angle], alpha=0.5)
                else:
                    plt.fill_between([0, -x_cross_wd, -xmax], [0, wd, wd], [0, -wd, -wd], alpha=0.5)
            else:
                verb and print("Tp <= {:.4g} s".format(-tp))
                wd = -wd
                if x_cross_wd > xmax:
                    pass
                else:
                    plt.fill_between([-x_cross_wd, -xmax], [wd, wd], [wd, y_max_angle], alpha=0.5)
                    plt.fill_between([-x_cross_wd, -xmax], [-wd, -wd], [-wd, -y_max_angle], alpha=0.5)
    else:  # angle == 0
        if zwn >= 0:
            verb and print("Ts <= {:.4g} s".format(ts))
            if wd > 0:
                verb and print("Tp >= {:.4g} s".format(tp))
                plt.fill_between([-zwn, -xmax], [wd, wd], [-wd, -wd], alpha=0.5)
            else:
                verb and print("Tp <= {:.4g} s".format(tp))
                wd = -wd
                plt.fill_between([-zwn, -xmax], [wd, wd], [ymax, ymax], alpha=0.5)
                plt.fill_between([-zwn, -xmax], [-wd, -wd], [-ymax, -ymax], alpha=0.5)
        else:
            pass

    if True:
        if angle > 0:
            plt.plot([0, -xmax], [0, xmax * math.tan(angle)])
            plt.plot([0, -xmax], [0, -xmax * math.tan(angle)])
        if zwn > 0:
            plt.plot([-zwn, -zwn], [-ymax, ymax])
        if wd < 20:
            plt.plot([0, -xmax], [wd, wd])
            plt.plot([0, -xmax], [-wd, -wd])

    plt.show(block=blocking)


def rupture_points(poly, verb=True):
    poly = sp.parse_expr(poly.replace("^", "**"))
    num = poly.as_numer_denom()[0]
    den = poly.as_numer_denom()[1]

    num_roots = solve(num)
    den_roots = solve(den)
    real_parts = []

    for r in num_roots:
        real_parts.append(sp.re(r).evalf())
    for r in den_roots:
        real_parts.append(sp.re(r).evalf())

    real_parts.sort()
    f = num * diff(den) - diff(num) * den

    verb and print("N'D - ND' = 0  =>  {} = 0".format(str(simplify(f)).replace("**", "^")))
    raices = solve(simplify(f))
    verb and print("Raíces -> {}".format([r.evalf(3) for r in raices]))
    valid = []
    for r in raices:
        # si es una raíz real
        if math.fabs(sp.im(r).evalf()) < 1e-10:
            # may have a very small imaginary part

            count = 0
            for i in real_parts:
                if i > sp.re(r).evalf():
                    count += 1

            if count % 2 == 0:
                verb and print("Punto de ruptura en s={:.3g} NO válido".format(sp.re(r).evalf()))
            else:
                verb and print("Punto de ruptura en s={:.3g} válido".format(sp.re(r).evalf()))
                valid.append(r.evalf())
        else:
            print("Punto de ruptura en s={} NO válido".format(r.evalf(3)))

    return raices


def routh(polinomio):
    from tbcontrol.symbolic import routh
    from sympy.solvers.inequalities import solve_rational_inequalities

    if "/" in polinomio:
        polinomio = polinomio.split("/")[1]

    s = sp.Symbol('s')
    k = sp.Symbol('k')
    K = sp.Symbol('K')
    p = sp.Poly(polinomio.replace("^", "**"), s)
    init_printing()
    print("La tabla de Routh es para el polinomio " + polinomio + " es:\n")
    table = routh(p)
    pprint(table)

    res = []
    changes = -1
    if 'K' in polinomio:
        print("\nEstabilidad:")
        polys = []
        for i in range(table.rows):
            val = table[i, 0]
            if not val.is_Number:
                polys.append(val.as_numer_denom()[0].as_poly())

        j = 1
        query = []
        for i in polys:
            ineq = (i, Poly(1, K),)
            all = (ineq, ">")
            query.append(all)
            res = solve_rational_inequalities([[all]])
            txt = pretty(res)
            print("Para inecuación ({}):\n".format(j))
            pprint(i.as_expr())
            print("")
            print("intervalo:\n")
            pprint(res)
            print("\n")
            j = j + 1

        res = solve_rational_inequalities([query])
        print("Globalmente el sistema es estable para K en intervalo:\n")
        pprint(res)
    else:
        changes = 0
        last_sign = table[0, 0]
        for i in range(table.rows):
            val = table[i, 0]
            if last_sign > 0 and val < 0 or last_sign < 0 and val > 0:
                changes = changes + 1
                last_sign = val

        if changes == 0:
            print("\nEl sistema es estable")
        else:
            print(
                "\nEl sistema es inestable, tiene {:d} polo/s en el s/p derecho y {:d} en s/p izquierdo".format(changes,
                                                                                                                table.rows - 1 - changes))
        return table, res, changes


def compute_controller(planta, s_star, cero=None):
    if cero is not None and cero != "0":
        print("Calculando una RED DE ADELANTO (RA) con cero en s={}".format(cero))
        planta = "(s-{})*(".format(cero) + planta + ")"
        is_pd = False
    else:
        print("Calculando un PROPORCIONAL DERIVATIVO (PD)")
        is_pd = True

    print("")

    looking_for = "cero" if is_pd else "polo"

    expr = sp.parse_expr(planta.replace("^", "**"))
    num = expr.as_numer_denom()[0]
    den = expr.as_numer_denom()[1]
    num = [float(num)] if num.is_Number else [float(x) for x in sp.poly(num).all_coeffs()]
    den = [float(den)] if den.is_Number else [float(x) for x in sp.poly(den).all_coeffs()]

    tf_ctrl = co.tf(num, den)
    poles = co.poles(tf_ctrl)
    zeros = co.zeros(tf_ctrl)
    mu = co.dcgain(tf_ctrl)

    for i in poles:
        mu = -mu * i
    for i in zeros:
        mu = -mu / i

    s_star = complex(s_star)

    angle_poles = 0
    mod_poles = 1
    for i in poles:
        angle = math.atan2(s_star.imag, s_star.real - i) * 180 / math.pi
        mod = abs(s_star - i)
        print("Polo en {:.2f} tiene ángulo {:.2f} grados con s* y módulo {:.2f}".format(i, angle, mod))
        angle_poles += angle
        mod_poles = mod_poles * mod

    angle_zeros = 0
    mod_zeros = 1
    for i in zeros:
        angle = math.atan2(s_star.imag, s_star.real - i) * 180 / math.pi
        mod = abs(s_star - i)
        print("Cero en {:.2f} tiene ángulo {:.2f} grados con s* y módulo {:.2f}".format(i, angle, mod))
        angle_zeros += angle
        mod_zeros = mod_zeros * mod

    needed = (-180 - angle_zeros + angle_poles)
    print("")
    print("Falta fase de {:.2f} grados".format(needed))
    print("")

    impossible = (is_pd and (needed > 180 or needed < 0)) or \
                 (not is_pd and (needed < -180 or needed > 0))

    if impossible:
        print("ERROR: Imposible encontrar " + looking_for)
    else:
        needed = math.fabs(needed)
        if needed > 90:
            delta_x = -s_star.imag / math.tan(math.pi * (180 - needed) / 180)
        else:
            delta_x = s_star.imag / math.tan(math.pi * needed / 180)

        sing_pos = s_star.real - delta_x

        if is_pd:
            gain = mod_poles / mod_zeros / abs(s_star - sing_pos) / mu
            ctrl = gain * co.tf([1, -sing_pos], [1])
        else:
            gain = mod_poles * abs(s_star - sing_pos) / mod_zeros / mu
            ctrl = gain * co.tf([1, -float(cero)], [1, -sing_pos])

        # gain = gain /dcgain

        print("La posición del " + looking_for + " es {:.2f} y la ganancia {:.2f}".format(sing_pos, gain))
        print("")
        print("C(s)=\n{}".format(ctrl))
    # return ctrl


def step_response(fdt, verb=True):
    plt.figure()
    tf_ctrl = text_to_tf(fdt)
    t, y = co.step_response(tf_ctrl)

    def find_time_index_by_val(val):
        for i in range(len(t)):
            if (y[i] > val):
                return i

    def find_time_index_by_time(val):
        for i in range(len(t)):
            if (t[i] > val):
                return i

    if len(tf_ctrl.num[0][0]) == 1:

        plt.plot([0, t[-1]], [tf_ctrl.dcgain(), tf_ctrl.dcgain()], 'g')
        plt.text(0, tf_ctrl.dcgain() * 1.01, "mu: {:.2f}".format(tf_ctrl.dcgain()))
        verb and print("mu: {:.4g}".format(tf_ctrl.dcgain()))

        if len(tf_ctrl.den[0][0]) == 2:
            # Primer orden
            tau = tf_ctrl.den[0][0][1] / tf_ctrl.den[0][0][0]
            i = find_time_index_by_time(3 * tau)
            plt.plot([t[i], t[i]], [0, y[i]], 'k')

            i = find_time_index_by_val(0.1 * tf_ctrl.dcgain())
            plt.plot([t[i], t[i]], [0, y[i]], 'k')
            i = find_time_index_by_val(0.9 * tf_ctrl.dcgain())
            plt.plot([t[i], t[i]], [0, y[i]], 'k')

        if len(tf_ctrl.den[0][0]) == 3:
            # Primer orden
            zwn = (tf_ctrl.den[0][0][1] / tf_ctrl.den[0][0][2]) / 2
            wn = math.sqrt(tf_ctrl.den[0][0][0] / tf_ctrl.den[0][0][2])
            z = zwn / wn
            wd = wn * sqrt(1 - z ** 2)

            i = find_time_index_by_time(4 / zwn)
            plt.plot([t[i], t[i]], [0, y[i]], 'r')
            plt.text(t[i] * 1.01, 0, "Ts98%: {:.2f}s".format(t[i]))
            verb and print("Ts98%: {:.4g}".format(t[i]))

            tp = math.pi / wd
            i = find_time_index_by_time(tp)
            plt.plot([t[i], t[i]], [0, y[i]], 'y')
            plt.plot([0, t[i]], [y[i], y[i]], 'y')
            plt.text(t[i], y[i] * 1.01, "S%: {:.2f}%".format((y[i] - tf_ctrl.dcgain()) / tf_ctrl.dcgain() * 100))
            plt.text(t[i] * 1.01, 0, "Tp: {:.2f}s".format(tp))

            verb and print("S%: {:.4g}".format((y[i] - tf_ctrl.dcgain()) / tf_ctrl.dcgain() * 100))
            verb and print("Tp: {:.4g}".format(tp))

    plt.plot(t, y)
    plt.show(block=blocking)


def root_locus_angles(fdt):
    tf_ctrl = text_to_tf(fdt)
    poles = co.poles(tf_ctrl)
    zeros = co.zeros(tf_ctrl)
    there_are_angles = False
    for p in poles:
        if p.imag != 0:
            angle = math.pi
            for q in poles:
                angle -= math.atan2(p.imag - q.imag, p.real - q.real)
            for z in zeros:
                angle += math.atan2(p.imag - z.imag, p.real - z.real)
            print("Polo en s={:.2f}".format(p), "ángulo: {:.2f} grados".format(angle / math.pi * 180))
            there_are_angles = True

    there_are_angles and print("")

    for p in zeros:
        if p.imag != 0:
            angle = math.pi
            for q in poles:
                angle += math.atan2(p.imag - q.imag, p.real - q.real)
            for z in zeros:
                angle -= math.atan2(p.imag - z.imag, p.real - z.real)
            print("Cero en s={:.2f}".format(p), "ángulo: {:.2f} grados".format(angle / math.pi * 180))
            there_are_angles = True

    if not there_are_angles:
        print("No hay polos o ceros con parte imaginaria no nula")


def dc_gain_any_type(fdt):
    num = fdt.num[0][0]
    den = fdt.den[0][0]

    fdt_type = 0

    while num[len(num) - 1] == 0:
        num = num[0:-1]

    while den[len(den) - 1] == 0:
        den = den[0:-1]

    gain = num[len(num) - 1] / den[len(den) - 1]
    return gain


def compensate_error(fdt, obj=None, pole=None, s_star=None, verbose=True):
    #    def print(*args, **kwargs):
    #        if verbose:
    #            __builtin__.print(*args, **kwargs)
    print("Situación actual: ", end="")
    fdt = text_to_tf(fdt)
    num = fdt.num[0][0]
    den = fdt.den[0][0]

    fdt_type = 0
    while den[len(den) - 1] == 0:
        fdt_type += 1
        den = den[0:-1]
    gain = num[len(num) - 1] / den[len(den) - 1]
    if fdt_type == 0:
        error = 1 / (1 + gain)
        print("e_step(oo)={:.2g}".format(error))
    elif fdt_type == 1:
        error = 1 / gain
        print("e_step(oo)=0, e_ramp(oo)={:.2g}".format(error))
    elif fdt_type == 2:
        error = 1 / gain
        print("e_step(oo)=0, e_ramp(oo)=0, e_parab(oo)={:.2g}".format(error))
    print("")
    if obj is not None:
        obj = float(obj)

        if pole is None:
            print("Calculando PROPORCIONAL INTEGRAL (PI)")
            if fdt_type == 0:
                print("- Anulando e_step(oo)")
                print("- Acotando e_ramp(oo) a {:.2g}".format(obj))
            if fdt_type == 1:
                print("- Anulando e_ramp(oo)")
                print("- Acotando e_parab(oo) a {:.2g}".format(obj))

            z = 1 / gain / obj
            ctrl = co.tf([1, z], [1, 0])
        else:
            pole = -float(pole)
            print("Calculando RED de RETARDO (RR)")
            if fdt_type == 0:
                z = (pole - obj * pole) / obj / gain
                print("- Acotando e_step(oo) a {:.2g}".format(obj))
            elif fdt_type == 1:
                print("- Acotando e_ramp(oo) a {:.2g}".format(obj))
                z = pole / gain / obj
            elif fdt_type == 2:
                print("- Acotando e_parab(oo) a {:.2g}".format(obj))
                z = pole / gain / obj

            ctrl = co.tf([1, z], [1, pole])
            print("")
            print("Posición del polo: s={:.2g}".format(-pole))

        print("")
        print("Posición del cero: s={:.2g}".format(-z))
        print("")

    k_c = 1
    if s_star is not None:
        s_star = complex(s_star)
        if pole is None:
            k_c = abs(s_star) / abs(s_star + z)
        else:
            k_c = abs(s_star + pole) / abs(s_star + z)
        print("K_adj = {:.5g}".format(k_c))
        print("")
    print("C(s)=\n{}".format(k_c * ctrl))

    return ctrl


from multiprocessing import Process


def root_locus(fdt, limit=0, asynt=None):
    plt.figure(1)
    tf_ctrl = text_to_tf(fdt)

    # a contains a list of lists. ej 4 poles: [ [3,4,-4+4j,5],[...]]
    rows, b = co.root_locus(tf_ctrl, plot=False)
    colors = ['red', 'green', 'blue', 'yellow', 'black']
    prev = []
    num_roots = len(rows[0])

    # Draw Asyntotes before anything else
    if asynt is not None:
        num = asynt[0]
        poc = asynt[1]
        xmax = -1e6
        ymax = -1e6

        # Compute limits
        idx = 0
        for row in rows:
            for pole in row:
                xmax = pole.real if pole.real > xmax else xmax
                ymax = pole.imag if pole.imag > ymax else ymax

            if limit > 0 and b[idx] > limit:
                break
            else:
                idx = idx + 1

        length = 1.5 * math.sqrt(xmax ** 2 + ymax ** 2)
        angle_inc = 360 / num
        angle = angle_inc / 2
        for i in range(0, num):
            plt.plot([poc, poc + length * math.cos(angle * math.pi / 180)],
                     [0, length * math.sin(angle * math.pi / 180)], color=(0.6, 0.6, 0.6))
            angle = angle + angle_inc

    # prev contains the previous point for any rama
    for i in range(num_roots):
        prev.append((0 + 0j))

    current_row = 0
    for row in rows:
        cnt = 0
        for val in row:
            if current_row > 0:
                plt.plot([prev[cnt].real, val.real], [prev[cnt].imag, val.imag], color=colors[cnt])
            prev[cnt] = val
            cnt = (cnt + 1) % num_roots

        if limit > 0 and b[current_row] > limit:
            break
        else:
            current_row = current_row + 1

    rows = co.poles(tf_ctrl)
    real_part = []
    imag_part = []
    for pol in rows:
        plt.scatter(pol.real, pol.imag, marker="x", color='red')
        real_part.append(pol.real)
        imag_part.append(pol.imag)

    rows = co.zeros(tf_ctrl)
    for zer in rows:
        plt.scatter(zer.real, zer.imag, marker="o", color='green', facecolors='none')

    plt.show(block=blocking)


def solve_equation_system(inp, vars, eqs):
    x = []
    eq = []
    inp = Symbol(inp)

    for i in eqs:
        i = i.replace(" ", "")
        if not i.endswith("=0"):
            print("*** ATENCIÓN: eq. {} no termina con '=0'".format(i))
        eq.append(i.replace("=0", "").replace("I", "_i_"))

    if len(vars) != len(eq):
        print("*** ERROR: Número de variables distinto de número de ecuaciones")
    else:
        for i in vars:
            i = i.replace("I", "_i_")
            x.append(Symbol(i))
    results = solve(eq, x)
    init_printing()

    resu = [(k, v) for k, v in results.items()]
    for i in resu:
        k, v = i
        pprint("{}(s)/{}(s)=".format(str(k).replace("_i_", "I"), inp))
        pprint(simplify(v) / inp)
        print("")
        print("")
        print("")


class Singularity:
    def __init__(self, type, val):
        self.type = type
        self.val = val
        self.m = []
        self.v = []

    def append_m(self, v):
        self.m.append(v)

    def append_v(self, v):
        self.v.append(v)


def print_table(module, m_important_freq):
    module.sort(key=lambda x: x.val)
    print("     ", end="")
    #    print(m_important_freq)
    for i in m_important_freq:
        print("{:10g}".format(i), end="")
    print("")
    for k in range(len(m_important_freq) * 10 + 5):
        print("-", end="")
    print("")

    for i in module:
        if i.type != -1:
            print("s={:5g}".format(-i.val), end="")
        else:
            for k in range(len(m_important_freq) * 10 + 5):
                print("-", end="")

            print("\nSuma   ", end="")
        print("       ", end="")
        for j in i.m[:-1]:
            print("|  {:4g}   ".format(j), end="")
        print("|")
    print("")


#    print("     ", end ="")


# f="27*(s+3)/(s+1)/(s+20)/s"
def asbode(f, **kwargs):
    fdt = text_to_tf(f)

    zeros = [-z.real for z in fdt.zeros()]
    poles = [-p.real for p in fdt.poles()]

    zeros.sort()
    poles.sort()

    sing = [z for z in zeros if z != 0] + [p for p in poles if p != 0]
    sing.sort()

    if len(sing) > 0:
        min = sing[0] / 10
        max = sing[-1] * 10
    else:
        min = 0.1
        max = 100

    max_pwr = None
    min_pwr = None

    for pwr in range(-6, 6):
        if max == math.pow(10, pwr):
            max_pwr = pwr + 1
            break
        elif max < math.pow(10, pwr):
            max_pwr = pwr
            break

    for pwr in range(-6, 6):
        if min == math.pow(10, pwr):
            min_pwr = pwr - 1
            break
        elif min < math.pow(10, pwr):
            min_pwr = pwr - 1
            break

    min = pow(10, min_pwr)
    max = pow(10, max_pwr)

    m_important_freq = [min, max]
    p_important_freq = [min, max]

    for z in zeros:
        if z != 0:
            m_important_freq.append(z)
            p_important_freq.append(z / 10)
            p_important_freq.append(z * 10)

    for p in poles:
        if p != 0:
            m_important_freq.append(p)
            p_important_freq.append(p / 10)
            p_important_freq.append(p * 10)

    m_important_freq = list(set(m_important_freq))
    p_important_freq = list(set(p_important_freq))
    m_important_freq.sort()
    p_important_freq.sort()


    all = []
    mallv = []
    module = []
    for cut in poles:
        p = Singularity(0, cut)
        for freq in m_important_freq:
            if cut == 0:
                p.append_m(-20)
                p.append_v(20 * math.log10(1 / freq))
            elif freq >= cut:
                p.append_m(-20)
                p.append_v(-20 * math.log10(freq / cut))
            else:
                p.append_m(0)
                p.append_v(0)

        module.append(p)
        all.append(p.m)
        mallv.append(p.v)

    for cut in zeros:
        z = Singularity(1, cut)
        for freq in m_important_freq:
            if cut == 0:
                z.append_m(20)
                z.append_v(20 * math.log10(freq))
            elif freq >= cut:
                z.append_m(20)
                z.append_v(20 * math.log10(freq / cut))
            else:
                z.append_m(0)
                z.append_v(0)
        module.append(z)
        all.append(z.m)
        mallv.append(z.v)

    res = Singularity(-1, 1e6)
    res.m = [sum(i) for i in zip(*all)]
    module.append(res)

    verbose = kwargs.get('tables', False)

    verbose and print("TABLA de GANANCIAS\n")

    verbose and print_table(module, m_important_freq)

    phase = []

    all = []
    allv = []
    for cut in poles:
        s = Singularity(0, cut)
        for freq in p_important_freq:
            if cut == 0:
                s.append_m(0)
                s.append_v(-90)
            elif freq >= 0.099999 * cut and freq < 10 * cut:
                s.append_m(-45)
                s.append_v(-45 * math.log10(freq / cut) - 45)
            elif freq >= 10 * cut:
                s.append_m(0)
                s.append_v(-90)
            else:
                s.append_m(0)
                s.append_v(0)
        phase.append(s)
        all.append(s.m)
        allv.append(s.v)

    for cut in zeros:
        s = Singularity(1, cut)
        for freq in p_important_freq:
            if cut == 0:
                s.append_m(0)
                s.append_v(90)
            elif freq >= 0.099999 * cut and freq < 10 * cut:
                s.append_m(+45)
                s.append_v(+45 * math.log10(freq / cut) + 45)
            elif freq >= 10 * cut:
                s.append_m(0)
                s.append_v(90)
            else:
                s.append_m(0)
                s.append_v(0)
        phase.append(s)
        all.append(s.m)
        allv.append(s.v)

    res = Singularity(-1, 1e6)
    res.m = [sum(i) for i in zip(*all)]
    phase.append(res)

    verbose and print("TABLA de FASE\n")

    verbose and print_table(phase, p_important_freq)

    gain = 20 * math.log10(dc_gain_any_type(fdt))
    resm = [sum(i) + gain for i in zip(*mallv)]
    resp = [sum(i) for i in zip(*allv)]

    verbose and print("Ganancia inicial          : {:.4g} dB".format(resm[0]))
    verbose and print("Fase inicial              : {:.4g} grados".format(resp[0]))

    num_crosses = 0
    for i in range(len(resm) - 1):
        if resm[i] == 0:
            wc = m_important_freq[i]
            num_crosses += 1
        elif resm[i] > 0 and resm[i + 1] < 0:
            x0 = math.log10(m_important_freq[i])
            m = module[-1].m[i]
            F0 = resm[i]
            wc_dec = (m * x0 - F0) / m
            wc = math.pow(10, wc_dec)
            num_crosses += 1

    fase = None
    if num_crosses == 1:
        for i in range(len(p_important_freq) - 1):
            if wc == p_important_freq[i]:
                phase_at_wc = resp[i]
            elif wc > p_important_freq[i] and wc < p_important_freq[i + 1]:
                fase = (resp[i + 1] - resp[i]) * math.log10(wc / p_important_freq[i]) / math.log10(
                    p_important_freq[i + 1] / p_important_freq[i]) + resp[i]

                #verbose and print("Margen de fase (asymp): {:-4g} grados a {:-4g} rad/s".format(fase + 180, wc))
    else:
        verbose and print("\nMÚLTIPLES CRUCES con 0dB")

    gain_margin, phase_margin, gain_freq, phase_freq = co.margin(fdt)
    if not math.isinf(gain_margin):
        verbose and print("Margen de ganancia (bode) : {:.4g} dB a {:.4g} rad/s".format(20*math.log10(gain_margin), gain_freq))

    if not math.isinf(phase_margin):
        verbose and print("Margen de fase (bode)     : {:.4g}º   a {:.4g} rad/s".format(phase_margin, phase_freq))

    if kwargs.get('bode', False) or kwargs.get('asymp', False):
        plt.figure()
        w = np.logspace(min_pwr, max_pwr, 1000)

        margins = kwargs.get("margins")
        if kwargs.get("only") is not None:
            plp = kwargs.get("only") == "phase"
            plm = kwargs.get("only") == "mag"
        else:
            plp, plm = True, True



        #co.bode_plot(fdt, w, dB=True, omega_limits=(10**min_pwr, 10**max_pwr), display_margins=margins, plot_magnitude=plm, plot_phase=plp)
        #plt.show()

        mag, phase, omega = co.frequency_response(fdt, w, )
        phase =  np.unwrap(phase)
        #plt.figure()

        # Plot magnitude
        plt.subplot(2, 1, 1)  # 2 rows, 1 column, first subplot
        plt.semilogx(omega, 20 * np.log10(mag))  # Convert magnitude to dB
        plt.grid(True)

        # Plot phase
        plt.subplot(2, 1, 2)  # 2 rows, 1 column, second subplot
        plt.semilogx(omega, phase*180/math.pi)  # Phase in degrees
        plt.grid(True)

        plt.tight_layout()  # Adjusts layout so plots don't overlap


        if plm:
            ax1 = plt.gcf().get_axes()[0]
            ax1.set_xlim(10 ** min_pwr, 10 ** max_pwr)
            lines1 = ax1.get_lines()
            ax1.yaxis.grid(which="major", visible=True)
            ax1.xaxis.grid(which="minor", visible=True)
            ylim = ax1.get_ylim()
            ylim_max = ylim[1] if kwargs.get("mmax", None) is None else kwargs.get("mmax", 0)
            ylim_min = ylim[0] if kwargs.get("mmin", None) is None else kwargs.get("mmin", 0)
            ul = math.ceil(ylim_max / 20.0) * 20
            ll = math.floor(ylim_min / 20.0) * 20
            ax1.set_ylim(ll, ul)
            ax1.set_yticks(np.arange(ll, ul+1, 20))
            ax1.yaxis.grid(which="minor", visible=False)
            ax1.yaxis.set_minor_locator(plt.MultipleLocator(10))  # Minor ticks for phase

            if kwargs.get("noy1ticks", False):
                ax1.set_yticklabels([])

            if not kwargs.get('bode', False) or kwargs.get('exclude') == 'mag':
                lines1[0].set_visible(False)

            if kwargs.get("asymp") and not kwargs.get('exclude') == 'mag':
                plt.sca(ax1)
                plt.plot(m_important_freq, resm, 'k')

            ax1.set_ylabel(kwargs.get('ylabel1', ''))
            if plp:
                ax1.set_xticklabels([])
                plt.subplots_adjust(hspace=0.1)  # Reduce vertical space (default is 0.3)

            if kwargs.get("margins"):
                if not math.isinf(gain_margin):
                    plt.sca(ax1)
                    plt.plot([gain_freq, gain_freq], [0, -20*math.log10(gain_margin)], color='green' if gain_margin > 0 else 'red')

        if plp:
            ax2 = plt.gcf().get_axes()[1]
            ax2.set_xlim(10 ** min_pwr, 10 ** max_pwr)
            lines2 = ax2.get_lines()
            ax2.yaxis.grid(which="major", visible=True)
            ax2.xaxis.grid(which="minor", visible=True)

            ylim = ax2.get_ylim()
            ylim_max = ylim[1] if kwargs.get("pmax", None) is None else kwargs.get("pmax", 0)
            ylim_min = ylim[0] if kwargs.get("pmin", None) is None else kwargs.get("pmin", 0)
            ul = math.ceil(ylim_max / 45.0) * 45
            ll = math.floor(ylim_min / 45.0) * 45
            ax2.set_ylim(ll, ul)
            ax2.set_yticks(np.arange(ll, ul+1, 45))
            ax2.yaxis.grid(which="minor", visible=False)
            ax2.yaxis.set_minor_locator(plt.MultipleLocator(15))  # Minor ticks for phase

            if kwargs.get("noxticks", False):
                ax2.set_xticklabels([])

            if kwargs.get("noy2ticks", False):
                ax2.set_yticklabels([])

            if not kwargs.get('bode', False) or kwargs.get('exclude') == 'phase':
                lines2[0].set_visible(False)

            if kwargs.get("asymp") and not kwargs.get('exclude') == 'phase':
                plt.sca(ax2)
                plt.plot(p_important_freq, resp, 'k')

            if kwargs.get("margins"):
                if not math.isinf(phase_margin):
                    plt.sca(ax2)
                    plt.plot([phase_freq, phase_freq], [-180, -180 + phase_margin], color='green' if phase_margin > 0 else 'red')

            ax2.set_xlabel(kwargs.get('xlabel', ''))
            ax2.set_ylabel(kwargs.get('ylabel2', ''))

        plt.gcf().suptitle(kwargs.get('title', ''))

        if kwargs.get('save', False):
            plt.savefig(kwargs.get('save'))

        if not kwargs.get("batch"):
            plt.show()

def roots(poly):
    poly = sp.parse_expr(poly.replace("^", "**").replace("=0", "").replace("j","I").replace("i","I"))
    raices = solve(poly)
    print("Polinomio:", str(simplify(poly)).replace("**", "^").replace("I","j"))
    print("\nRaíces:")
    for r in raices:
        # si es una raíz real
        if r.is_real:
            print(" s=", r.evalf())
        else:
            print(" s=", str(complex(r)))


def tf_to_text(tf):
    def n2str(i):
        if i == int(i):
            return "{:d}".format(int(i))
        else:
            return "{:.3}".format(float(i))

    def do(polynomial):
        text_string = ""
        if len(polynomial) > 1: text_string = "("
        expo = len(polynomial) - 1
        for i in polynomial:
            if i == 0:
                pass
            elif i == 1 and expo == 1:
                text_string = text_string + "s"
            elif expo == 1:
                text_string = text_string + n2str(i) + "*s"
            elif i == 1 and expo > 1:
                text_string = text_string + "s^" + n2str(expo)
            elif i > 0 and expo == 0:
                text_string = text_string + n2str(i)
            else:
                text_string = text_string + n2str(i) + "*s^" + n2str(expo)
            expo = expo - 1
            if i > 0: text_string = text_string + "+"
        text_string = text_string[0:-1]
        if len(polynomial) > 1: text_string += ")"
        return text_string

    if isinstance(tf, numbers.Number):
        return str(tf)

    num = do(tf.num[0][0])
    den = do(tf.den[0][0])

    if den != "1":
        return "" + num + "/" + den
    else:
        return num
