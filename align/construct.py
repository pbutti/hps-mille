"""Construct a detector LCDD from the compact.xml"""

import os

import typer

import _cmd
from _cfg import cfg
from _cli import app

@app.command()
def construct(det_name : str) :
    """
    Construct a detector LCDD from the compact.xml

    The directory corresponding to DET_NAME is assumed to already
    exist withing <hps-java>/detector-data/detectors.
    """
    detector_dir = os.path.join(cfg.cfg().javadir, 'detector-data/detectors', det_name)

    if not os.path.isdir(detector_dir) :
        raise typer.BadParameter(f'{det_name} not in hps-java')

    # construct LCDD from compact
    _cmd.run(['java'] + cfg.cfg().javaopts + [
        '-cp', cfg.cfg().jarfile,
        'org.hps.detector.DetectorConverter',
        '-f', 'lcdd',
        '-i', f'{detector_dir}/compact.xml',
        '-o', f'{detector_dir}/{det_name}.lcdd'
      ], cwd = os.path.join(cfg.cfg().javadir,'detector-data'))

    # write detector name
    with open(f'{detector_dir}/detector.properties','w') as f :
        f.write(f'name: {det_name}\n')

    # rebuild jar to include this new detector
    _cmd.run(['mvn'] + cfg.cfg().mvnopts, cwd=os.path.join(cfg.cfg().javadir,'detector-data'))
    _cmd.run(['mvn'] + cfg.cfg().mvnopts, cwd=os.path.join(cfg.cfg().javadir,'distribution'))
    
if __name__ == '__main__' :
    app()
