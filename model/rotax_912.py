" engine_model.py "
from gpkit import Model, Variable, units

class Engine(Model):
    "engine model"
    def setup(self):

        W = Variable("W", "lbf", "Installed/Total engine weight")
        mfac = Variable("m_{fac}", 1.0, "-", "Engine weight margin factor")
        Wrotax912 = Variable("W_{Rotax-912}", 152.6, "lbf",
                             "Installed/Total DF70 engine weight")
        Pslmax = Variable("P_{sl-max}", 98.56, "hp",
                          "Max shaft power at sea level")

        constraints = [W/mfac >= Wrotax912,
                       Pslmax == Pslmax]

        return constraints

    def flight_model(self, state):
        return EnginePerf(self, state)

class EnginePerf(Model):
    "engine performance model"
    def setup(self, static, state):

        Pshaft = Variable("P_{shaft}", "hp", "Shaft power")
        rpm = Variable("RPM", "rpm", "Engine operating RPM")
        Pavn = Variable("P_{avn}", 40, "watts", "Avionics power")
        Ptotal = Variable("P_{total}", "hp", "Total power, avionics included")
        eta_alternator = Variable("\\eta_{alternator}", 0.8, "-",
                                  "alternator efficiency")
        Leng = Variable("L_{eng}", 1, "-", "shaft power loss factor")
        Pshaftmax = Variable("P_{shaft-max}",
                             "hp", "Max shaft power at altitude")
        rpm_max = Variable("RPM_{max}", 5800, "rpm", "Maximum RPM")
        mdotmin = Variable("\\dot{m}_{f-min}", 7.0, "l/hr",
                           "minimum fuel burn rate")
        mdot = Variable("\\dot{m}", "l/hr", "fuel burn rate")

        constraints = [
            (Ptotal/Pshaftmax) == 1.11456*(rpm/rpm_max)**1.63677,
            (mdot/mdotmin)**0.1 == 1.15172*(rpm/rpm_max)**0.233531,
            Pshaftmax/static["P_{sl-max}"] == Leng,
            Pshaftmax >= Ptotal,
            Ptotal >= Pshaft + Pavn/eta_alternator,
            mdot >= mdotmin,
            rpm <= rpm_max]

        return constraints
