"""Command Line Interface for align"""

import argparse
import sys
import inspect
from _cfg import cfg
import _align

def main() :
    stage_choices = dict(inspect.getmembers(_align, inspect.isfunction))

    parser = argparse.ArgumentParser('python3 align',
        description='run various stages of alignment procedure',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('stage', choices = stage_choices.keys(), help='choose which stage or stages to run')

    arg = parser.parse_args(sys.argv[1:2])

    stage_choices[arg.stage]()
