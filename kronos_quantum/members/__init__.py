"""Import every quantum member module so it self-registers into the registry."""
from . import quantum      # noqa: F401  KQUBIT, KQROSS, KSENSE, KTENSOR, KQERN, KQOPT, KDYN
from . import quantum_v3   # noqa: F401  KMIT, KLINQ
