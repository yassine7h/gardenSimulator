from Simulation import Simulation

simulation = Simulation()
simulation.charger_configuration("configs/Pootager_Cas_4.xml")
simulation.simulate(logging=True)
simulation.generate_resulte(filename="result.xml")

