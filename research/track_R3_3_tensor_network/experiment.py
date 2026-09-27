"""
R3-3 experiment: tensor-network (MPS/two-site DMRG) vs classical baseline on the K1
kinetic kernel, scored on ACCURACY-AT-FIXED-COST.  PROVENANCE: SIM. Runs today, no hardware.

Both methods carry a real COST KNOB so the fixed-cost comparison is fair:
  classical  = restarted Lanczos (scipy eigsh) capped at a matvec budget k  (accuracy improves with k)
               NAMED baseline: ARPACK implicitly-restarted Lanczos on the full N^d sparse operator.
  tensor-net = two-site DMRG at bond dimension chi                          (accuracy improves with chi)

Ground truth = exact ARPACK ground energy (eigsh, tight tol) where the full operator is feasible.
Cost axes reported BOTH: measured wall-clock (s) and a FLOP proxy, plus peak operator memory (N^d).
"""
import numpy as np, scipy.sparse.linalg as spla, scipy.sparse as sp, time, os, sys, tracemalloc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel_and_dmrg as K

def exact_ground(d,N,g,tol=1e-11):
    H=K.full_hamiltonian(d,N,g)
    t0=time.perf_counter()
    w=spla.eigsh(H,k=1,which='SA',tol=tol,return_eigenvectors=False)
    wall=time.perf_counter()-t0
    return float(w[0]), wall, H.nnz, H.shape[0]

def classical_lanczos_budget(d,N,g,maxiter_list,tol=0.0):
    """Restarted Lanczos capped at maxiter (matvec budget). Returns list of (maxiter,E,wall,converged)."""
    H=K.full_hamiltonian(d,N,g); dim=H.shape[0]; nnz=H.nnz
    out=[]
    for mi in maxiter_list:
        ncv=min(dim-1, max(2*1+1, 20))
        t0=time.perf_counter()
        conv=True
        try:
            w=spla.eigsh(H,k=1,which='SA',maxiter=mi,ncv=ncv,tol=tol,return_eigenvectors=False)
            E=float(w[0])
        except spla.ArpackNoConvergence as e:
            conv=False
            E=float(e.eigenvalues[0]) if len(e.eigenvalues)>0 else np.nan
        wall=time.perf_counter()-t0
        # FLOP proxy: (matvecs ~ maxiter*ncv) * nnz*2
        flops=mi*ncv*nnz*2.0
        out.append(dict(maxiter=mi, E=E, wall=wall, converged=conv, nnz=nnz, dim=dim, flops=flops))
    return out

def dmrg_budget(d,N,g,chi_list,n_sweeps=12,seed=1):
    """DMRG at a sequence of bond dims. Returns list of (chi,E,wall,max_bond,sweeps,flops)."""
    mpo=K.build_mpo(d,N,g)
    out=[]
    for chi in chi_list:
        t0=time.perf_counter()
        E,info=K.dmrg(mpo,d,N,chi=chi,n_sweeps=n_sweeps,seed=seed)
        wall=time.perf_counter()-t0
        # FLOP proxy per two-site update ~ (chi^2 N^2)*(mpo_bond=3) matvec, ~ n_matvec times, x eigsh inner (~ncv)
        flops=info['n_matvec']*(chi**2)*(N**2)*3*30*2.0
        out.append(dict(chi=chi, E=E, wall=wall, max_bond=int(info['max_bond']),
                        sweeps=info['sweeps'], n_matvec=info['n_matvec'], flops=flops))
    return out

if __name__=='__main__':
    d,N,g=6,8,0.6
    Eex,wex,nnz,dim=exact_ground(d,N,g)
    print(f"exact d={d} N={N} g={g}: E={Eex:.8f} wall={wex:.3f}s dim={dim} nnz={nnz}")
    print("classical Lanczos budget:")
    for r in classical_lanczos_budget(d,N,g,[1,2,3,5,10]):
        print(f"  maxiter={r['maxiter']:>3} E={r['E']:.8f} rel={abs(r['E']-Eex)/abs(Eex):.2e} wall={r['wall']:.4f} conv={r['converged']}")
    print("DMRG budget:")
    for r in dmrg_budget(d,N,g,[2,4,8,16,32]):
        print(f"  chi={r['chi']:>3} E={r['E']:.8f} rel={abs(r['E']-Eex)/abs(Eex):.2e} wall={r['wall']:.4f} bond={r['max_bond']}")
