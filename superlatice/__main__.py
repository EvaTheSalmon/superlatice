import argparse
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

__version__ = 1
pd.options.mode.chained_assignment = None


def isNaN(num):
    return num != num


def load_file(input_path: str) -> pd.DataFrame:
    """
    Function that loads and cleans file
    :param input_path:
    :return: DataFrame with processes and path to origin file
    """
    with open(input_path, encoding="utf8") as fp:
        data = pd.read_csv(fp, names=['time', 'title', 'shutter', 'state'], sep=';| ', engine='python')
        del data['title']

    i = 0
    for string in data['time']:
        if type(string) == str:
            hour_point = float(string[:2])
            minute_point = float(string[3:5])
            second_point = float(string[6:8])
            data.at[i, 'time'] = hour_point * 3600 + minute_point * 60 + second_point
        i += 1
    data = data.replace({'state': {'close': 0, 'open': 1}})
    data['state'] = data['state'].astype(int)
    data['time'] = data['time'].astype(int)
    return data


def get_unique_list(t: list) -> list:
    s = []
    for i in t:
        if i not in s:
            s.append(i)
    return s


def fill_columns(data: pd.DataFrame) -> pd.DataFrame:
    shutters = data.columns.tolist()
    shutters.remove('time')
    for s in shutters:
        i = 0
        m = data[s].iat[0]
        for t in data[s]:
            if isNaN(t):
                data[s].iat[i] = m
            elif int(t) == 1:
                m = 1
            else:
                m = 0
            i += 1
    return data


def separate_shutters(data: pd.DataFrame) -> pd.DataFrame:
    maxtime = int(data.tail(1).iat[0, 0])
    maindb = pd.DataFrame({'time': range(0, maxtime)})
    shutters = get_unique_list(data.set_index(['time', 'state']).to_dict('list')['shutter'])

    for s in shutters:
        sh = data.loc[data['shutter'] == s]
        del sh['shutter']
        sh = sh.rename(columns={'state': 'shut'+str(s)})
        maindb = maindb.set_index('time').join(sh.set_index('time'))
        maindb['time'] = range(0, maxtime)
    m = fill_columns(maindb)
    return m


def plot_graph(data: pd.DataFrame):
    del data['time']
    return data.plot().get_figure()


def mean(data: pd.DataFrame, pieces: int, width: float):
    maxtime = int(data['time'].at[len(data)-1])
    del data['time']
    data = data.groupby(data.index // (maxtime/pieces)).mean()
    data = data.div(data.sum(axis=1), axis=0)
    return data.plot.bar(stacked=True, width=width).get_figure()


def yes_no_question(question: str) -> bool:
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    print(question + ', continue? [Y/n]')
    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def check_output(output_path: str) -> bool:
    """
    Function to check if the provided by --output path can be used to write files. If directory not exist then user
    will see the message proposing to create such.
    :param output_path: path to check in string format
    :return: True of False
    """
    if Path(output_path).is_dir():
        return True
    if not Path(output_path).is_dir():
        if yes_no_question('Provided path not exist and will be created'):
            Path(output_path).mkdir(parents=True)
            return True
        else:
            print("Stopped by user")
            return False
    else:
        return False


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