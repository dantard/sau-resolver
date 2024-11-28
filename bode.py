#!/usr/bin/env python3
import sys

from lark.tools.serialize import argparser
from resolver import asbode







if __name__ == "__main__":
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(description="A simple argument parser example.")

    # Add arguments
    parser.add_argument('fdt', help="Transfer function")
    parser.add_argument('-t', '--tables', help="Print tables", action='store_true')
    parser.add_argument('-a', '--asymp', help="Plot asymptotic Bode", action='store_true')
    parser.add_argument('-b', '--bode', help="Plot real Bode", action='store_true')
    parser.add_argument('-e', '--exclude', help="Exclude 'phase' or 'mag'", type=str, default=None)
    parser.add_argument('-M', '--mmax', help="Module Max", type=int, default=None)
    parser.add_argument('-m','--mmin', help="Module Min", type=int, default=None)
    parser.add_argument('-P','--pmax', help="Phase Max", type=int, default=None)
    parser.add_argument('-p','--pmin', help="Phase Min", type=int, default=None)
    parser.add_argument('-s', '--save', help="Save to filename", type=str, default=None)
    parser.add_argument('-B', '--batch', help="Don't show figure", action='store_true')
    parser.add_argument('-L','--xlabel', help="X Label", type=str, default="")
    parser.add_argument('--ylabel1', help="Y Mag Label", type=str, default="")
    parser.add_argument('--ylabel2', help="Y Phase Label", type=str, default="")
    parser.add_argument('-T', '--title', help="Title", type=str, default="")
    parser.add_argument('-Y','--noy1ticks', help="Hide magnitude y-labels", action='store_true')
    parser.add_argument('-y','--noy2ticks', help="Hide phase y-labels", action='store_true')
    parser.add_argument('-x', '--noxticks', help="Hide frequency x-labels", action='store_true')
    parser.add_argument('-g', '--margins', help="Show margins (True or 'overlay')", action='store_true')
    parser.add_argument('-o', '--only', help="Plot only (mag or phase)", type=str, default=None)

    args = parser.parse_args()

    if not (args.asymp or args.bode or args.tables):
         sys.exit("*** You must select at least one plot type: -a, -b, -t")

    if args.batch and args.save is None:
         sys.exit("*** Batch mode is pretty useless without -s option")

    kwargs = vars(args)

    asbode(args.fdt, **kwargs)