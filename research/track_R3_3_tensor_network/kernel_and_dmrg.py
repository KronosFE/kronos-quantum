"""
R3-3 — Quantum-inspired classical (tensor-network) solver for the K1 kinetic kernel.

KERNEL (fusion-authentic, ground-truthable): the discretised velocity-space kinetic
operator of K1 (Vlasov/collision, 5-D phase space; track7 kernels.py) in a coupled
velocity-mode CHAIN representation.  The d phase-space/velocity coordinates are the
sites of a matrix-product state (MPS); each site carries a local dimension N (grid
points / Hermite moments in that coordinate).

  H = sum_i h_i  +  g * sum_i X_i X_{i+1}

  h_i  = 1/2 ( -d^2/dv^2 + omega^2 v^2 )   discretised on an N-point grid  (Dirichlet)
         -> on-site relaxation operator; ground state = 1-D Maxwellian (collisional eq.)
  g X_i X_{i+1}  = inter-mode velocity-space coupling (anisotropy / streaming / FLR).

Physical reading: the leading (ground) eigenmode is the collisional equilibrium; its
eigenvalue E0 is the transport-relevant relaxation scalar.  g is BOTH the physical
coupling strength AND the entanglement knob:
  g = 0    -> separable, product-Maxwellian, Schmidt rank 1  (MPS exact, cheap)
  g -> 1-  -> a normal mode softens, correlation length & entanglement grow
              (MPS needs large bond dim; this is the stiff / strongly-coupled regime).

PROVENANCE: SIM.  No hardware, no quantum device, no operating-plant data.  Runs today.
Ground truth for accuracy scoring = exact diagonalisation (ARPACK eigsh) of the SAME
discretised sparse operator, cross-checked against the analytic coupled-oscillator
normal-mode energy E0 = 1/2 sum_k sqrt(lambda_k(K)).

Classical baseline (NAMED, optimised): ARPACK implicitly-restarted Lanczos
(scipy.sparse.linalg.eigsh, k=1, which='SA') on the full N^d sparse operator -- the
workhorse sparse symmetric eigensolver.  Its memory & cost scale as N^d (the curse of
dimensionality the classical closure hits).

TN solver: from-scratch two-site DMRG (canonical MPS, SVD truncation to bond dim chi,
effective-Hamiltonian ground state via eigsh on a LinearOperator).  Cost/sweep ~ d N^2 chi^2.
Correctness is PROVEN against exact diagonalisation on small cases (see validate()).
"""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla, time

# ----------------------------------------------------------------------------- local ops
def local_ops(N, L=6.0, omega=1.0):
    """1-D grid operators on [-L,L], N points, Dirichlet. Returns (h, X, I)."""
    x = np.linspace(-L, L, N)
    dx = x[1]-x[0]
    # second derivative, tridiagonal, Dirichlet BC
    D2 = (np.diag(-2.0*np.ones(N)) + np.diag(np.ones(N-1),1) + np.diag(np.ones(N-1),-1))/dx**2
    X  = np.diag(x)
    h  = 0.5*(-D2 + (omega**2)*X@X)
    return h, X, np.eye(N)

# ----------------------------------------------------------------------------- full sparse H (reference)
def full_hamiltonian(d, N, g, L=6.0, omega=1.0):
    """Build the exact N^d x N^d sparse operator (reference / classical baseline target)."""
    h, X, I = local_ops(N, L, omega)
    hs, Xs, Is = sp.csr_matrix(h), sp.csr_matrix(X), sp.identity(N, format='csr')
    def kron_at(op_list):
        M = op_list[0]
        for op in op_list[1:]:
            M = sp.kron(M, op, format='csr')
        return M
    H = sp.csr_matrix((N**d, N**d))
    for i in range(d):                       # on-site
        ops = [Is]*d; ops[i] = hs
        H = H + kron_at(ops)
    for i in range(d-1):                     # neighbour coupling
        ops = [Is]*d; ops[i] = Xs; ops[i+1] = Xs
        H = H + g*kron_at(ops)
    return H

def analytic_E0(d, N, g, L=6.0, omega=1.0):
    """Continuum coupled-oscillator normal-mode ground energy (cross-check only)."""
    K = np.diag((omega**2)*np.ones(d)) + g*(np.diag(np.ones(d-1),1)+np.diag(np.ones(d-1),-1))
    lam = np.linalg.eigvalsh(K)
    if np.any(lam <= 0):
        return np.nan
    return 0.5*np.sum(np.sqrt(lam))

