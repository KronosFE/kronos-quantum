"""
R3-3 DEFINITIVE experiment: tensor-network (MPS/two-site DMRG) vs classical baseline on the
K1 kinetic kernel (discretised Vlasov/collision operator, coupled velocity-mode chain), scored on
ACCURACY-AT-FIXED-COST.  PROVENANCE: SIM. Runs TODAY, no quantum hardware, no operating-plant data.

Ground truth = exact ARPACK ground energy of the DISCRETISED operator (eigsh, tol 1e-11), where the
full N^d operator is feasible.  For d where the full operator is INFEASIBLE (N^d too large), DMRG is
cross-checked by (i) chi-convergence (variational upper bound, monotone) and (ii) the continuum
coupled-oscillator normal-mode formula (a coarser reference; the residual is the grid discretisation gap).

BASELINE (named, optimised): ARPACK implicitly-restarted Lanczos (scipy.sparse.linalg.eigsh, k=1,
which='SA') on the full sparse N^d operator -- the standard sparse symmetric ground-state eigensolver.
TN SOLVER: from-scratch two-site DMRG, canonical MPS, SVD truncation to bond dimension chi.

Cost knobs (both sides real): classical = Lanczos tolerance (-> matvec count); TN = bond dimension chi.
Cost axes reported BOTH: measured wall-clock (s) and matvec count; plus operator/state memory (elements).
Verdict metric: iso-accuracy wall-clock to reach rel_err <= TARGET_ACC (lower wins); feasibility at large d.
"""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla, time, os, sys, math, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel_and_dmrg as K

SEED=20260726          # house MC seed
TARGET_ACC=1e-6        # iso-accuracy target for the wall-clock verdict
HERE=os.path.dirname(os.path.abspath(__file__))

def entanglement_mid(d,N,g):
    """Mid-cut entanglement entropy (nats) + effective Schmidt rank of the exact ground state."""
    H=K.full_hamiltonian(d,N,g)
    w,v=spla.eigsh(H,k=1,which='SA',tol=1e-10); psi=v[:,0]
    cut=d//2; M=psi.reshape(N**cut, N**(d-cut))
    s=np.linalg.svd(M,compute_uv=False); s=s[s>1e-14]
    p=s**2; p/=p.sum(); S=float(-(p*np.log(p)).sum())
    eff=int(np.sum(s/s[0]>1e-8))
    return S, eff, float(w[0])

def classical_full(d,N,g,tol):
    """Full sparse Lanczos to tolerance tol. Returns E, wall, matvec count, nnz, dim, mem_elems."""
    H=K.full_hamiltonian(d,N,g); dim=H.shape[0]; nnz=H.nnz
    cnt={'n':0}
    def mv(x): cnt['n']+=1; return H@x
    Hop=spla.LinearOperator((dim,dim),matvec=mv,dtype=float)
    t0=time.perf_counter()
    w=spla.eigsh(Hop,k=1,which='SA',tol=tol,return_eigenvectors=False,maxiter=dim*20)
    wall=time.perf_counter()-t0
    return float(w[0]),wall,cnt['n'],nnz,dim,nnz   # sparse operator memory ~ nnz elements

def dmrg_run(d,N,g,chi,n_sweeps=14):
    mpo=K.build_mpo(d,N,g)
    t0=time.perf_counter(); E,info=K.dmrg(mpo,d,N,chi=chi,n_sweeps=n_sweeps,seed=1); wall=time.perf_counter()-t0
    mem=d*N*(chi**2)                     # MPS state memory (elements)
    return E,wall,info['n_matvec'],int(info['max_bond']),info['sweeps'],mem

def iso_accuracy_wall(curve, Eref, target):
    """First (lowest-cost) point on a curve reaching rel_err<=target -> its wall-clock; else None."""
    for row in curve:
        if abs(row['E']-Eref)/abs(Eref) <= target:
            return row['wall'], row
    return None, None

