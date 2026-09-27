"""Track 7 figures F25/F26/F27/F29 from quantum_resource_estimate.csv + taxonomy/crossover/roadmap.
PROVENANCE: RESOURCE-EST on every panel. Assumes fault-tolerant hardware that does not yet exist."""
import numpy as np, pandas as pd, os, sys
import matplotlib as mpl, matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
try:
    apply_figure_style(sizes=(8,7,6))
except Exception as e:
    print("style note:",e)
FIG=os.path.join(HERE,"figs")
df=pd.read_csv(os.path.join(HERE,"quantum_resource_estimate.csv"))
tax=pd.read_csv(os.path.join(HERE,"taxonomy.csv"))
vdf=pd.read_csv(os.path.join(HERE,"crossover_verdict.csv"))
rm=pd.read_csv(os.path.join(HERE,"roadmap_dates.csv"))
CAP_DIST="d=19, t_cycle=1 us, p=1e-3, magic-state factory 15 d^2/factory, P_fail=1e-2 (baseline scenario)"
C={"K1":"#1b6ca8","K2":"#c1272d","K3":"#2e8b57","cls":"#555555","bar":"#888888"}

# ============ F25 — taxonomy matrix ============
def f25():
    cols=["speedup_class","readin_readout_penalty","survives_readinout","TRL"]
    colhdr=["speedup CLASS","read-in / read-out penalty","survives read-in/out?","TRL tier"]
    fig,ax=plt.subplots(figsize=(13,4.6)); ax.axis("off")
    nrow=len(tax); ncol=len(cols)
    ax.set_xlim(0,ncol+1.15); ax.set_ylim(0,nrow+1.4)
    def wrap(s,n=34):
        import textwrap; return "\n".join(textwrap.wrap(str(s),n))
    for j,h in enumerate(["kernel"]+colhdr):
        ax.text(0.05+j*1.0 if j==0 else j+0.02, nrow+0.55, h, fontweight="bold", fontsize=8, va="center")
    for i,(_,r) in enumerate(tax.iterrows()):
        y=nrow-1-i+0.5
        kc=C[r.kernel]
        ax.add_patch(mpl.patches.Rectangle((0.02,y-0.42),0.92,0.9,facecolor=kc,alpha=0.16,edgecolor=kc,lw=1.4))
        ax.text(0.06,y,f"{r.kernel}\n{r.physics.split('(')[0].strip()}",fontsize=7,va="center",fontweight="bold",color=kc)
        for j,c in enumerate(cols):
            ax.text(j+1+0.02,y,wrap(r[c]),fontsize=6.0,va="center")
    for j in range(ncol+2):
        xx=0.98 if j==1 else j
        ax.axvline(xx if j!=0 else 0.98, ymin=0.03, ymax=0.85, color="0.85", lw=0.6)
    ax.set_title("F25  Which fusion kernels a quantum computer could accelerate — a taxonomy of CLASSES, not factors",
                 fontsize=9, loc="left", pad=12)
    fig.text(0.01,0.015,
        "RESOURCE-EST — algorithmic taxonomy; no measurement. Each cell carries a speedup CLASS (asymptotic scaling and whether it survives read-in/read-out), never a speedup factor. "
        "Quantum COMPUTATION is an OFFLINE calibration tier, NEVER in the control loop. Assumes fault-tolerant hardware that does not yet exist. No Kronos operating-plant data exists.",
        fontsize=5.6, va="bottom")
    fig.tight_layout(rect=[0,0.05,1,1]); fig.savefig(os.path.join(FIG,"F25_taxonomy.png"),dpi=300); plt.close(fig)

