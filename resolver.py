#!/usr/bin/python3

import sys

from matplotlib import pyplot as plt
import control as co
import sympy as sp
import math
from sympy import *


def text_to_tf(fdt):
    expr = sp.parse_expr(fdt.replace("^", "**"))
    num = expr.as_numer_denom()[0]
    den = expr.as_numer_denom()[1]
    num = float(num) if num.is_Number else [float(x) for x in sp.poly(num).all_coeffs()]
    den = float(den) if den.is_Number else [float(x) for x in sp.poly(den).all_coeffs()]
    return co.tf(num, den)


def asynt(poly):
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
        poc = sum/numb_asynt
        print("Punto de contacto: s={:.3g}".format(poc))
        print("Ángulo/s: ", end="")
        for i in range(numb_asynt):
            print(180*(2*i+1)/numb_asynt, "",end="")
        print("")


def rupture_points(poly):
    poly=sp.parse_expr(poly)
    num=poly.as_numer_denom()[0]
    den = poly.as_numer_denom()[1]

    num_roots = solve(num)
    den_roots = solve(den)
    real_parts = []

    for r in num_roots:
        real_parts.append(sp.re(r).evalf())
    for r in den_roots:
        real_parts.append(sp.re(r).evalf())

    real_parts.sort()
    f = num*diff(den) - diff(num)*den
    print("N'D - ND' = 0 -> {} ".format(f))
    r = solve(f)
    print("Raíces -> {} -> {}".format(r, [i.evalf() for i in r]))
    for v in r:
        if sp.im(v).evalf() == 0:
            count = len([i for i in real_parts if i > v.evalf()])
            if count %2 == 0:
                print("Punto de ruptura en s={:.3g} NO válido".format(v.evalf()))
            else:
                print("Punto de ruptura en s={:.3g} válido".format(v.evalf()))

    return r


def routh(polinomio):
    from tbcontrol.symbolic import routh
    from sympy.solvers.inequalities import solve_rational_inequalities

    s = sp.Symbol('s')
    k = sp.Symbol('k')
    K = sp.Symbol('K')
    p = sp.Poly(polinomio.replace("^", "**"), s)
    init_printing()
    print("La tabla de Routh es para el polinomio " + polinomio + " es:\n")
    table = routh(p)
    pprint(table)

    if 'K' in polinomio:
        print("\nEstabilidad:")
        polys = []
        for i in range(table.rows):
            val = table[i, 0]
            if not val.is_Number:
                polys.append(val.as_numer_denom()[0].as_poly())

        query = []
        for i in polys:
            ineq = (i, Poly(1, K),)
            all = (ineq, ">")
            query.append(all)
            res = solve_rational_inequalities([[all]])
            txt = pretty(res)
            print("* Para inecuación [" + pretty(i.as_expr()) + " > 0], intervalo", pretty(res))

        res = solve_rational_inequalities([query])
        print("** Sistema estable para K en intervalo:", pretty(res))
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


def compute_controller(planta, s_star, cero):
    if (cero != ""):
        print("Calculando una RED DE ADELANTO (RA) con cero en s={}".format(cero))
        planta = "(s-{})*(".format(cero) + planta + ")"
        is_pd = False
    else:
        print("Calculando un PROPORCIONAL DERIVATIVO (PD)")
        is_pd = True

    print("---")

    looking_for = "cero" if is_pd else "polo"

    expr = sp.parse_expr(planta.replace("^", "**"))
    num = expr.as_numer_denom()[0]
    den = expr.as_numer_denom()[1]
    num = float(num) if num.is_Number else [float(x) for x in sp.poly(num).all_coeffs()]
    den = float(den) if den.is_Number else [float(x) for x in sp.poly(den).all_coeffs()]
    tf_ctrl = co.tf(num, den)
    poles = co.pole(tf_ctrl)
    zeros = co.zero(tf_ctrl)
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
    print("---")
    print("Falta fase de {:.2f} grados".format(needed))
    print("---")

    impossible = (is_pd and (needed > 180 or needed < 0)) or \
                        (not is_pd and (needed < -180 or needed > 0))

    if impossible:
        print("ERROR: Imposible encontrar " + looking_for)
    else:
        needed = math.fabs(needed)
        if needed > 90:
            delta_x = s_star.imag / math.tan(math.pi * (180 - needed) / 180)
        else:
            delta_x = s_star.imag / math.tan(math.pi * needed / 180)

        sing_pos = s_star.real - delta_x

        if is_pd:
            gain = mod_poles / mod_zeros / abs(s_star - sing_pos)
            ctrl = gain * co.tf([1, -sing_pos], [1])
        else:
            gain = mod_poles * abs(s_star - sing_pos) / mod_zeros
            ctrl = gain * co.tf([1, -float(cero)], [1, -sing_pos])

        print("La posición del " + looking_for + " es {:.2f} y la ganancia {:.2f}".format(sing_pos, gain))
        print("---")
        print("El controlador es: C(s)={}".format(ctrl))
    return ctrl


