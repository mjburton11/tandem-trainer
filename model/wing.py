" wing.py "
import numpy as np
from gpkit import Variable, Model, Vectorize
from capspar import CapSpar
from constant_taper_chord import c_bar
from naca652_aero import NACA652Aero
from wing_skin import WingSkin

class Wing(Model):
    "The thing that creates the lift"
    def setup(self, N=5, lam=0.8):

        W = Variable("W", "lbf", "weight")
        mfac = Variable("m_{fac}", 1.5, "-", "wing weight margin factor")
        S = Variable("S", "ft^2", "surface area")
        AR = Variable("AR", "-", "aspect ratio")
        b = Variable("b", "ft", "wing span")
        tau = Variable("\\tau", 0.15, "-", "airfoil thickness ratio")
        croot = Variable("c_{root}", "ft", "root chord")
        cmac = Variable("c_{MAC}", "ft", "mean aerodynamic chord")
        lamw = Variable("\\lambda", lam, "-", "wing taper ratio")
        cb, _ = c_bar(lam, N)
        with Vectorize(N):
            cbar = Variable("\\bar{c}", cb, "-",
                            "normalized chord at mid element")
        with Vectorize(N-1):
            cbave = Variable("\\bar{c}_{ave}", (cb[1:]+cb[:-1])/2, "-",
                             "normalized mid section chord")
            cave = Variable("c_{ave}", "ft", "mid section chord")

        constraints = [b**2 == S*AR,
                       lamw == lamw,
                       cbar == cbar,
                       cave == cbave*S/b,
                       croot == S/b*cb[0],
                       cmac == S/b]

        self.spar = CapSpar(b, cave, tau, N)
        self.skin = WingSkin(S, croot, b)
        self.components = [self.spar, self.skin]

        constraints.extend([W/mfac >= sum(c["W"] for c in self.components)])

        return self.components, constraints

    def flight_model(self, state):
        return NACA652Aero(self, state)

    def loading(self, Wcent):
        return WingLoading(self, Wcent)

class WingLoading(Model):
    "wing loading cases"
    def setup(self, wing, Wcent):

        spar = wing.spar.loading(Wcent)
        skin = wing.skin.loading()
        loading = [spar, skin]

        return loading
