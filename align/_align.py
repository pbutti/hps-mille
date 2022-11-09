"""Helper functions for running different stages of alignment"""

import os
import _cmd
from _cfg import cfg

def construct_detector(det_name) :
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
    
def tracking(det_name, run, output_file_prefix, steering, input_file) :

    # allow output file prefix to define an output directory
    #   and create it if it doesn't exist yet
    import os
    d = os.path.dirname(output_file_prefix)
    if d != '' :
        os.makedirs(d, exist_ok=True)

    # run tracking over the input detector
    return _cmd.run(['java'] + cfg.cfg().javaopts + [
      '-DdisableSvtAlignmentConstants',
      '-jar', cfg.cfg().jarfile,
      '-R', run, 
      '-d', det_name,
      f'-DoutputFile={output_file_prefix}',
      steering,
      '-i', input_file
      ])

def millepede(det_name, **kwargs) :
    pass
