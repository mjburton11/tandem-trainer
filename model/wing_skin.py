" wing skin "
from gpkit import Model, Variable

class WingSkin(Model):
    "wing skin model"
    def setup(self, S, croot, b):

        rhoai = Variable("\\rho_{AI}", 2.7, "g/cm^3", "density of aluminum")
        W = Variable("W", "lbf", "wing skin weight")
        g = Variable("g", 9.81, "m/s^2", "gravitational acceleration")
        t = Variable("t", "in", "wing skin thickness")
        tmin = Variable("t_{min}", 0.05, "in", "minimum thickness")
        Jtbar = Variable("\\bar{J/t}", 0.018232, "1/mm",
                         "torsional moment of inertia")

        constraints = [W >= rhoai*S*2*t*g,
                       Jtbar == Jtbar,
                       t >= tmin,
                       b == b,
                       croot == croot]

        return constraints

    def loading(self):
        return WingSkinL(self)

class WingSkinL(Model):
    "wing skin loading model for torsional loads in skin"
    def setup(self, static):

        tauai = Variable("\\tau_{AI}", 207, "MPa", "torsional stress limit")
        Cmw = Variable("C_{m_w}", 0.121, "-", "negative wing moment coefficent")
        rhosl = Variable("\\rho_{sl}", 1.225, "kg/m^3",
                         "air density at sea level")
        Vne = Variable("V_{NE}", 150, "m/s", "never exceed vehicle speed")
        Nmax = Variable("N_{max}", 5, "-", "safety load factor")

        constraints = [
            tauai >= (Nmax/static["\\bar{J/t}"]/(static["c_{root}"])**2
                      / static["t"]*Cmw*static["S"]*rhosl*Vne**2)]

        return constraints
