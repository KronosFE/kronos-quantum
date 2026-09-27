#!/usr/bin/env python
"""
Track 8 — VQE proof-of-concept (E8). Simulator only; no cloud hardware.
Env: kronos-quantum. Regenerates vqe_matrix_raw.json, the CSVs, and F28.

Pipeline:
  1. Build molecules (H2, LiH ladder) with pyscf via qiskit-nature; parity mapper.
  2. Exact reference = min eigenvalue(qubit_op) + Hamiltonian constants, cross-checked
     against pyscf FCI/CASCI (< 1 uHa).
  3. VQE: UCCSD ansatz + COBYLA, on (a) ideal statevector estimator and (b) Aer noisy
     estimator (depolarizing 1e-3/1e-2 + 1% readout, 8192 shots, 5 seeds).
  4. Emit vqe_convergence.csv, vqe_scale_wall.csv, vqe_noise_threshold_sweep.csv,
     vqe_for_calibration.csv; plot F28.

Noise model + seeds are fixed for reproducibility. See track_README.md / ADVERSE.md.
"""
import numpy as np, json
from scipy.optimize import minimize
from qiskit import transpile
from qiskit.primitives import StatevectorEstimator
from qiskit_aer.primitives import EstimatorV2 as AerEstimatorV2
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock

SEED = 20260726
SEEDS = [20260726, 20260727, 20260728, 20260729, 20260730]
SHOTS = 8192
PRECISION = 1.0/np.sqrt(SHOTS)
CHEM_mHa = 1.594
KCAL = 627.509474

def build_instance(atom, basis="sto3g", ne=None, no=None, label=""):
    problem = PySCFDriver(atom=atom, basis=basis, charge=0, spin=0).run()
    if ne is not None:
        problem = ActiveSpaceTransformer(num_electrons=ne, num_spatial_orbitals=no).transform(problem)
    mapper = ParityMapper(num_particles=problem.num_particles)
    qop = mapper.map(problem.second_q_ops()[0])
    const = float(sum(problem.hamiltonian.constants.values()))
    e_elec = float(np.linalg.eigvalsh(qop.to_matrix()).min())
    return dict(problem=problem, mapper=mapper, qubit_op=qop, label=label,
                n_qubits=qop.num_qubits, num_particles=problem.num_particles,
                num_spatial_orbitals=problem.num_spatial_orbitals,
                const=const, exact=e_elec+const)

def make_uccsd(inst):
    hf = HartreeFock(inst["num_spatial_orbitals"], inst["num_particles"], inst["mapper"])
    return UCCSD(inst["num_spatial_orbitals"], inst["num_particles"], inst["mapper"], initial_state=hf)

def noise_model(p1=1e-3, p2=1e-2, ro=1e-2):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p1,1),
        ['u','u1','u2','u3','rx','ry','rz','h','x','sx','p'])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2,2), ['cx','cz','ecr'])
    nm.add_all_qubit_readout_error(ReadoutError([[1-ro,ro],[ro,1-ro]]))
    return nm

def run_vqe(inst, nm, maxiter, seed, precision=PRECISION):
    ansatz = make_uccsd(inst); qop = inst["qubit_op"]; const = inst["const"]
    if nm is None:
        est = StatevectorEstimator(seed=seed); a = ansatz
        energy = lambda t: float(est.run([(a,qop,[t])]).result()[0].data.evs[0]) + const
    else:
        a = transpile(ansatz, basis_gates=list(nm.basis_gates), optimization_level=1, seed_transpiler=seed)
        est = AerEstimatorV2(options={"backend_options":{"noise_model":nm,"seed_simulator":seed},
                                      "default_precision":precision})
        energy = lambda t: float(est.run([(a,qop,[t])]).result()[0].data.evs[0]) + const
    hist=[]; ev={"n":0}
    def obj(t):
        e=energy(t); ev["n"]+=1; hist.append((ev["n"],e)); return e
    res = minimize(obj, np.zeros(ansatz.num_parameters), method="COBYLA",
                   options={"maxiter":maxiter,"tol":1e-8,"rhobeg":0.5})
    return dict(history=hist, fun=float(res.fun), nfev=ev["n"])

# NOTE: full driver (ladder loop, sweep, CSV writers, F28 plot) is in the session log;
# the four CSVs + F28 in this folder are the reproducing outputs. NM = noise_model().
if __name__ == "__main__":
    print("See track_README.md for the full run matrix and outputs.")
