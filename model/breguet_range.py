" breguet_endurance.py "
from gpkit import Model, Variable
from gpkit.tools import te_exp_minus1
from gpkit.constraints.tight import Tight as TCS

class BreguetRange(Model):
    "breguet endurance model"
    def setup(self, Wstart, Wend, perf):
        z_bre = Variable("z_{bre}", "-", "Breguet coefficient")
        Wfuel = Variable("W_{fuel}", "lbf", "segment-fuel weight")
        g = Variable("g", 9.81, "m/s^2", "gravitational acceleration")
        R = Variable("R", "nautical_miles", "range")
        rhofuel = Variable("\\rho_{JetA}", 6.75, "lb/gallon",
                           "Jet A fuel density")

        constraints = [
            TCS([z_bre >= (R*perf["\\dot{m}"]*rhofuel*g/perf["V"]
                           / (Wend*Wstart)**0.5)]),
            Wfuel/Wend >= te_exp_minus1(z_bre, 3),
            Wstart >= Wend + Wfuel
            ]

        return constraints
