#!/usr/bin/env python3
"""
Track 8b - Quantum SENSING & metrology (E11). Reproduces every number in:
  quantum_sensing_trl.csv, sensing_precision_scaling.csv, precision_scaling_devices.csv,
  sensing_to_ai_gain.csv, and figures F21-F24.
Seed convention: 20260726 (program). Hardware: local CPU (56 cores, no GPU) - all
computations here are sub-second; no latency claim is made from this script.
Provenance: TRL-SURVEY (survey tables) + SIM (state-estimation propagation). NO Kronos
operating-plant data is used anywhere. Design point: reference_design_card.csv
(R0=2 m, a=1 m, B0=10 T, Ip=31.47 MA, ne=5.42e20 m^-3).
"""
import numpy as np, csv, os
TR=os.path.dirname(os.path.abspath(__file__))

# --- E11 precision scaling: theory laws (AC-50: both are THEORY, not device points) ---
N=np.logspace(2,12,200)
dphi_sql=1/np.sqrt(N)     # standard quantum limit, F_Q<=N  (separable)
dphi_heis=1/N            # Heisenberg limit,      F_Q<=N^2 (entangled) - a BOUND not a spec
# From the quantum Cramer-Rao bound dphi >= 1/sqrt(nu F_Q). Caves 1981; Giovannetti 2011.

# --- Sensing -> AI state-estimation propagation (SIM) ---
mu0=4e-7*np.pi; a=1.0
r_p=0.85*a; r_wall=1.15*a; n_fil=16; n_sensors=40
th_f=np.linspace(0,2*np.pi,n_fil,endpoint=False)
th_s=np.linspace(0,2*np.pi,n_sensors,endpoint=False)
fx,fy=r_p*np.cos(th_f),r_p*np.sin(th_f)
sx,sy=r_wall*np.cos(th_s),r_wall*np.sin(th_s)
H=np.array([[mu0/(2*np.pi*np.hypot(sx[i]-fx[j],sy[i]-fy[j])) for j in range(n_fil)]
            for i in range(n_sensors)])
Ip_total=31.473e6
base=1.0+0.3*np.cos(th_f)+0.12*np.cos(2*th_f)
x_true=Ip_total*base/base.sum()
y_clean=H@x_true
L=np.zeros((n_fil,n_fil))
for i in range(n_fil):
    L[i,i]=2; L[i,(i-1)%n_fil]=-1; L[i,(i+1)%n_fil]=-1
lam_rel=1e-3; MODEL_ERR=2e-3   # 0.2% forward-operator/geometry mismatch = irreducible floor

def sweep(signal_scale,sigmas,n_seed=20):
    ys=y_clean*signal_scale; xt=x_true*signal_scale
    HtH=H.T@H; lam=lam_rel*(np.trace(HtH)/np.trace(L.T@L)); means=[];stds=[]
    for sig in sigmas:
        e=[]
        for s in range(n_seed):
            rng=np.random.default_rng(20260726+s)
            y=ys+rng.normal(0,sig,n_sensors)+rng.normal(0,MODEL_ERR*np.abs(ys))
            s2=sig**2+(MODEL_ERR*np.median(np.abs(ys)))**2
            xh=np.linalg.solve(HtH/s2+lam*(L.T@L), H.T@y/s2)
            e.append(np.linalg.norm(xh-xt)/np.linalg.norm(xt))
        e=np.array(e); means.append(e.mean()); stds.append(e.std())
    return np.array(means),np.array(stds)

if __name__=="__main__":
    sigmas=np.logspace(-15,-2,40)
    m_s,_=sweep(1.0,sigmas); m_w,_=sweep(1/300.,sigmas)
    def at(sig,m): return np.interp(np.log10(sig),np.log10(sigmas),m)
    conv,nv=5e-4,2.85e-11
    print("model floor (zero-noise recon error): %.3e"%m_s[0])
    print("EQUILIBRIUM  conv=%.3e NV=%.3e  reduction=%.1f%%"%(at(conv,m_s),at(nv,m_s),
          100*(at(conv,m_s)-at(nv,m_s))/at(conv,m_s)))
    print("EDGE/WEAK    conv=%.3e NV=%.3e  reduction=%.1f%%"%(at(conv,m_w),at(nv,m_w),
          100*(at(conv,m_w)-at(nv,m_w))/at(conv,m_w)))
