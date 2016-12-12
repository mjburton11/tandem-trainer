" wing.py "
import numpy as np
from gpkit import Variable, Model, Vectorize

class NACA652Aero(Model):
    "wing aerodynamic model with profile and induced drag"
    def setup(self, static, state):
        "wing drag model"
        Cd = Variable("C_d", "-", "wing drag coefficient")
        CL = Variable("C_L", "-", "lift coefficient")
        e = Variable("e", 0.9, "-", "Oswald efficiency")
        Re = Variable("Re", "-", "Reynold's number")
        cdp = Variable("c_{dp}", "-", "wing profile drag coeff")

        constraints = [
            Cd >= cdp + CL**2/np.pi/static["AR"]/e,
            cdp**18.3487 >= (2.44337e-49*CL**25.264*Re**2.09928
                             + 1.15012e+56*CL**92.7062*Re**-14.1311
                             + 1.56299e-10*CL**0.0617453*Re**-5.1536),
            Re == state["\\rho"]*state["V"]*static["c_{MAC}"]/state["\\mu"],
            ]

        return constraints