# ============ F26 — 3-panel resource estimate (logical qubits + T-count vs problem size) ============
def f26():
    fig,axes=plt.subplots(1,3,figsize=(13.5,4.6))
    specs=[("K1","grid_pts_per_dim_N","grid points per dim  N","Vlasov / kinetic (E3)\nHamiltonian-sim + Carleman"),
           ("K2","grid_unknowns_Ng","equilibrium unknowns  N_g","equilibrium linear-solve (E1)\nQLSA — READ-IN/OUT LEADS"),
           ("K3","active_space_spin_orbitals_M","active-space spin-orbitals  M","materials ground state (E8)\nQPE / qubitization")]
    for ax,(k,pm,xl,tl) in zip(axes,specs):
        sub=df[(df.kernel==k)&(df.range_level=="mid")].sort_values("problem_size")
        lo=df[(df.kernel==k)&(df.range_level=="low")].sort_values("problem_size")
        hi=df[(df.kernel==k)&(df.range_level=="high")].sort_values("problem_size")
        kc=C[k]
        ax.plot(sub.problem_size, sub.T_count, "-o", color=kc, lw=2, ms=4, label="T-count (mid)")
        ax.fill_between(sub.problem_size, lo.T_count.values, hi.T_count.values, color=kc, alpha=0.18, label="T-count low–high")
        ax.set_yscale("log"); ax.set_xscale("log"); ax.set_xlabel(xl)
        ax.set_title(tl, fontsize=8, loc="left")
        # AC-43 bars
        ax.axhline(1e9, color="0.4", ls=":", lw=1); ax.axhline(1e12, color="0.4", ls="--", lw=1)
        ax.text(sub.problem_size.min(), 1.3e9, "1e9 T (2030 bar)", fontsize=5.5, color="0.35")
        ax.text(sub.problem_size.min(), 1.3e12, "1e12 T (2035 bar)", fontsize=5.5, color="0.35")
        # logical qubits on twin axis
        ax2=ax.twinx()
        ax2.plot(sub.problem_size, sub.logical_qubits, "-s", color="0.25", lw=1.2, ms=3, alpha=0.8)
        ax2.set_yscale("log"); ax2.set_ylabel("logical qubits", color="0.25", fontsize=7)
        ax2.tick_params(axis="y", labelcolor="0.25", labelsize=6)
        if k=="K2":
            # LEAD the adverse: annotate read-in/read-out inflation
            solo=df[(df.kernel=="K2")&(df.range_level=="low")].sort_values("problem_size")  # low=solve-only illusion
            ax.plot(solo.problem_size, solo.T_count, "--", color="0.5", lw=1.4, label="'one solve' illusion")
            i=list(sub.problem_size).index(1e4)
            ax.annotate("read-in + read-out\ninflate T by ~1e10×\n(full field, not one ⟨M⟩)",
                        xy=(1e4, sub.T_count.values[i]), xytext=(1.2e3, 3e19),
                        fontsize=6, color=kc, arrowprops=dict(arrowstyle="->",color=kc,lw=1))
        ax.legend(fontsize=5.6, loc="lower right", frameon=False)
    axes[0].set_ylabel("T-count  (log)")
    fig.suptitle("F26  Fault-tolerant resource estimate — T-count (colour) and logical qubits (grey) vs problem size",
                 fontsize=10, x=0.01, ha="left")
    fig.text(0.01,0.005,
        f"RESOURCE-EST — surface-code cost model, {CAP_DIST}. Assumes fault-tolerant hardware that does not yet exist. "
        "K2 panel LEADS with the read-in/read-out adverse finding: QLSA returns a quantum state, not the flux field control needs; "
        "extracting the whole field is O(N/eps^2) reruns. K1 T-count INCLUDES the Carleman/KvN nonlinearity cost. No Kronos operating-plant data exists.",
        fontsize=5.4, va="bottom")
    fig.tight_layout(rect=[0,0.055,1,0.95]); fig.savefig(os.path.join(FIG,"F26_resource_estimate.png"),dpi=300); plt.close(fig)

