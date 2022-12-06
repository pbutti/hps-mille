"""Main entrypoint when running this package

    python3 align <args>

Calls into this module.
"""

import typer

from _cli import app
from _cfg import cfg
import construct
import tracking
import apply
import pede

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

if __name__ == '__main__' :
    app()
