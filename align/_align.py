"""Helper functions for running different stages of alignment"""

# system deps
import argparse
import os
import sys

# external deps
import typer

# us
import _cmd
from _cfg import cfg

app = typer.Typer()

@app.command()
def construct(det_name : str) :
    """
    Construct a detector LCDD from the compact.xml

    The directory corresponding to DET_NAME is assumed to already
    exist withing <hps-java>/detector-data/detectors.
    """
    detector_dir = os.path.join(cfg.cfg().javadir, 'detector-data/detectors', det_name)
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
    
@app.command()
def tracking(det_name : str, run : int, input_file : str, 
    method : str = typer.Option('kf',help='type of tracking to do (kf or st)'),
    out_prefix : str = typer.Option(None,help='prefix to put onto output files'), 
    ) :
    """
    Run tracking in the input detector.

    The detector LCDD is assumed to already be constructed.
    """

    # allow output file prefix to define an output directory
    #   and create it if it doesn't exist yet
    import os
    d = os.path.dirname(out_prefix)
    if d != '' :
        os.makedirs(d, exist_ok=True)

    steering = None
    if method == 'kf' :
        steering = cfg.cfg().kf_steer
    elif method == 'st' :
        steering = cfg.cfg().st_steer
    else :
        raise ValueError('Unknown tracking method "%s", choices are "kf" or "st"' % method)

    # run tracking over the input detector
    _cmd.run(['java'] + cfg.cfg().javaopts + [
      '-DdisableSvtAlignmentConstants',
      '-jar', cfg.cfg().jarfile,
      '-R', str(run), 
      '-d', det_name,
      f'-DoutputFile={out_prefix}',
      steering,
      '-i', input_file
      ])

@app.command()
def millepede() :
    """
    Run the pede minimizer over the bin files generated by tracking
    """

    # get default parameters depending on beamspot and year

    # update parameters from previous fit

    # define which parameters are floating

    # determine MP minimization settings

    # build steering file for pede

    # run pede

    # move output to destination directory

    return

@app.command()
def config() :
    """
    Print the deduced/parsed config for debugging
    """

    print(cfg.cfg())
    return

@app.callback()
def main(config : str =  typer.Option(None,help='JSON config file')):
    """
    run alignment sub commands
    """

    if config is not None :
        with open(config) as f :
            conf = json.load(f)
        cfg.cfg(**conf)
    else :
        cfg.cfg()
