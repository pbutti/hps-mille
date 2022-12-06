"""Module to hold CLI object"""

import functools
import inspect
from typing import Callable

import typer
from typer.models import ParameterInfo

app = typer.Typer()

def typer_unpacker(f: Callable):
    """Decorator which access typer defaults and updates the kwargs
    so that the function can be used in typer CLI and normally

    https://github.com/tiangolo/typer/issues/279#issuecomment-893667754
    """
    def wrapper(*args, **kwargs):
        # Get the default function argument that aren't passed in kwargs via the
        # inspect module: https://stackoverflow.com/a/12627202
        missing_default_values = {
            k: v.default
            for k, v in inspect.signature(f).parameters.items()
            if v.default is not inspect.Parameter.empty and k not in kwargs
        }

        for name, func_default in missing_default_values.items():
            # If the default value is a typer.Option or typer.Argument, we have to
            # pull either the .default attribute and pass it in the function
            # invocation, or call it first.
            if isinstance(func_default, ParameterInfo):
                if callable(func_default.default):
                    kwargs[name] = func_default.default()
                else:
                    kwargs[name] = func_default.default

        # Call the wrapped function with the defaults injected if not specified.
        return f(*args, **kwargs)

    return wrapper
