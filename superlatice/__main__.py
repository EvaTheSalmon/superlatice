import argparse
import sys
from pandas import options
import matplotlib.pyplot as plt
from pathlib import Path

from function_lib import *

__version__ = 1
options.mode.chained_assignment = None


def main(self) -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description='This is a tool to analyze \
                                                                              superlatice data')
    parser.add_argument(
        "path", metavar='/path/to/your.file', type=str, nargs='+',
        help="input path to '.csv' files to extract data to work with"
    )

    parser.add_argument(
        "--plot", "-p",
        action="store_true",
        help="show plot for superlatice"
    )

    parser.add_argument(
        "--mean", "-m",
        action="store",
        type=float,
        help="show mean concentration, for every \"n\" percent of superlatice width"
    )

    parser.add_argument(
        "--width", "-w",
        action="store",
        default=0.9,
        type=float,
        help="set width of bars for mean concentration [0..1]"
    )

    parser.add_argument(
        "--output", "-o",
        action="store",
        help="custom output path to save results. if not provided input file dir is used by default"
    )

    args = parser.parse_args()
    path = args.path
    plot = args.plot
    pieces = args.mean
    width = args.width
    output_path = args.output

    # default action with no flags provided
    if (plot is False and pieces is None) or plot:
        for file in path:
            fig1 = plot_graph(separate_shutters(load_file(file)))
            if output_path is not None:
                if check_output(output_path):
                    p = Path(file).stem
                    fig1.savefig(output_path + '\\' + str(p) + '.jpg')
                    print('data written to ', output_path)
            else:
                p = Path(file).stem
                d = Path(file).parent
                fig1.savefig(str(d) + '\\' + str(p) + '.jpg')
                print(' data written to ', str(d))

    if pieces is not None:
        for file in path:
            fig2 = mean(separate_shutters(load_file(file)), pieces, width)
            if output_path is not None:
                if check_output(output_path):
                    p = Path(file).stem
                    fig2.savefig(output_path + '\mean_' + str(p) + '.jpg')
                    print('mean data written to ', output_path)
            else:
                p = Path(file).stem
                d = Path(file).parent
                fig2.savefig(str(d) + '\mean_' + str(p) + '.jpg')
                print('mean data written to ', str(d))


if __name__ == '__main__':
    main(sys.argv)
