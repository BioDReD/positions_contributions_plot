#!/usr/bin/env python3

"""
Created on 18 Jul. 2022
"""

__author__ = "Nicolas JEANNE"
__copyright__ = "GNU General Public License"
__email__ = "jeanne.n@chu-toulouse.fr"
__version__ = "1.0.0"

import argparse
import logging
import os
import sys

from dna_features_viewer import GraphicFeature, GraphicRecord
import pandas as pd


def create_log(path, level):
    """Create the log as a text file and as a stream.

    :param path: the path of the log.
    :type path: str
    :param level: the level og the log.
    :type level: str
    :return: the logging:
    :rtype: logging
    """

    log_level_dict = {"DEBUG": logging.DEBUG,
                      "INFO": logging.INFO,
                      "WARNING": logging.WARNING,
                      "ERROR": logging.ERROR,
                      "CRITICAL": logging.CRITICAL}

    if level is None:
        log_level = log_level_dict["INFO"]
    else:
        log_level = log_level_dict[args.log_level]

    if os.path.exists(path):
        os.remove(path)

    logging.basicConfig(format="%(asctime)s %(levelname)s:\t%(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=log_level,
                        handlers=[logging.FileHandler(path), logging.StreamHandler()])
    return logging


def create_hue(thr):
    """
    Create a dictionary of hues with thresholds as keys.

    :param thr: the threshold from where the hue should start.
    :type thr: float
    :return: the dictionary of hues
    :rtype: dict
    """
    hue_list = ["#fee0d2", "#fc9272", "#de2d26"]
    step = (100 - thr) / len(hue_list)
    hue_data = {}
    local_thr = thr + step
    for hue_value in hue_list:
        hue_data[local_thr] = hue_value
        local_thr = local_thr + step
    return hue_data


if __name__ == "__main__":
    descr = f"""
    {os.path.basename(__file__)} v. {__version__}

    Created by {__author__}.
    Contact: {__email__}
    {__copyright__}

    Distributed on an "AS IS" basis without warranties or conditions of any kind, either express or implied.

    Produce a plot of the contribution of the positions of a sequence. 
    The contributions are 
    A threshold is set to select only the positions above it. 
    """
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--out", required=True, type=str, help="the path to the output plot.")
    parser.add_argument("-t", "--threshold", required=True, type=float,
                        help="the threshold (>=) to display the contribution of the position.")
    parser.add_argument("-p", "--position-col", required=True, type=str, help="the name of the position column.")
    parser.add_argument("-x", "--target-col", required=True, type=str,
                        help="the name of the target contribution column.")
    parser.add_argument("-s", "--sequence-size", required=False, type=int, help="the size of the studied sequence.")
    parser.add_argument("-l", "--log", required=False, type=str,
                        help="the path for the log file. If this option is skipped, the log file is created in the "
                             "output directory.")
    parser.add_argument("--log-level", required=False, type=str,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="set the log level. If the option is skipped, log level is INFO.")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("input", type=str,
                        help="the path to CSV (semi-colon separated) contribution file.")
    args = parser.parse_args()

    # create output directory
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)

    # create the logger
    if args.log:
        log_path = args.log
    else:
        log_path = os.path.join(out_dir, f"{os.path.splitext(os.path.basename(__file__))[0]}.log")
    create_log(log_path, args.log_level)

    logging.info(f"version: {__version__}")
    logging.info(f"CMD: {' '.join(sys.argv)}")

    # load the data
    df = pd.read_csv(args.input, sep=";", decimal=",")

    # set the color palette
    hue = create_hue(args.threshold)

    # get the sequence length
    if args.sequence_size:
        seq_size = args.sequence_size
    else:
        seq_size = int(df[args.position_col].max())
    logging.info(f"sequence size ({'provided by the user' if args.sequence_size else 'last position of contribution'}):"
                 f" {seq_size}")
    features = [GraphicFeature(start=0, end=seq_size, strand=+1, color="#ffd700", label="Spike",
                               fontdict={"weight": "bold"})]
    nb_pass_contrib = 0
    nb_contrib = 0
    for index, row in df.iterrows():
        if row[args.target_col] > 0:
            nb_contrib += 1
        if row[args.target_col] >= args.threshold:
            nb_pass_contrib += 1
            color = None
            for local_threshold in sorted(hue.keys()):
                color = hue[local_threshold]
                if row[args.target_col] < local_threshold:
                    break

            features.append(GraphicFeature(start=row[args.position_col],
                                           end=row[args.position_col]+1,
                                           strand=+1,
                                           color=color,
                                           box_color=color,
                                           label=f"{int(row[args.position_col])}: {round(row[args.target_col], 2)}%"))
    prop_passed = nb_pass_contrib / nb_contrib
    logging.info(f"{nb_pass_contrib}/{nb_contrib} positions with a contribution >= {args.threshold}% contribution "
                 f"threshold ({prop_passed:.2%})")

    record = GraphicRecord(sequence_length=seq_size, features=features, plots_indexing="genbank")
    ax, _ = record.plot(draw_line=True, figure_width=20)
    ax.set_title(f"Contributions {args.target_col.replace('_', ' ')}: {prop_passed:.2%} of {nb_contrib} positions >= "
                 f"{args.threshold}% contribution threshold", loc="left", weight="bold")
    ax.figure.savefig(args.out, bbox_inches="tight")
