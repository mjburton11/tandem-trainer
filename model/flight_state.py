" flight state of gas powered aircraft "
from gpkit import Model, Variable
from gassolar.environment.air_properties import get_airvars
class FlightState(Model):
    """
    environmental state of aircraft

    inputs
    ------
    latitude: earth latitude [deg]
    altitude: flight altitude [ft]
    percent: percentile wind speeds [%]
    day: day of the year [Jan 1st = 1]
    """
    def setup(self, altitude=12000):

        density, vis = get_airvars(altitude)

        V = Variable("V", "m/s", "true airspeed")
        Vmin = Variable("V_{min}", 10, "m/s", "minimum true airspeed")
        rho = Variable("\\rho", density, "kg/m**3", "air density")
        mu = Variable("\\mu", vis, "N*s/m**2", "dynamic viscosity")
        h = Variable("h", altitude, "ft", "flight altitude")
        href = Variable("h_{ref}", 15000, "ft", "reference altitude")

        constraints = [V >= Vmin,
                       rho == rho,
                       mu == mu,
                       h == h,
                       href == href]

        return constraints