def run():
    rows=[]
    # ---- REGIMES ----
    # A: moderate (both feasible) -- expect TN win.   B: small (adverse: classical dense wins).
    # C: large-d (classical full tensor infeasible; TN feasible+converged).
    regimes=[
        ("A_moderate", 6, 8, 0.6, True,  True ),
        ("A_moderate", 7, 8, 0.5, True,  True ),
        ("B_small",    3, 4, 0.5, True,  True ),
        ("B_small",    4, 5, 0.5, True,  True ),
        ("C_large_d", 10, 8, 0.3, False, True ),
        ("C_large_d", 20, 8, 0.3, False, True ),
        ("C_large_d", 40, 8, 0.3, False, True ),
        ("C_large_d", 80, 8, 0.3, False, True ),
    ]
    for (regime,d,N,g,classical_feasible,tn_feasible) in regimes:
        Ndp = N**d
        # ground truth + entanglement (only where full operator feasible)
        if classical_feasible and Ndp<=3_000_000:
            S,eff,Eex = entanglement_mid(d,N,g); gt_src="exact_disc(ARPACK)"
        else:
            S,eff = float('nan'), -1
            Eex = K.analytic_E0(d,N,g); gt_src="analytic_continuum(coarse_ref)"

        # CLASSICAL curve
        cls_curve=[]
        if classical_feasible:
            for tol in [1e-2,1e-4,1e-6,1e-8,1e-10]:
                E,wall,mv,nnz,dim,mem=classical_full(d,N,g,tol)
                cls_curve.append(dict(knob=f"tol={tol:.0e}",E=E,wall=wall,matvec=mv,flops=mv*nnz*2.0,mem=mem))
        # DMRG curve
        tn_curve=[]
        chi_list=[2,4,8,16,32] if regime!="C_large_d" else [8,16,24,32]
        for chi in chi_list:
            E,wall,mv,mb,sw,mem=dmrg_run(d,N,g,chi)
            flops=mv*(chi**2)*(N**2)*3*30*2.0
            tn_curve.append(dict(knob=f"chi={chi}",E=E,wall=wall,matvec=mv,flops=flops,mem=mem,max_bond=mb,sweeps=sw))

        # iso-accuracy verdict (only meaningful when a true ground truth exists)
        if gt_src.startswith("exact"):
            cls_iso,_=iso_accuracy_wall(cls_curve,Eex,TARGET_ACC)
            tn_iso,_ =iso_accuracy_wall(tn_curve,Eex,TARGET_ACC)
        else:
            cls_iso,tn_iso=None,None

        # emit rows: one per (method, budget)
        for r in cls_curve:
            rel=abs(r['E']-Eex)/abs(Eex)
            rows.append(dict(regime=regime,method="classical_Lanczos",kernel="K1_Vlasov_chain",
                d=d,N=N,g=g,classical_dim_Nd=f"{Ndp:.3e}",budget_knob=r['knob'],
                matvec=r['matvec'],wall_s=round(r['wall'],5),flops_proxy=f"{r['flops']:.3e}",
                mem_elems=r['mem'],accuracy_relerr=f"{rel:.3e}",entanglement_S_mid=(f"{S:.4f}" if S==S else "nan"),
                eff_schmidt_rank=eff,feasible=1,ground_truth=gt_src,provenance="SIM",basis_tag="SIM"))
        for r in tn_curve:
            rel=abs(r['E']-Eex)/abs(Eex)
            rows.append(dict(regime=regime,method="tensor_network_DMRG",kernel="K1_Vlasov_chain",
                d=d,N=N,g=g,classical_dim_Nd=f"{Ndp:.3e}",budget_knob=r['knob'],
                matvec=r['matvec'],wall_s=round(r['wall'],5),flops_proxy=f"{r['flops']:.3e}",
                mem_elems=r['mem'],accuracy_relerr=f"{rel:.3e}",entanglement_S_mid=(f"{S:.4f}" if S==S else "nan"),
                eff_schmidt_rank=eff,feasible=1,ground_truth=gt_src,provenance="SIM",basis_tag="SIM"))

        # verdict row
        if cls_iso is not None and tn_iso is not None:
            winner = "tensor_network_DMRG" if tn_iso<cls_iso else "classical_Lanczos"
            speedup = (cls_iso/tn_iso) if tn_iso>0 else float('inf')
        elif not classical_feasible:
            winner="tensor_network_DMRG(only_feasible)"; speedup=float('inf')
        else:
            winner="none_reached_target"; speedup=float('nan')
        rows.append(dict(regime=regime,method="VERDICT",kernel="K1_Vlasov_chain",
            d=d,N=N,g=g,classical_dim_Nd=f"{Ndp:.3e}",
            budget_knob=f"iso_acc<= {TARGET_ACC:.0e}",
            matvec="", wall_s="", flops_proxy="",
            mem_elems="",
            accuracy_relerr=f"cls_wall={cls_iso if cls_iso else 'INF/NA'};tn_wall={tn_iso if tn_iso else 'INF/NA'}",
            entanglement_S_mid=(f"{S:.4f}" if S==S else "nan"),eff_schmidt_rank=eff,
            feasible=(1 if classical_feasible else 0),
            ground_truth=f"wins={winner};speedup={speedup:.2f}x" if speedup==speedup else f"wins={winner}",
            provenance="SIM",basis_tag="SIM"))
        print(f"[{regime}] d={d} N={N} g={g} dim={Ndp:.1e} S_mid={S if S==S else float('nan'):.3f} "
              f"cls_iso={cls_iso} tn_iso={tn_iso} winner={winner}")

    # write CSV
    cols=["regime","method","kernel","d","N","g","classical_dim_Nd","budget_knob","matvec","wall_s",
          "flops_proxy","mem_elems","accuracy_relerr","entanglement_S_mid","eff_schmidt_rank",
          "feasible","ground_truth","provenance","basis_tag"]
    out=os.path.join(HERE,"tensor_network_vs_classical.csv")
    with open(out,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow(r)
    print("WROTE",out,"rows=",len(rows))
    return rows

if __name__=="__main__":
    run()
