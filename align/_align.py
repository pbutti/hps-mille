"""Helper functions for running different stages of alignment"""

# system deps
import argparse
import os
import sys
import json
import shutil
import re
from typing import List

# external deps
import typer

# us
import _cmd
from _cfg import cfg
from _parameter import Parameter

app = typer.Typer(name='mille/align')

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
    
@app.command()
def tracking(det_name : str, run : int, input_file : str, 
    method : str = typer.Option('kf',
        help='type of tracking to do (kf or st)'),
    out_prefix : str = typer.Option(None,
        help='prefix to put onto output files'), 
    new_det : bool = typer.Option(False,
        help='this is a new detector and so we should construct it first'),
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
        to_float : List[str] = typer.Option(..., help='parameters to float'),
        out_dir : str = typer.Option(os.getcwd(), help='directory to save output to'),
        prefix : str = typer.Option('',help='prefix to attach to files'),
        year : int = typer.Option(2019,
            help='year data was taken, determines set of parameters'),
        survey_constraints : bool = typer.Option(False,
            help='UNTESTED apply constraints from survey'),
        beamspot_constraints : bool = typer.Option(False,
            help='UNTESTED apply beam spot constraints'),
        constraint_file : str = typer.Option(None,
            help='UNTESTED optional external constraint file for pede'),
        previous_fit : str = typer.Option(None,
            help='UNTESTED optional fille containting previous pede fit solution'),
        subito : bool = typer.Option(False,
            help='add the "-s" parameter to pede')
        ) :
    """
    Run the pede minimizer over the bin files generated by tracking
    """

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

    # build steering file for pede
    pede_steering_file = os.path.realpath(os.path.join(out_dir,prefix+'steer.txt'))
    with open(pede_steering_file,'w') as psf :
        # write out input mille binary files
        psf.write('CFiles\n')
        # scan each entry provided on command line,
        #  recursively entering subdiretories and including
        #  all '*.bin' files found
        for ipf in input_file :
            ipf = os.path.realpath(ipf)
            if os.path.isfile(ipf) and ipf.endswith('.bin') :
                psf.write(ipf+'\n')
            elif os.path.isdir(ipf) :
                for root, dirs, files in os.walk(ipf) :
                    for name in files :
                        if name.endswith('.bin') :
                            psf.write(os.path.join(root,name)+'\n')

        # external constraint file
        if constraint_file is not None :
            psf.write('\n')
            psf.write('!Constraint file\n')
            psf.write(constraint_file+'\n')

        # parameters that can float
        psf.write('\nParameter\n')
        for i, p in parameters.items() : 
            psf.write(p.pede_format() + '\n')

        # survey constraints
        if survey_constraints :
            psf.write('\n!Survey constraints tu\n')
            for p, name in param_map.items() :
                if p.module_number() == 0 :
                    continue
                if p.direction() == 'u' and p.type() == 't' :
                    psf.write('\nMeasurement 0.0 %.3f\n' % survey_meas_tu)
                    psf.write('%s 1.0\n' & p)
            psf.write("\n\n")
        
        # apply beamspotConstraint (This I think is not correct)
        if beamspot_constraints:
            #f.write(buildSteering.getBeamspotConstraints(paramMap))
            psf.write(buildSteering.getBeamspotConstraintsFloatingOnly(pars))
            psf.write("\n\n")
        
        psf.write("\n\n")
        # determine MP minimization settings
        with open(cfg.cfg().pede_minimization) as minfile :
            for line in minfile :
                psf.write(line)

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
            shutil.copy2(f,os.path.join(out_dir,prefix+f'millepede.{ext}'))

    return

@app.command()
def apply(pede_res : str, detector : str,
        bump : bool = typer.Option(True,
            help='Bump detector iteraction number and create a new copy?'),
        interactive : bool = typer.Option(False,
            help='Ask before applying any parameters'),
        force : bool = typer.Option(False,
            help='Force re-creation even if new iteraction already exists'),
        cleanup : bool = typer.Option(False,
            help='Remove original copy of compact.xml after update.')
        ) :
    """
    Apply the deduce alignment parameters from pede to the detector
    """

    if bump :
        # deduce source directory and check that it exists
        src_path = os.path.join(cfg.cfg().javadir, 'detector-data', 'detectors', detector)
        if not os.path.isdir(src_path) :
            raise typer.BadParameter(f'Detector {detector} is not in hps-java')
        
        # deduce iter value, using iter0 if there is no iter suffix
        matches = re.search('.*iter([0-9]*)', detector)
        if matches is None :
            detector = detector + '_iter0'
        else :
            i = int(matches.group(1))
            detector = detector.replace(f'_iter{i}',f'_iter{i+1}')
        print(detector)

        # deduce destination path, and make sure it does not exist
        dest_path = os.path.join(cfg.cfg().javadir, 'detector-data', 'detectors', detector)
        if os.path.isdir(dest_path) :
            if not interactive and not force :
                raise ValueError(f'Detector {detector} already exists and so it cannot be created')
            if interactive :
                typer.confirm(f'Overwite already existing detector {detector}?', abort=True)

        # make copy
        shutil.copytree(src_path, dest_path, dirs_exist_ok = True)

    # now we have bumped or not, so reconstruct detector path and check that it exists
    path = os.path.join(cfg.cfg().javadir, 'detector-data', 'detectors', detector)
    if not os.path.isdir(path) :
        raise typer.BadParameter(f'Detector {detector} is not in hps-java')

    # make sure compact exists
    detdesc = os.path.join(path,'compact.xml')
    if not os.path.isfile(detdesc) :
        raise typer.BadParameter(f'Detector {detector} has no compact.xml in {path} to apply parameter to.')

    # get list of parameters and their MP values
    parameters = Parameter.parse_pede_res(pede_res, skip_nonfloat=True)

    # modify file in place
    original_cp = detdesc + '.prev'
    shutil.copy2(detdesc,original_cp)
    f = open(detdesc,'w')
    with open(detdesc,'w') as f :
        with open(original_cp) as og :
            for line in og :
                if 'millepede_constant' not in line :
                    f.write(line)
                    continue

                for i in parameters :
                    if str(i) in line :
                        # the parameter with ID i is being set on this line
                        # format:
                        #   (whitespace) <millepede_constant name="<id>" value="<val>"/>

                        # get to value
                        i_value = line.find('value')
                        pre_val = line[:i_value]
                        post_val = line[i_value:]

                        # get to opening "
                        quote_open = post_val.find('"')
                        pre_val += post_val[:quote_open+1]
                        post_val = post_val[quote_open+1:]

                        # get to closing "
                        quote_close = post_val.find('"')
                        value = post_val[:quote_close]
                        post_val = post_val[quote_close:]

                        op = '+' if parameters[i].val > 0 else '-'
                        new_value = f'{value} {op} {abs(parameters[i].val)}'

                        if interactive :
                            doit = typer.confirm(f'Update {i} from "{value}" to "{new_value}"?')
                            if doit :
                                f.write(f'{pre_val}{new_value}{post_val}')
                            else :
                                f.write(line)
                        else :
                            f.write(f'{pre_val}{new_value}{post_val}')

    if (interactive and typer.confirm('Delete original copy?')) or cleanup :
        os.remove(original_cp)

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
