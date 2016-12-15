" Simple Gas Powered Aircraft Model"
import numpy as np
from loiter import Loiter
from flight_segment import FlightSegment
from gpkit import Model, Variable
from naca652_aero import NACA652Aero
from rotax_912 import Engine
from gpkitmodels.aircraft.GP_submodels.wing import WingAero

class Aircraft(Model):
    "vehicle"
    def setup(self):

        self.wing = Wing()
        self.engine = Engine()

        Wstructures = Variable("W_{structures}", "lbf", "structural weight")
        fstructures = Variable("f_{structures}", 0.7, "-",
                               "fractional structural weight")
        Wpay = Variable("W_{pay}", 500, "lbf", "payload")
        Wzfw = Variable("W_{zfw}", "lbf", "zero fuel weight")

        constraints = [Wstructures == Wstructures,
                       fstructures == fstructures,
                       Wzfw >= Wstructures + Wpay]

        return self.wing, constraints

    def flight_model(self, state):
        return AircraftPerf(self, state)

class Wing(Model):
    "wing model"
    def setup(self):

        S = Variable("S", "ft**2", "planform area")
        b = Variable("b", "ft", "wing span")
        cmac = Variable("c_{MAC}", "ft", "mean aerodynamic chord")
        AR = Variable("AR", 27, "-", "aspect ratio")

        constraints = [b**2 == S*AR,
                       cmac == S/b]

        return constraints

    def flight_model(self, state):
        return NACA652Aero(self, state)

class AircraftPerf(Model):
    "aircraft performance"
    def setup(self, static, state):

        self.wing = static.wing.flight_model(state)
        self.engine = static.engine.flight_model(state)
        dynamic = [self.wing, self.engine]

        CD = Variable("C_D", "-", "aircraft drag coefficient")
        cda0 = Variable("CDA_0", 0.005, "-", "non-wing drag coefficient")
        Wstart = Variable("W_{start}", "lbf", "vector-begin weight")
        Wend = Variable("W_{end}", "lbf", "vector-end weight")
        etaprop = Variable("\\eta_{prop}", 0.7, "-", "propulsive efficiency")

        constraints = [CD >= cda0 + self.wing["C_d"],
                       Wstart == Wstart,
                       Wend == Wend,
                       etaprop == etaprop
                      ]

        return constraints, dynamic

class Mission(Model):
    "create a mission for the flight"
    def setup(self):

        gassimple = Aircraft()
        N = 5

        fs = FlightSegment(gassimple, N=N)
        mission = [fs]

        mtow = Variable("MTOW", "lbf", "max take off weight")
        Wfueltot = Variable("W_{fuel-tot}", "lbf", "total fuel weight")
        Rmin = Variable("R_{min}", 400.0, "nautical_miles",
                        "minimum flight range")

        constraints = [
            mtow == mission[0]["W_{start}"][0],
            mtow >= Wfueltot + gassimple["W_{zfw}"],
            Wfueltot >= sum([fs["W_{fuel-fs}"] for fs in mission]),
            mission[-1]["W_{end}"][-1] >= gassimple["W_{zfw}"],
            gassimple["W_{structures}"] >= mtow*gassimple["f_{structures}"],
            Rmin/N <= fs["R"]
            ]

        return gassimple, mission, constraints

if __name__ == "__main__":
    M = Mission()
    M.cost = M["MTOW"]
    sol = M.solve("mosek")
