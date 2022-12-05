"""Helper functions for running different stages of alignment"""

# system deps
import argparse
import os
import sys
import json
from typing import List

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
    new_det : bool = typer.Option(False,help='this is a new detector and so we should construct it first'),
    ) :
    """
    Run tracking in the input detector.

    The detector LCDD is assumed to already be constructed.
    """

    if new_det :
        construct(det_name)

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
def millepede(
        input_file : List[str],
        to_float : List[str],
        year : int = typer.Option(2019,
            help='year data was taken, determines set of parameters'),
        survey_constraints : bool = typer.Option(False,
            help='apply constraints from survey'),
        beamspot_constraints : bool = typer.Option(False,
            help='apply beam spot constraints'),
        constraint_file : str = typer.Option(None,
            help='optional external constraint file for pede')
        previous_fit : str = typer.Option(None,
            help='optional fille containting previous pede fit solution')
        ) :
    """
    Run the pede minimizer over the bin files generated by tracking
    """

    from ._millepede import *

    # get parameters depending on year
    param_map_file = os.path.join(cfg.cfg().data_dir,'param_maps','hpsSvtParamMap.txt')
    if year == 2019 :
        param_map_file = os.path.join(cfg.cfg().data_dir,'param_maps','hpsSvtParamMap_2019.txt')

    parameters = Parameter.parse_map_file(param_map_file)

    # update parameters from previous fit
    if previous_fit is not None :
        Parameter.parse_pede_res(previous_fit, destination = previous_fit, skip_nonfloat = False)

    # define which parameters are floating
    floating = []
    for f in to_float :
        idn = None
        if f.isnumeric() :
            # string is a number, assume it is the idn
            idn = int(f)
        else:
            # look for sensor name
            for probe_id, p in parameters.items() :
                if p.name == f :
                    idn = prob_id
                    break

            if idn is None :
                raise ValueError(f'Parameter {f} not found in parameter map.')

        if idn not in parameters :
            raise ValueError(f'Parameter {idn} not found in parameter map.')

        parameters[idn].float()

    # determine MP minimization settings
    with open(cfg.cfg().pede_minimization) as minfile :
        minimization = minfile.readlines()

    # build steering file for pede
    pede_steering_file = os.path.join(out_dir,prefix,'steer.txt')
    with open(pede_steering_file,'w') as psf :
        # write out input mille binary files
        psf.write('CFiles\n')
        # scan each entry provided on command line,
        #  recursively entering subdiretories and including
        #  all '*.bin' files found
        for ipf in input_file :
            for root, dirs, files in os.walk(ipf) :
                for name in files :
                    if name.endswith('.bin') :
                        f.write(os.path.join(root,name)+'\n')

        # external contraint file
        if contraint_file is not None :
            f.write('\n')
            f.write('!Constraint file\n')
            f.write(constraint_file+'\n')

        # parameters that can float
        f.write('\nParameter\n')
        for p in parameters :
            f.write(p.pede_format() + '\n')

        # survey constraints
        if survey_constraints :
            f.write('\n!Survey constraints tu\n')
            for p, name in param_map.items() :
                if p.module_number() == 0 :
                    continue
                if p.direction() == 'u' and p.type() == 't' :
                    f.write('\nMeasurement 0.0 %.3f\n' % survey_meas_tu)
                    f.write('%s 1.0\n' & p)
            f.write("\n\n")
        
        #Apply beamspotConstraint (This I think is not correct)
        if beamspot_constraints:
            #f.write(buildSteering.getBeamspotConstraints(paramMap))
            f.write(buildSteering.getBeamspotConstraintsFloatingOnly(pars))
            f.write("\n\n")
        
        f.write("\n\n")
        f.write(minimization)

    # run pede
    for ext in ['res','eve','log','his'] :
        _cmd.run(['rm','-f', f'millepede.{ext}'], 
                cwd=cfg.cfg().scratch)
    pede_cmd = [cfg.cfg().pede, pede_steering_file]
    if subito :
        pede_cmd.append('-s')
    _cmd.run(pede_cmd, cwd=cfg.cfg().scratch)

    # move output to destination directory
    for ext in ['res','eve','log','his'] :
        f=os.path.join(cfg.cfg().scratch,f'millepede.{ext}')
        if os.path.isfile(f) :
            shutil.copy2(f,os.path.join(out_dir,prefix,f))

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

    conf_kw = dict()
    if config is not None :
        with open(config) as f :
            conf_kw = json.load(f)

    cfg.cfg(**conf_kw)
