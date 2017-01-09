" Simple Gas Powered Aircraft Model"
import numpy as np
from loiter import Loiter
from flight_segment import FlightSegment
from gpkit import Model, Variable
from naca652_aero import NACA652Aero
from rotax_912 import Engine
from wing import Wing
from gpkitmodels.helpers import summing_vars

class Aircraft(Model):
    "vehicle"
    def setup(self):

        self.wing = Wing()
        self.engine = Engine()
        self.fuselage = Fuselage()

        self.components = [self.wing, self.engine, self.fuselage]

        Wpay = Variable("W_{pay}", 700, "lbf", "payload")
        Wzfw = Variable("W_{zfw}", "lbf", "zero fuel weight")

        constraints = [Wzfw >= sum(summing_vars(self.components, "W")) + Wpay]

        return self.components, constraints

    def flight_model(self, state):
        return AircraftPerf(self, state)

    def loading(self, Wcent):
        return AircraftLoading(self, Wcent)

class Fuselage(Model):
    "fuselage weight"
    def setup(self):

        W = Variable("W", "lbf", "fuselage weight")
        f = Variable("f", 0.3, "-", "fraction of total weight")

        constraints = [W == W,
                       f == f]

        return constraints

class AircraftLoading(Model):
    "aircraft loading model"
    def setup(self, aircraft, Wcent):

        loading = [aircraft.wing.loading(Wcent)]

        return loading

class AircraftPerf(Model):
    "aircraft performance"
    def setup(self, static, state):

        self.wing = static.wing.flight_model(state)
        self.engine = static.engine.flight_model(state)
        dynamic = [self.wing, self.engine]

        CD = Variable("C_D", "-", "aircraft drag coefficient")
        cda0 = Variable("CDA_0", 0.025, "-", "non-wing drag coefficient")
        etaprop = Variable("\\eta_{prop}", 0.7, "-", "propulsive efficiency")

        constraints = [CD >= cda0 + self.wing["C_d"],
                       etaprop == etaprop
                      ]

        return constraints, dynamic

class Mission(Model):
    "create a mission for the flight"
    def setup(self):

        mtow = Variable("MTOW", "lbf", "max take off weight")
        Wfueltot = Variable("W_{fuel-tot}", "lbf", "total fuel weight")
        Rmin = Variable("R_{min}", 400.0, "nautical_miles",
                        "minimum flight range")
        Wcent = Variable("W_{cent}", "lbf", "aircraft center weight")

        tandem = Aircraft()

        N = 5
        fs = FlightSegment(tandem, N=N)
        self.mission = [fs]

        loading = AircraftLoading(tandem, Wcent)

        constraints = [
            mtow == self.mission[0]["W_{start}"][0],
            mtow >= Wfueltot + tandem["W_{zfw}"],
            Wfueltot >= sum([fs["W_{fuel-fs}"] for fs in self.mission]),
            self.mission[-1]["W_{end}"][-1] >= tandem["W_{zfw}"],
            Wcent >= tandem.engine["W"] + tandem["W_{pay}"] + Wfueltot,
            Rmin/N <= fs["R"],
            tandem.fuselage["W"] >= mtow*tandem.fuselage["f"]
            ]

        return tandem, self.mission, loading, constraints

if __name__ == "__main__":
    M = Mission()
    M.cost = M["MTOW"]
    sol = M.solve("mosek")