def step_response(fdt):
    tf_ctrl = text_to_tf(fdt)
    t, y = co.step_response(tf_ctrl)
    plt.plot(t, y)
    plt.show()


def root_locus_angles(fdt):
    tf_ctrl = text_to_tf(fdt)
    poles = co.pole(tf_ctrl)
    zeros = co.zero(tf_ctrl)
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

    there_are_angles and print("---")

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


def compensate_error(fdt, obj=None, pole=None, s_star=None):
    fdt = text_to_tf(fdt)
    num = fdt.num[0][0]
    den = fdt.den[0][0]
    print(fdt.den[0][0])
    fdt_type = 0
    while den[len(den)-1] == 0:
        fdt_type += 1
        den = den[0:-1]
    gain = num[len(num)-1]/den[len(den)-1]
    if fdt_type == 0:
        error = 1/(1+gain)
        print("e_step(oo)={:.2g}".format(error))
    elif fdt_type == 1:
        error = 1 / gain
        print("e_step(oo)=0, e_ramp(oo)={:.2g}".format(error))
    elif fdt_type == 2:
        error = 1 / gain
        print("e_step(oo)=0, e_ramp(oo)=0, e_parab(oo)={:.2g}".format(error))
    if obj is not None:
        obj = float(obj)

        if pole is None:
            print("** Calculando PROPORCIONAL INTEGRAL (PI)")
            if fdt_type == 0:
                print("Anulando e_step(oo)")
                print("Acotando e_ramp(oo) a {:.2g}".format(obj))
            if fdt_type == 1:
                print("Anulando e_ramp(oo)")
                print("Acotando e_parab(oo) a {:.2g}".format(obj))

            z = -1 / gain / obj
            ctrl = co.tf([1, -z], [1, 0])
        else:
            pole = -float(pole)
            print("** Calculando RED de RETARDO (RR)")
            if fdt_type == 0:
                z = -(pole-obj*pole)/obj/gain
                print("Acotando e_step(oo) a {:.2g}".format(obj))
            elif fdt_type == 1:
                print("Acotando e_ramp(oo) a {:.2g}".format(obj))
                z = -pole / gain / obj
            elif fdt_type == 2:
                print("Acotando e_parab(oo) a {:.2g}".format(obj))
                z = -pole / gain / obj

            ctrl = co.tf([1, -z], [1, obj])
            print("Posición del polo: s={:.2g}".format(-pole))

        print("Posición del cero: s={:.2g}".format(z))

    k_c = 1
    if s_star is not None:
        s_star = complex(s_star)
        if pole is None:
            k_c = abs(s_star)/abs(s_star - z)
        else:
            k_c = abs(s_star - z)/abs(s_star + pole)
        print("K_adj = {:.5g}".format(k_c))

    print("Controlador C(s)={}".format(k_c*ctrl))

    return ctrl


def root_locus(fdt):
    fig = plt.figure()
    tf_ctrl = text_to_tf(fdt)

    a, b = co.root_locus(tf_ctrl, plot=False)
    colors = ['red', 'green', 'blue', 'yellow', 'black']

    prev = []
    num_roots = len(a[0])
    for i in range(num_roots):
        prev.append((0 + 0j))

    num_rows = 0
    for row in a:
        cnt = 0
        for val in row:
            if num_rows > 0:
                plt.plot([prev[cnt].real, val.real], [prev[cnt].imag, val.imag], color=colors[cnt])
            prev[cnt] = val
            cnt = (cnt + 1) % num_roots
        num_rows = num_rows + 1

    a = co.pole(tf_ctrl)
    real_part = []
    for pol in a:
        plt.scatter(pol.real, pol.imag, marker="x", color='red')
        real_part.append(pol.real)

    ax =plt.axes()
    ax.set_xlim(min(real_part)-math.fabs(min(real_part)*2), max(real_part)+math.fabs(max(real_part)*2))

    plt.show()


