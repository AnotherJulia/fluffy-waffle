from core import Environment, Factory
from examples.TRD.patient import Patient
from examples.TRD.patient_esk import PatientEsk
from utilities import Capacity, generate_networkx_graph


def run_simulation(simulation_id, config, cap_dist, simulation_duration):
    
    env = Environment(time=0, dt=1)

    # states
    for state in config['states']:
        env.create_state(**{k: state[k] for k in ['slug', 'description', 'depth']}, env=env)

    # steps
    capacity = Capacity(cap_dist)
    # if simulation_id == 0:
    #     print(f"{capacity}")

    for step in config['steps']:
        step['capacity'] = capacity.retrieve_capacity(step['slug'])
        env.create_step(**{k: step[k] for k in ['slug', 'description', 'capacity', 'config', 'depth']}, env=env)

    # state connections
    for state in config['states']:
        for connection in state.get('connections', []):
            env.create_connection(start_slug=state['slug'], end_slug=connection)

    # step connections
    for step in config['steps']:
        for connection in step.get('connections', []):
            env.create_connection(start_slug=step['slug'], end_slug=connection)
    
    is_esketamine_there = False
    for bubble in env.bubbles:
        if bubble.slug == "esketamine":
            is_esketamine_there = True

    if is_esketamine_there:
        factory = Factory(config=config['agent_config'], agent_class_type=PatientEsk)
    else:
        factory = Factory(config=config['agent_config'], agent_class_type=Patient)

    env.connect_factory(factory)
    
    # if simulation_id == 0:
    #     generate_networkx_graph(env)        

    # setup initial patients
    for agent, count in config['initial_agents'].items():
        env.create_agent(agent, count)

    env.set_patient_rate(config['patient_rate'])
    env.run(until=simulation_duration, verbose=False)

    # env.plot_occupancies(["relapse"])

    from core import SimulationInstance
    instance = SimulationInstance(run_id=simulation_id, agents=env.agents,run_data=env.data, environment=env)
    return instance
