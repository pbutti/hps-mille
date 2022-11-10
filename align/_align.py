"""Helper functions for running different stages of alignment"""

import argparse
import os
import sys
import _cmd
from _cfg import cfg

def construct() :
    parser = argparse.ArgumentParser(description = 'construct an LCDD from a compact.xml')

    parser.add_argument('det_name', help='name of detector')

    args = parser.parse_args(sys.argv[2:])

    detector_dir = os.path.join(cfg.cfg().javadir, 'detector-data/detectors', det_name)
    # construct LCDD from compact
    _cmd.run(['java'] + cfg.cfg().javaopts + [
        '-cp', cfg.cfg().jarfile,
        'org.hps.detector.DetectorConverter',
        '-f', 'lcdd',
        '-i', f'{detector_dir}/compact.xml',
        '-o', f'{detector_dir}/{det_name}.lcdd'
      ], cwd = cfg.cfg().javadir)

    # write detector name
    with open(f'{detector_dir}/detector.properties','w') as f :
        f.write(f'name: {det_name}\n')

    # rebuild jar to include this new detector
    _cmd.run(['mvn'] + cfg.cfg().mvnopts, cwd=os.path.join(cfg.cfg().javadir,'detector-data'))
    _cmd.run(['mvn'] + cfg.cfg().mvnopts, cwd=os.path.join(cfg.cfg().javadir,'distribution'))
    
def tracking() :
    parser = argparse.ArgumentParser(description = 'construct an LCDD from a compact.xml')

    parser.add_argument('det_name', help='name of detector')
    parser.add_argument('output_prefix', help='prefix output files in steering file with this string')
    parser.add_argument('--run',type=int,help='run number so conditions are usable')
    parser.add_argument('--steering',help='steering file')
    parser.add_argument('--input',help='input slcio file')

    args = parser.parse_args(sys.argv[2:])

    # allow output file prefix to define an output directory
    #   and create it if it doesn't exist yet
    import os
    d = os.path.dirname(output_file_prefix)
    if d != '' :
        os.makedirs(d, exist_ok=True)

    # run tracking over the input detector
    _cmd.run(['java'] + cfg.cfg().javaopts + [
      '-DdisableSvtAlignmentConstants',
      '-jar', cfg.cfg().jarfile,
      '-R', run, 
      '-d', det_name,
      f'-DoutputFile={output_file_prefix}',
      steering,
      '-i', input_file
      ])

def millepede() :

    # get default parameters depending on beamspot and year

    # update parameters from previous fit

    # define which parameters are floating

    # determine MP minimization settings

    # build steering file for pede

    # run pede

    # move output to destination directory

    return
