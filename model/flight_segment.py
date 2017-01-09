" flight segment model "
from gpkit import Model, Variable, Vectorize
from breguet_range import BreguetRange
from steady_level_flight import SteadyLevelFlight
from flight_state import FlightState

# pylint: disable=attribute-defined-outside-init, invalid-name

class FlightSegment(Model):
    "flight segment"
    def setup(self, aircraft, N=5, altitude=15000):

        Wfuelfs = Variable("W_{fuel-fs}", "lbf", "flight segment fuel weight")

        self.aircraft = aircraft
        with Vectorize(N):
            W = Variable("W", "lbf", "aircraft weight during flight segment")
            Wstart = Variable("W_{start}", "lbf", "vector-begin weight")
            Wend = Variable("W_{end}", "lbf", "vector-end weight")
            self.fs = FlightState(altitude)
            self.aircraftPerf = self.aircraft.flight_model(self.fs)
            self.slf = SteadyLevelFlight(W, self.fs, self.aircraft,
                                         self.aircraftPerf)
            self.br = BreguetRange(Wstart, Wend, self.aircraftPerf)

        self.submodels = [self.fs, self.aircraftPerf, self.slf, self.br]

        self.constraints = [Wfuelfs >= self.br["W_{fuel}"].sum(),
                            W == (Wstart*Wend)**0.5]

        if N > 1:
            self.constraints.extend([Wend[:-1] >= Wstart[1:]])

        return self.aircraft, self.submodels, self.constraints
