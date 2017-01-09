" cap spar "
from gpkit import Model, Variable, Vectorize
from constant_taper_chord import c_bar
from beam import Beam

class ChordSparL(Model):
    "spar loading model"
    def setup(self, static, Wcent):

        Nmax = Variable("N_{max}", 5, "-", "max loading")
        cbar, _ = c_bar(0.5, static.N)
        sigmaai = Variable("\\sigma_{AI}", 207, "MPa", "aluminum max stress")
        kappa = Variable("\\kappa", 0.05, "-", "max tip deflection ratio")

        with Vectorize(static.N-1):
            Mr = Variable("M_r", "N*m", "wing section root moment")

        with Vectorize(static.N):
            qbar = Variable("\\bar{q}", cbar, "-", "normalized loading")

        beam = Beam(static.N, qbar)

        constraints = [
            # dimensionalize moment of inertia and young's modulus
            beam["\\bar{EI}"] <= (8*static["E"]*static["I"]/Nmax
                                  / Wcent/static["b"]**2),
            Mr == (beam["\\bar{M}"][:-1]*Wcent*Nmax*static["b"]/4),
            sigmaai >= Mr/static["S_y"],
            beam["\\bar{\\delta}"][-1] <= kappa,
            ]

        return beam, constraints
