" cap spar "
from gpkit import Model, Variable, Vectorize
from chord_spar_loading import ChordSparL

class CapSpar(Model):
    "cap spar model"
    def setup(self, b, cave, tau, N=5):
        self.N = N

        # phyiscal properties
        rhoai = Variable("\\rho_{AI}", 2.7, "g/cm^3", "density of aluminum")
        E = Variable("E", 70, "GPa", "Youngs modulus of aluminum")

        t = Variable("t", "in", "spar cap thickness")
        hin = Variable("h_{in}", "in", "inner spar height")
        w = Variable("w", "in", "spar width")
        I = Variable("I", "m^4", "spar x moment of inertia")
        Sy = Variable("S_y", "m**3", "section modulus")

        W = Variable("W", "lbf", "spar weight")
        w_lim = Variable("w_{lim}", 0.15, "-", "spar width to chord ratio")
        g = Variable("g", 9.81, "m/s^2", "gravitational acceleration")

        constraints = [I <= 2*w*t*(hin/2)**2,
                       W >= rhoai*w*t*b*g,
                       w <= w_lim*cave,
                       cave*tau >= hin + 2*t,
                       Sy*(hin + t) <= I,
                      ]

        return constraints

    def loading(self, Wcent):
        return ChordSparL(self, Wcent)
