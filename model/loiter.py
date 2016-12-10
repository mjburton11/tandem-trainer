" loiter segment "
from gpkit import Model, Variable
from flight_segment import FlightSegment

class Loiter(Model):
    "loiter segment"
    def setup(self, aircraft, N=5, altitude=15000):

        fs = FlightSegment(aircraft, N, altitude)

        t = Variable("t", "days", "loitering time")
        constraints = [fs.be["t"] >= t/N]

        return fs, constraints