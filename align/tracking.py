"""run tracking in hps-java on the input detector"""

import typer

import _cmd
from _cfg import cfg
from _cli import app

@app.command()
def tracking(det_name : str, run : int, input_file : str, 
    method : str = typer.Option('kf',
        help='type of tracking to do (kf or st)'),
    out_prefix : str = typer.Option(None,
        help='prefix to put onto output files')
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

if __name__ == '__main__' :
    app()
