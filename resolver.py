from matplotlib import pyplot as plt
import control as co
import sympy as sp
import math

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

compute_controller("1/(s+5)/(s+8)","-4+8j","-6")
