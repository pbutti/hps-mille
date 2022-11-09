"""Command Line Interface for align"""

import argparse
import sys
from _cfg import cfg
from _align import construct_detector, tracking

def main() :
    parser = argparse.ArgumentParser('python3 align',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--log', help='redirect command printouts to passed file')
    parser.add_argument('det_name', help='Base name for detector (i.e. omit iteration)')
    parser.add_argument('stage', nargs='+', choices=['construct','tracking'], help='choose which stage or stages to run')

    arg = parser.parse_args()

    log = sys.stdout
    if arg.log is not None :
        log = open(arg.log, 'w') 

    for s in arg.stage :
        if s == 'construct' :
            construct_detector(arg.det_name, log = log)
        elif s == 'tracking' :
            tracking(arg.det_name)

    if arg.log is not None :
        log.close()
