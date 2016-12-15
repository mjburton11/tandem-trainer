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
fig, ax = plot_sweep(M, "f_{structures}", np.linspace(0.5, 0.8, 15), ["MTOW"], ylim=[0,3000])
fig.savefig("mtowvsfstruct.pdf")

fig, ax = plot_sweep(M, "AR", np.linspace(5, 30, 15), ["MTOW"], ylim=[0,3000])
fig.savefig("mtowvsAR.pdf")

fig, ax = plot_sweep(M, "W_{pay}", np.linspace(300, 800, 15), ["MTOW"], ylim=[0,3000])
fig.savefig("mtowvswpay.pdf")

fig, ax = plot_sweep(M, "CDA_0", np.linspace(0.001, 0.05, 15), ["MTOW"], ylim=[0,3000])
fig.savefig("mtowvscd0.pdf")
```

![Max take off weight vs structural fraction](mtowvsfstruct.pdf)
![Max take off weight vs aspect ratio](mtowvsAR.pdf)
![Max take off weight vs payload weight](mtowvswpay.pdf)
![Max take off weight vs non wing drag coefficient](mtowvscd0.pdf)