def solve_equation_system(inp, vars, eqs):

    x = []
    eq = []
    inp = Symbol(inp)

    for i in eqs:
        if not i.endswith("=0"):
            print("*** ATENCIÓN: eq. {} no termina con '=0'".format(i))
        eq.append(i.replace("=0", ""))

    if len(vars) != len(eq):
        print("*** ERROR: Número de variables distinto de número de ecuaciones")
    else:
        for i in vars:
            x.append(Symbol(i))
    results = solve(eq, x)
    init_printing()
    for i in x:
        pprint("{}(s)/{}(s)=".format(i, inp))
        pprint(simplify(results[i]) / inp)
        print("")
        print("---")
        print("")


if True:

    def check_error_one_param():
        if len(sys.argv) < 3:
            print("Use: {} {} <fdt>".format(sys.argv[0], sys.argv[1]))
            print("Example: {} {} 's^2+2*s+1'".format(sys.argv[0], sys.argv[1]))
            sys.exit(0)

    if len(sys.argv) < 2:
        print("Available commands are:")
        print("root_locus")
        print("root_locus_angles")
        print("compute_controller")
        print("step_response")
        print("solve_equation_system")
        sys.exit(0)

    if sys.argv[1] == "root_locus":
        check_error_one_param()
        root_locus(sys.argv[2])
    elif sys.argv[1] == "root_locus_angles":
        check_error_one_param()
        root_locus_angles(sys.argv[2])
    elif sys.argv[1] == "step_response":
        check_error_one_param()
        step_response(sys.argv[2])
    elif sys.argv[1] == "compute_controller":
        if len(sys.argv) < 4:
            print("Use: {} compute_controller <plant> <s*> [RA_zero]".format(sys.argv[0]))
            print("Example: {} compute_controller 's^2+2*s+1' '-8+4j' '-8' ".format(sys.argv[0]))
            sys.exit(0)
        if len(sys.argv) >=5:
            compute_controller(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            compute_controller(sys.argv[2], sys.argv[3], "")
    elif sys.argv[1] == "solve_equation_system":
        if len(sys.argv) !=5:
            print("Use: {} solve_equation_system <input> <[variables]> <[equations]>".format(sys.argv[0]))
            print("Example: {} solve_equation_system 'Vr' 'i, ve, om, t' 'vr-(r*i+l*s*i+ve)=0, t-(j*s*om+b*om)=0, \
                                                                               t-ki*i=0, ve-ke*om=0'".format(sys.argv[0]))
            sys.exit(0)
        vars = sys.argv[3].replace(" ", "").split(",")
        eqs = sys.argv[4].replace(" ", "").split(",")
        print(vars, eqs)
        solve_equation_system(sys.argv[2], vars, eqs)
    elif sys.argv[1] == "rupture_points":
        check_error_one_param()
        rupture_points(sys.argv[2].replace("^","**"))
    elif sys.argv[1] == "asynt":
        check_error_one_param()
        asynt(sys.argv[2].replace("^", "**"))
    elif sys.argv[1] == "root_locus_all":
        check_error_one_param()
        fdt = sys.argv[2].replace("^", "**")
        print("* Asíntotas")
        asynt(fdt)
        print("---")
        print("* Puntos de ruptúra")
        rupture_points(fdt)
        print("---")
        print("* Ángulos de partida/llegada")
        root_locus_angles(fdt)
        print("---")
        root_locus(fdt)
    elif sys.argv[1] == "compensate_error":
        fdt = sys.argv[2].replace("^", "**")
        if len(sys.argv) == 4:
            compensate_error(fdt, sys.argv[3])
        elif len(sys.argv) == 5:
            compensate_error(fdt, sys.argv[3], sys.argv[4])
        elif len(sys.argv) == 6:
            if sys.argv[4] == "0":
                compensate_error(fdt, sys.argv[3], None, sys.argv[5])
            else:
                compensate_error(fdt, sys.argv[3], sys.argv[4], sys.argv[5])
        else:
            compensate_error(fdt)

