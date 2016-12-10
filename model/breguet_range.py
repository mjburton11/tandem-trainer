" breguet_endurance.py "
from gpkit import Model, Variable
from gpkit.tools import te_exp_minus1
from gpkit.constraints.tight import Tight as TCS

class BreguetRange(Model):
    "breguet endurance model"
    def setup(self, perf):
        z_bre = Variable("z_{bre}", "-", "Breguet coefficient")
        Wfuel = Variable("W_{fuel}", "lbf", "segment-fuel weight")
        g = Variable("g", 9.81, "m/s^2", "gravitational acceleration")
        R = Variable("R", "nautical_miles", "range")

        constraints = [
            TCS([z_bre >= (perf["P_{total}"]*R*perf["BSFC"]*g/perf["V"]
                           / (perf["W_{end}"]*perf["W_{start}"])**0.5)]),
            Wfuel/perf["W_{end}"] >= te_exp_minus1(z_bre, 3),
            perf["W_{start}"] >= perf["W_{end}"] + Wfuel
            ]

        return constraints
