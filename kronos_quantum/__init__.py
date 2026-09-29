"""Kronos Quantum — honest, runnable quantum-computing-for-fusion codes.

Nine quantum programs, each a real, runnable pipeline that executes on a
simulator today and on real quantum hardware the moment you plug in an account
(one environment variable, same code path).  Every code carries an honest card:
no quantum *advantage* for fusion is claimed this decade -- a meaningful role is
a post-~2036 prospect -- but the tooling and testing are real NOW.

Registry-by-design.  You get a code through the registry, never a top-level
import:

    import kronos_quantum as Q
    Q.list_codes()            # the nine quantum codes
    s = Q.get("KQUBIT")       # the instance
    p = Q.run("KQUBIT", None) # -> Prediction(y, uncertainty, in_domain)

`from kronos_quantum import KQUBIT` fails by design.
"""
from __future__ import annotations

__version__ = "0.3.0"

from .base import Surrogate, Prediction  # noqa: E402

#: code-name -> Surrogate subclass
SURROGATES: dict[str, type] = {}


def register(cls):
    """Class decorator: add a quantum code to the registry."""
    SURROGATES[cls.name] = cls
    return cls


def get(name: str) -> Surrogate:
    """Instantiate a code by name (e.g. get('KQUBIT'))."""
    return SURROGATES[name]()


def run(name: str, x=None):
    """Convenience: predict with a named code. -> Prediction."""
    return get(name).predict(x)


def list_codes():
    """All registered quantum code names, sorted."""
    return sorted(SURROGATES)


# backwards-compatible alias (the KODEX fleet calls this list_surrogates)
list_surrogates = list_codes


def cards():
    """Return every code's honest card."""
    return [get(n).card() for n in list_codes()]


# populate the registry (members import numpy + base only at load time; pennylane
# and sklearn are imported lazily, so `import kronos_quantum` stays light)
from . import members  # noqa: E402,F401
