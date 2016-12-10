" flight segment model "
from gpkit import Model, Variable, Vectorize
from breguet_range import BreguetRange
from steady_level_flight import SteadyLevelFlight
from flight_state import FlightState

# pylint: disable=attribute-defined-outside-init, invalid-name

class FlightSegment(Model):
    "flight segment"
    def setup(self, aircraft, N=5, altitude=15000):

        self.aircraft = aircraft
        with Vectorize(N):
            self.fs = FlightState(altitude)
            self.aircraftPerf = self.aircraft.flight_model(self.fs)
            self.slf = SteadyLevelFlight(self.fs, self.aircraft,
                                         self.aircraftPerf)
            self.br = BreguetRange(self.aircraftPerf)

        self.submodels = [self.fs, self.aircraftPerf, self.slf, self.br]
        Wfuelfs = Variable("W_{fuel-fs}", "lbf", "flight segment fuel weight")

        self.constraints = [Wfuelfs >= self.br["W_{fuel}"].sum()]

        if N > 1:
            self.constraints.extend([self.aircraftPerf["W_{end}"][:-1] >=
                                     self.aircraftPerf["W_{start}"][1:]])

        return self.aircraft, self.submodels, self.constraints
