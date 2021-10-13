from resolver import *
import sys

set_verbose(True)

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
    if len(sys.argv) >= 5:
        compute_controller(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        compute_controller(sys.argv[2], sys.argv[3], "")
elif sys.argv[1] == "solve_equation_system":
    if len(sys.argv) != 5:
        print("Use: {} solve_equation_system <input> <[variables]> <[equations]>".format(sys.argv[0]))
        print("Example: {} solve_equation_system 'Vr' 'i, ve, om, t' 'vr-(r*i+l*s*i+ve)=0, t-(j*s*om+b*om)=0, \
                                                                           t-ki*i=0, ve-ke*om=0'".format(
            sys.argv[0]))
        sys.exit(0)
    vars = sys.argv[3].replace(" ", "").split(",")
    eqs = sys.argv[4].replace(" ", "").split(",")
    print(vars, eqs)
    solve_equation_system(sys.argv[2], vars, eqs)
elif sys.argv[1] == "rupture_points":
    check_error_one_param()
    rupture_points(sys.argv[2].replace("^", "**"))
elif sys.argv[1] == "asynt":
    check_error_one_param()
    asynt(sys.argv[2].replace("^", "**"))
elif sys.argv[1] == "root_locus_all":
    check_error_one_param()
    fdt = sys.argv[2].replace("^", "**")
    print("* Asíntotas")
    asynt(fdt)
    print("")
    print("* Puntos de ruptúra")
    rupture_points(fdt)
    print("")
    print("* Ángulos de partida/llegada")
    root_locus_angles(fdt)
    print("")
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
elif sys.argv[1] == "valid_zone":
    valid_zone(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]))
else:
    print("Non existent command")