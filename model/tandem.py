" Simple Gas Powered Aircraft Model"
import numpy as np
from loiter import Loiter
from flight_segment import FlightSegment
from gpkit import Model, Variable
from naca652_aero import NACA652Aero
from rotax_912 import Engine
from wing import Wing
from gpkitmodels.helpers import summing_vars
from cylindrical_fuselage import Fuselage

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
        self.fuse = static.fuselage.flight_model(state)
        dynamic = [self.wing, self.engine, self.fuse]

        CD = Variable("C_D", "-", "aircraft drag coefficient")
        cda0 = Variable("CDA_0", 0.025, "-", "non-wing drag coefficient")
        etaprop = Variable("\\eta_{prop}", 0.7, "-", "propulsive efficiency")

        constraints = [CD >= cda0 + self.wing["C_d"] + self.fuse["C_d"],
                       etaprop == etaprop
                      ]

        return constraints, dynamic

class Mission(Model):
    "create a mission for the flight"
    def setup(self):

        mtow = Variable("MTOW", "lbf", "max take off weight")
        Wfueltot = Variable("W_{fuel-tot}", "lbf", "total fuel weight")
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
            # tandem.fuselage["W"] >= mtow*tandem.fuselage["f"]
            ]

        return tandem, self.mission, loading, constraints

if __name__ == "__main__":
    M = Mission()
    M.cost = M["MTOW"]
    sol = M.solve("mosek")