# ============ F27 — crossover / NO-crossover: wall-clock vs problem size ============
def f27():
    fig,axes=plt.subplots(1,3,figsize=(13.5,4.4))
    specs=[("K1","grid points per dim  N","CGYRO/GENE on Perlmutter node"),
           ("K2","equilibrium unknowns  N_g","EFIT multigrid on 1 Xeon core"),
           ("K3","active-space spin-orbitals  M","DMRG (Block2) [optimized]")]
    for ax,(k,xl,clab) in zip(axes,specs):
        sub=df[(df.kernel==k)&(df.range_level=="mid")].sort_values("problem_size")
        kc=C[k]
        ax.plot(sub.problem_size, sub.q_wall_s_baseline, "-o", color=kc, lw=2, ms=4, label="quantum wall-clock (FT, baseline)")
        ax.plot(sub.problem_size, sub.classical_wall_s_low, "-s", color=C["cls"], lw=1.8, ms=4, label=f"classical OPTIMIZED\n{clab}")
        ax.plot(sub.problem_size, sub.classical_wall_s_high, ":", color=C["cls"], lw=1.2, alpha=0.7, label="classical naive (upper)")
        ax.set_yscale("log"); ax.set_xscale("log"); ax.set_xlabel(xl)
        ax.set_title(f"{k}: NO CROSSOVER", fontsize=8.5, loc="left", color=kc, fontweight="bold")
        ax.legend(fontsize=5.6, loc="upper left", frameon=False)
        # shade the region: quantum always above classical-optimized
        ax.fill_between(sub.problem_size, sub.classical_wall_s_low, sub.q_wall_s_baseline,
                        where=(sub.q_wall_s_baseline.values>sub.classical_wall_s_low.values),
                        color=kc, alpha=0.08)
    axes[0].set_ylabel("wall-clock  [s]  (log)")
    fig.suptitle("F27  Classical-vs-quantum crossover — none this decade for any kernel (the section headline)",
                 fontsize=10, x=0.01, ha="left")
    fig.text(0.01,0.005,
        f"RESOURCE-EST — {CAP_DIST}. Quantum wall-clock is the reaction-limited LOWER bound (enough factories that distillation never stalls). "
        "A surface-code logical operation (~d·t_cycle) is ~1e5× slower than a classical FLOP, so quantum needs ≥1e5× fewer operations to break even — it never does. "
        "Classical baselines are NAMED optimized codes on NAMED hardware (AC-43). Assumes fault-tolerant hardware that does not yet exist. No Kronos operating-plant data exists.",
        fontsize=5.4, va="bottom")
    fig.tight_layout(rect=[0,0.06,1,0.95]); fig.savefig(os.path.join(FIG,"F27_crossover.png"),dpi=300); plt.close(fig)

# ============ F29 — roadmap: logical qubits vs year, sensing/compute SEPARATED ============
def f29():
    fig,ax=plt.subplots(figsize=(9.5,5.2))
    marks={"IBM":"o","Google":"s","Quantinuum":"^"}
    for org,g in rm.groupby("org"):
        ax.plot(g.year, g.logical_qubits, marks.get(org,"o"), ms=9, label=f"{org} (vendor projection)")
        for _,r in g.iterrows():
            ax.annotate(f"{org} {r.year}", (r.year,r.logical_qubits), textcoords="offset points",
                        xytext=(6,4), fontsize=6)
    # kernel thresholds (logical qubits needed at a scientifically-interesting size)
    thr={"K1":(130,"K1 Vlasov N=64"),"K2":(44,"K2 equilib N_g=1e4"),"K3":(120,"K3 materials M=100")}
    for k,(q,lab) in thr.items():
        ax.axhline(q, color=C[k], ls="--", lw=1.3, alpha=0.8)
        ax.text(2028.2, q*1.05, f"{lab}: {q} logical qubits", fontsize=6.2, color=C[k])
    ax.set_yscale("log"); ax.set_xlabel("calendar year"); ax.set_ylabel("logical qubits (log)")
    ax.set_title("F29  Quantum-COMPUTATION hardware trajectory vs kernel qubit thresholds\n(compute tier only; quantum SENSING is a SEPARATE track — see Track 8b)",
                 fontsize=9, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.text(0.5,0.02,
        "NOTE: even where a roadmap reaches a kernel's QUBIT threshold, the T-count runtime still LOSES to classical (see F27). "
        "Qubit availability is necessary, not sufficient.", transform=ax.transAxes, fontsize=6.2, style="italic", color="0.3", ha="center")
    fig.text(0.01,0.005,
        "RESOURCE-EST + TRL-SURVEY — dated points are NAMED vendor roadmap projections (IBM/Google/Quantinuum), not physics. "
        "Quantum-COMPUTATION tier ONLY; quantum-SENSING maturity is a separate track and is NOT plotted here (AC-46). "
        "Thresholds assume the baseline surface-code cost model. Assumes fault-tolerant hardware that does not yet exist. No Kronos operating-plant data exists.",
        fontsize=5.4, va="bottom")
    fig.tight_layout(rect=[0,0.05,1,1]); fig.savefig(os.path.join(FIG,"F29_roadmap.png"),dpi=300); plt.close(fig)

f25(); f26(); f27(); f29()
print("figures written:", os.listdir(FIG))
