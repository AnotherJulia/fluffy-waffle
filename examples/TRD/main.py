from core import Environment, Factory
from patient import Patient
from utilities import generate_networkx_graph

general_capacity = 240
left = 67



if __name__ == '__main__':
    env = Environment(time=0, dt=1)  # dt = 1week

    env.create_state(slug="intake", description="Patients coming into the TRD care pathway", depth=0, env=env)
    env.create_state(slug="remission", description="Patients coming out of the pathway", depth=0, env=env)
    env.create_state(slug="relapse", description="Patients relapsing from the remission bubble", depth=0, env=env)
    env.create_state(slug="recovery", description="Patients relapsing from the remission bubble", depth=0, env=env)

    # TODO: ADD STATE SUICIDE / DEATH
    # TODO: CURRENTLY = RELAPSE -> INTAKE; SHOULD CHANGE THIS TO SOMETHING MORE ACCURATE

    env.create_connection("remission", "recovery")
    env.create_connection("remission", "relapse")
    env.create_connection("recovery", "relapse")
    env.create_connection("relapse", "intake")

    # LEVEL 1 : AUGMENTED THERAPIES

    env.create_step(slug="ad", description="AD Treatment, 4wks", capacity=30, config="../../config/ad_config.json",
                    depth=1, env=env)
    env.create_connection(start_slug="intake", end_slug="ad")
    env.create_connection("ad", "remission")

    env.create_step(slug="ap", description="AP treatment, 4wks", capacity=20, config="../../config/ap_config.json",
                    depth=1, env=env)
    env.create_connection(start_slug="intake", end_slug="ap")
    env.create_connection("ap", "remission")

    env.create_step(slug="ad_ap", description="AP+AD treatment, 4wks", capacity=30,
                    config="../../config/ad_ap_config.json", depth=1, env=env)
    env.create_connection(start_slug="intake", end_slug="ad_ap")
    env.create_connection("ad_ap", "remission")

    # LEVEL 2: ESKETAMINE TREATMENT

    env.create_step(slug="esketamine", description="Esketamine treatment, 4wks", capacity=60,
                    config="../../config/esketamine_config.json", depth=2, env=env)
    env.create_connection(start_slug="ad", end_slug="esketamine")
    env.create_connection(start_slug="ap", end_slug="esketamine")
    env.create_connection(start_slug="ad_ap", end_slug="esketamine")

    # LEVEL 3: ECT

    env.create_step(slug="ect", description="ECT Treatment, 28wks", capacity=15, config="../../config/ect_config.json",
                    depth=3, env=env)
    env.create_connection("esketamine", "ect")
    env.create_connection("ect", "remission")
    env.create_connection("ect", "ad")

    generate_networkx_graph(env)

    factory = Factory(config="../../config/agent_params.json", agent_class_type=Patient)
    env.connect_factory(factory)

    env.create_agent("intake", 1)

    # Set up the initial conditions of the pathway
    env.set_patient_rate(3)         # this means 2 patients a week coming into the trd pathway

    env.run(until=500, verbose=True)
    #
    states = ["intake", "remission", "relapse"]
    steps = ["ad", "ap", "ad_ap", "esketamine", "ect"]
    env.plot_occupancies(steps)
    env.plot_waiting_queues(steps)

    patient = env.agents[0]
    print(patient.medical_history)
