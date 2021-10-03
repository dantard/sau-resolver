from matplotlib import pyplot as plt
import control as co
import sympy as sp
import math
from sympy import *

def ruth(polinomio):

	from matplotlib import pyplot as plt
	import control as co
	import sympy as sp
	import math
	from tbcontrol.symbolic import routh
	from sympy.solvers.inequalities import solve_poly_inequalities
	from sympy.solvers.inequalities import solve_rational_inequalities
	

	s = sp.Symbol('s')
	k = sp.Symbol('k')
	K = sp.Symbol('K')
	p=sp.Poly(polinomio.replace("^","**"),s)
	init_printing()
	print("La tabla de Routh es para el polinomio "+polinomio+" es:\n")
	table = routh(p)
	pprint(table)
	

	if 'K' in polinomio:
		print("\nEstabilidad:")
		polys = []
		for i in range(table.rows):
			val = table[i,0]
			if not val.is_Number:
				polys.append(val.as_numer_denom()[0].as_poly())
		
		query = []
		for i in polys:
			ineq = (i,Poly(1,K),)
			all=(ineq,">")
			query.append(all)
			res=solve_rational_inequalities([[all]])
			txt=pretty(res)
			print("* Para inecuación ["+pretty(i.as_expr())+" > 0], intervalo",pretty(res))
			
		res=solve_rational_inequalities([query])
		print("** Sistema estable para K en intervalo:", pretty(res))
	else:
		changes = 0
		last_sign = table[0,0]
		for i in range(table.rows):
			val = table[i,0]
			if last_sign > 0 and val<0 or last_sign <0 and val > 0:
				changes = changes + 1 
				last_sign=val
		
		if changes==0:
			print("\nEl sistema es estable")
		else:
			print("\nEl sistema es inestable, tiene {:d} polo/s en el s/p derecho y {:d} en s/p izquierdo".format(changes, table.rows-1-changes))
			


def compute_controller(planta, s_star, cero):

	if (cero!=""):
	  print("Calculando una RED DE ADELANTO (RA) con cero en s={}".format(cero))
	  planta="(s-{})*(".format(cero) +planta+")"
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
	poles=co.pole(tf_ctrl)
	zeros=co.zero(tf_ctrl)
	s_star=complex(s_star)

	angle_poles = 0
	mod_poles = 1
	for i in poles:
	  angle = math.atan2(s_star.imag,s_star.real-i)*180/math.pi
	  mod = abs(s_star-i)
	  print("Polo en {:.2f} tiene ángulo {:.2f} grados con s* y módulo {:.2f}".format(i, angle, mod))
	  angle_poles+=angle
	  mod_poles = mod_poles * mod

	angle_zeros = 0
	mod_zeros = 1
	for i in zeros:
	  angle = math.atan2(s_star.imag,s_star.real-i)*180/math.pi
	  mod = abs(s_star-i)
	  print("Cero en {:.2f} tiene ángulo {:.2f} grados con s* y módulo {:.2f}".format(i, angle, mod))
	  angle_zeros+=angle
	  mod_zeros = mod_zeros * mod

	needed = (-180-angle_zeros+angle_poles)
	print("---")
	print("Falta fase de {:.2f} grados".format(needed))
	print("---")

	ko = (is_pd and (needed > 180 or needed < 0)) or \
	      (not is_pd and (needed < -180 or needed > 0))

	if (ko):
	  print("ERROR: Imposible encontrar " + looking_for)
	else:
	  needed = math.fabs(needed)
	  if needed > 90:
	      delta_x = s_star.imag/math.tan(math.pi*(180-needed)/180)
	  else:
	      delta_x = s_star.imag/math.tan(math.pi*needed/180)

	  sing_pos = s_star.real-delta_x

	  if is_pd:
	    gain = mod_poles / mod_zeros / abs(s_star - sing_pos)
	    ctrl = gain*co.tf([1, -sing_pos],[1])
	  else:
	    gain = mod_poles * abs(s_star - sing_pos) / mod_zeros 
	    ctrl = gain*co.tf([1, -float(cero)],[1, -sing_pos])
	  
	  print("La posición del "+ looking_for+" es {:.2f} y la ganancia {:.2f}".format(sing_pos, gain)) 
	  print("---")
	  print("El controlador es: C(s)={}".format(ctrl))

ruth("-s^3+ s^2+3*s+1")
