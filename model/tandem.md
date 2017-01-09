# Tandem Trainer Aircraft

Sizing model for a tandem trainer plane.

```python
#inPDF: replace with tex/Mission.generated.tex
from tandem import Mission
from gen_tex import gen_model_tex, find_submodels, gen_tex_fig, gen_fixvars_tex 

M = Mission()
models, modelnames = find_submodels([M], [M.__class__.__name__])
for m in models: 
    gen_model_tex(m, m.__class__.__name__)

with open("tex/Mission.generated.tex", "w") as f:
    for m in models:
        f.write("\n\\subsection{%s}\n\n" % m.__class__.__name__)
        with open("tex/%s.vars.generated.tex" % m.__class__.__name__) as f1:
            lines = f1.readlines()
            f.writelines(lines)
        with open("tex/%s.cnstrs.generated.tex" % m.__class__.__name__) as f2:
            lines = f2.readlines()
            f.writelines(lines)

```
# Fits

![Fit of drag polar data from NACA 652-2412 airfoil](naca652_polars/naca652polarfit1.pdf)

![Fit of power to RPM from Rotax 912 engine](engine/powervsrpmfit.pdf)
![Fit of fuel burn to PRM from Rotax 912 engine](engine/fuelburnvsrpmfit.pdf)


# Solution

Minimizing the max take off weight we arrive at the solution.

```python
#inPDF: replace with tex/sol.generated.tex 
import matplotlib.pyplot as plt
import numpy as np

M.cost = M["MTOW"]
sol = M.solve("mosek")

with open("tex/sol.generated.tex", "w") as f:
    f.write(sol.table(latex=True))
```

# Sweeps

```python
#inPDF: skip
from plotting import plot_sweep
fig, ax = plot_sweep(M, "f", np.linspace(0.1, 0.6, 15), ["MTOW", "b", "AR"])
fig.savefig("mtowvsffuse.pdf")

fig, ax = plot_sweep(M, "W_{pay}", np.linspace(300, 800, 15), ["MTOW", "b", "AR"])
fig.savefig("mtowvswpay.pdf")

fig, ax = plot_sweep(M, "CDA_0", np.linspace(0.001, 0.05, 15), ["MTOW", "b", "AR"])
fig.savefig("mtowvscd0.pdf")

fig, ax = plot_sweep(M, "m_{fac}", np.linspace(1.0, 2, 15), ["MTOW", "b", "AR"])
fig.savefig("mtowvsmfac.pdf")
```

![Variation with fuselage weight fraction](mtowvsffuse.pdf)
![Variation with payload weiht](mtowvswpay.pdf)
![Variation with non wing drag](mtowvscd0.pdf)
![Variation with wing weight margin factor](mtowvsmfac.pdf)