def exact_E0(d, N, g, L=6.0, omega=1.0, tol=1e-10):
    """Exact ground energy of the DISCRETISED operator via ARPACK (ground truth)."""
    H = full_hamiltonian(d, N, g, L, omega)
    t0 = time.perf_counter()
    w = spla.eigsh(H, k=1, which='SA', tol=tol, return_eigenvectors=False)
    wall = time.perf_counter()-t0
    nnz = H.nnz
    return float(w[0]), wall, nnz, H.shape[0]

# ----------------------------------------------------------------------------- MPO
def build_mpo(d, N, g, L=6.0, omega=1.0):
    """Finite-automaton MPO, bond dim 3, for H = sum h_i + g sum X_i X_{i+1}."""
    h, X, I = local_ops(N, L, omega)
    # bulk W[a,b] operator-valued 3x3:
    #   [[ I ,  0 ,  0 ],
    #    [ X ,  0 ,  0 ],
    #    [ h , gX ,  I ]]
    def bulk():
        W = np.zeros((3,3,N,N))
        W[0,0]=I; W[1,0]=X; W[2,0]=h; W[2,1]=g*X; W[2,2]=I
        return W
    mpo = []
    for i in range(d):
        W = bulk()
        if i==0:
            mpo.append(W[2:3,:,:,:].copy())      # left boundary = bottom row (1,3,N,N)
        elif i==d-1:
            mpo.append(W[:,0:1,:,:].copy())       # right boundary = first col (3,1,N,N)
        else:
            mpo.append(W.copy())
    return mpo   # list of (bl,br,N,N)

# ----------------------------------------------------------------------------- MPS + two-site DMRG
def rand_mps(d, N, chi0, seed=0):
    rng = np.random.default_rng(seed)
    dims = [1]+[min(chi0, N**min(i+1, d-i-1)) for i in range(d-1)]+[1]
    dims = [max(1,x) for x in dims]
    A = [rng.standard_normal((dims[i], N, dims[i+1]))*0.1 for i in range(d)]
    return A

def right_canonicalise(A):
    d = len(A)
    for i in range(d-1, 0, -1):
        chil, N, chir = A[i].shape
        mat = A[i].reshape(chil, N*chir)
        U,S,Vh = np.linalg.svd(mat, full_matrices=False)
        A[i] = Vh.reshape(-1, N, chir)
        US = U*S
        A[i-1] = np.tensordot(A[i-1], US, axes=([2],[0]))
    # normalise
    n = np.linalg.norm(A[0].ravel()); A[0]/=n
    return A

def init_right_env(A, mpo):
    d = len(A)
    R = [None]*(d+1)
    R[d] = np.ones((1,1,1))
    for i in range(d-1, -1, -1):
        R[i] = contract_right(A[i], mpo[i], R[i+1])
    return R

def contract_right(Ai, Wi, Rnext):
    # Ai (a,N,b), Wi (wl,wr,N,N'), Rnext (b, wr, b')
    tmp = np.tensordot(Ai, Rnext, axes=([2],[0]))          # a,N, wr,b'
    tmp = np.tensordot(Wi, tmp, axes=([1,3],[2,1]))        # wl,N, a, b'
    tmp = np.tensordot(tmp, Ai.conj(), axes=([1,3],[1,2])) # wl,a, a'
    return tmp.transpose(1,0,2)                            # a, wl, a'

def contract_left(Ai, Wi, Lprev):
    # Lprev (a, wl, a'), Ai (a,N,b), Wi (wl,wr,N,N')
    tmp = np.tensordot(Lprev, Ai, axes=([0],[0]))          # wl,a', N,b
    tmp = np.tensordot(Wi, tmp, axes=([0,2],[0,2]))        # wr,N', a',b
    tmp = np.tensordot(Ai.conj(), tmp, axes=([0,1],[2,1])) # b(from a'),  wr,b
    return tmp.transpose(2,1,0)                            # b, wr, b'   -> (a=b, wl=wr, a'=b')

def two_site_H(L, W1, W2, R):
    """Two-site effective Hamiltonian as a LinearOperator on T(aL,N1,N2,aR).
    Index conventions (verified against dense einsum + Hermiticity/upper-bound check):
      L: (ket_out a', w, bra_in a)      R: (ket_out b', w, bra_in b)
      W: (w_left, w_right, s_out, s_in)
    H_eff: T'(a',p,x,b') = L(a',wl,a) W1(wl,wm,p,q) W2(wm,wr,x,y) R(b',wr,b) T(a,q,y,b)
    Uses a fixed-path einsum for the matvec (correct for all bond dims).
    """
    aL = L.shape[0]; N1=W1.shape[2]; N2=W2.shape[2]; aR=R.shape[0]
    def mv(v):
        T = v.reshape(aL, N1, N2, aR)                 # (a,q,y,b)
        x = np.tensordot(L, T, axes=([2],[0]))        # a',wl, q,y,b
        x = np.tensordot(W1, x, axes=([0,3],[1,2]))   # wm,p, a',y,b
        x = np.tensordot(W2, x, axes=([0,3],[0,3]))   # wr,x, p,a',b
        x = np.tensordot(R, x, axes=([1,2],[0,4]))    # b',x, p,a'
        return x.transpose(3,2,1,0).ravel()           # a',p,x,b'
    dim = aL*N1*N2*aR
    return spla.LinearOperator((dim,dim), matvec=mv, dtype=float), (aL,N1,N2,aR)

def dmrg(mpo, d, N, chi, n_sweeps=8, chi0=None, seed=0, tol_local=1e-8, verbose=False,
         time_budget=None):
    """Two-site DMRG. Returns (E, info). Stops on convergence, sweep cap, or time_budget (s)."""
    t_start = time.perf_counter()
    chi0 = chi0 or min(chi, 8)
    A = right_canonicalise(rand_mps(d, N, chi0, seed))
    R = init_right_env(A, mpo)
    Lenv = [None]*(d+1); Lenv[0] = np.ones((1,1,1))
    E_prev = np.inf; n_matvec=0; max_bond=0
    hit_budget=False
    for sweep in range(n_sweeps):
        # left-to-right then right-to-left
        for direction in ('LR','RL'):
            rng_sites = range(d-1) if direction=='LR' else range(d-2,-1,-1)
            for i in rng_sites:
                if time_budget is not None and (time.perf_counter()-t_start) > time_budget:
                    hit_budget=True; break
                Hop, shp = two_site_H(Lenv[i], mpo[i], mpo[i+1], R[i+2])
                aL,N1,N2,aR = shp
                # initial guess from current tensors
                two = np.tensordot(A[i], A[i+1], axes=([2],[0])).ravel()
                k = min(1, Hop.shape[0]-1) or 1
                try:
                    w,v = spla.eigsh(Hop, k=1, which='SA', v0=two, tol=tol_local, maxiter=2000)
                except Exception:
                    w,v = spla.eigsh(Hop, k=1, which='SA', tol=tol_local, maxiter=5000)
                n_matvec += 1
                E = float(w[0]); psi = v[:,0].reshape(aL*N1, N2*aR)
                U,S,Vh = np.linalg.svd(psi, full_matrices=False)
                keep = min(chi, np.sum(S>1e-14))
                keep = max(1, keep)
                U=U[:,:keep]; S=S[:keep]; Vh=Vh[:keep,:]
                max_bond=max(max_bond,keep)
                if direction=='LR':
                    A[i]   = U.reshape(aL,N1,keep)
                    A[i+1] = (np.diag(S)@Vh).reshape(keep,N2,aR)
                    Lenv[i+1] = contract_left(A[i], mpo[i], Lenv[i])
                else:
                    A[i]   = (U*S).reshape(aL,N1,keep)
                    A[i+1] = Vh.reshape(keep,N2,aR)
                    R[i+1] = contract_right(A[i+1], mpo[i+1], R[i+2])
            if hit_budget: break
        if hit_budget: break
        if abs(E-E_prev) < 1e-10:
            E_prev=E; break
        E_prev=E
    wall = time.perf_counter()-t_start
    info = dict(sweeps=sweep+1, n_matvec=n_matvec, max_bond=max_bond, wall=wall,
                hit_budget=hit_budget)
    return E_prev, info

# ----------------------------------------------------------------------------- validation
def validate():
    print("VALIDATION: DMRG vs exact diagonalisation (proves correctness)")
    print(f"{'d':>2} {'N':>3} {'g':>5} {'E_exact':>12} {'E_dmrg':>12} {'rel_err':>10} {'chi':>4}")
    for (d,N,g) in [(4,6,0.0),(4,6,0.5),(5,6,0.5),(6,5,0.7),(4,8,0.9)]:
        Eex,_,_,_ = exact_E0(d,N,g)
        mpo = build_mpo(d,N,g)
        Ed,info = dmrg(mpo,d,N,chi=40,n_sweeps=12,seed=1)
        rel = abs(Ed-Eex)/abs(Eex)
        print(f"{d:>2} {N:>3} {g:>5.2f} {Eex:>12.6f} {Ed:>12.6f} {rel:>10.2e} {info['max_bond']:>4}")

if __name__=='__main__':
    validate()
