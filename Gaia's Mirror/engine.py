# gaia_mirror/engine.py

import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
import asyncio

# Configure logging for the engine module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Engine] - %(levelname)s - %(message)s')

class EngineError(Exception):
    """Custom exception for errors within the modeling engine."""
    pass

class SystemNode:
    """
    Represents a single Earth system (e.g., Atmosphere, Biosphere) within the interconnected graph.
    Each node has its own state and an internal model to update that state based on inputs.
    """
    def __init__(self, node_id: str, name: str, node_type: str, initial_state: Dict[str, Any]):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type # e.g., 'Atmosphere', 'Biosphere', 'Economy'
        self._state: Dict[str, Any] = initial_state
        self._incoming_inputs: Dict[str, List[Any]] = {} # To store inputs from connected nodes/data
        self._model: Optional[Callable[[Dict, Dict], Dict]] = None # Internal model function

        logging.debug(f"Node '{self.name}' ({self.node_id}) of type '{self.node_type}' initialized.")

    def set_model(self, model_function: Callable[[Dict, Dict], Dict]):
        """Assigns an internal model function to this node."""
        self._model = model_function
        logging.debug(f"Model assigned to node '{self.name}'.")

    def receive_input(self, input_key: str, data: Any):
        """Receives input data from an edge or direct injection."""
        if input_key not in self._incoming_inputs:
            self._incoming_inputs[input_key] = []
        self._incoming_inputs[input_key].append(data)
        logging.debug(f"Node '{self.name}' received input for '{input_key}'.")

    def _process_inputs(self) -> Dict[str, Any]:
        """
        Aggregates and processes all received inputs for the current timestep.
        This could involve averaging, summing, or more complex fusion logic.
        """
        processed_inputs = {}
        for key, values in self._incoming_inputs.items():
            # Simple aggregation: take the last value, or average if multiple.
            if values:
                if isinstance(values[0], (int, float)) and len(values) > 1:
                    processed_inputs[key] = sum(values) / len(values)
                else:
                    processed_inputs[key] = values[-1] # Take the latest
            
            # Clear inputs after processing for next timestep
            self._incoming_inputs[key] = [] 
        return processed_inputs

    async def update_state(self, timestep: int, external_interventions: List[Dict] = None):
        """
        Updates the node's state using its internal model, incorporating inputs
        and external interventions.
        """
        if self._model is None:
            raise EngineError(f"Node '{self.name}' has no model assigned.")

        processed_inputs = self._process_inputs()
        
        # Apply interventions directly to the state or feed into the model
        current_state_copy = self._state.copy()
        if external_interventions:
            for intervention in external_interventions:
                if intervention.get("target_node") == self.node_id:
                    # Example: direct state modification, or feeding into processed_inputs
                    # Real implementation would be more nuanced based on intervention type
                    logging.info(f"Applying intervention to '{self.name}': {intervention}")
                    current_state_copy.update(intervention.get("state_modifications", {}))

        # Run the internal model asynchronously if it supports it, or use a thread pool
        # For pseudocode, we'll assume it's callable as a regular function for now.
        new_state_segment = await asyncio.to_thread(self._model, current_state_copy, processed_inputs)
        
        # Merge new state segment back into the node's full state
        self._state.update(new_state_segment)
        logging.debug(f"Node '{self.name}' state updated at timestep {timestep}.")

    def get_state(self) -> Dict[str, Any]:
        """Returns the current state of the node."""
        return self._state.copy()

    def get_output(self, output_key: str) -> Any:
        """Provides specific output data from its state for connected nodes."""
        return self._state.get(output_key)

class SystemEdge:
    """
    Represents a directional causal link between two SystemNodes.
    """
    def __init__(self,
                 source_node_id: str,
                 target_node_id: str,
                 flow_type: str, # e.g., 'carbon_flow', 'water_cycle', 'economic_influence'
                 output_key_from_source: str, # Which state variable to get from source
                 input_key_to_target: str, # Which input key to set on target
                 transformation_func: Optional[Callable[[Any], Any]] = None):
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.flow_type = flow_type
        self.output_key_from_source = output_key_from_source
        self.input_key_to_target = input_key_to_target
        self.transformation_func = transformation_func if transformation_func else lambda x: x

    def propagate(self, source_output: Any) -> Any:
        """Transforms and propagates data across the edge."""
        return self.transformation_func(source_output)

class InterconnectedSystemsModelingEngine:
    """
    The core computational module that implements a novel modeling paradigm
    to capture non-linear relationships, feedback loops, and emergent properties
    between Earth's systems. Orchestrates SystemNodes and SystemEdges.
    """
    def __init__(self, data_store_client: Any = None): # data_store_client would get historical/current data
        self.nodes: Dict[str, SystemNode] = {}
        self.edges: List[SystemEdge] = []
        self.timestep_duration = timedelta(days=30) # Example: Monthly timesteps
        self.current_simulation_id: Optional[str] = None
        self.data_store_client = data_store_client # Placeholder for interaction with ingested data
        logging.info("InterconnectedSystemsModelingEngine initialized.")

    def add_node(self, node: SystemNode):
        """Adds a system node to the engine."""
        if node.node_id in self.nodes:
            raise EngineError(f"Node with ID '{node.node_id}' already exists.")
        self.nodes[node.node_id] = node
        logging.info(f"Added node: {node.name} ({node.node_id}).")

    def add_edge(self, edge: SystemEdge):
        """Adds a causal link between two nodes."""
        if edge.source_node_id not in self.nodes or edge.target_node_id not in self.nodes:
            raise EngineError(f"Edge references unknown node(s): {edge.source_node_id} or {edge.target_node_id}.")
        self.edges.append(edge)
        logging.info(f"Added edge: {edge.source_node_id} -> {edge.target_node_id} ({edge.flow_type}).")

    async def _initialize_system_state(self, initial_state_data: Optional[Dict[str, Any]] = None):
        """
        Initializes the state of all nodes, optionally from specific data
        or by querying the data store for the latest global state.
        """
        logging.info("Initializing system state...")
        if initial_state_data:
            for node_id, state in initial_state_data.items():
                if node_id in self.nodes:
                    self.nodes[node_id]._state = state
                    logging.debug(f"Node '{node_id}' initialized with provided state.")
                else:
                    logging.warning(f"Initial state provided for unknown node ID: {node_id}.")
        else:
            # Pseudocode: Query data_store_client for latest aggregated data (from ingest.py)
            # This would aggregate recent data from ingest.py outputs.
            logging.info("Querying data store for latest global state (MOCK).")
            # For demonstration, set some default initial states if not overridden
            if 'atmosphere' in self.nodes and not self.nodes['atmosphere']._state:
                self.nodes['atmosphere']._state = {"co2_ppm": 420.0, "temperature_c": 15.0}
            if 'hydrosphere' in self.nodes and not self.nodes['hydrosphere']._state:
                self.nodes['hydrosphere']._state = {"ocean_ph": 8.1, "sea_level_cm": 0.0}
            if 'biosphere' in self.nodes and not self.nodes['biosphere']._state:
                self.nodes['biosphere']._state = {"biodiversity_index": 0.75, "forest_cover_percent": 30.0, "carbon_sink_capacity": 0.03}
            if 'geosphere' in self.nodes and not self.nodes['geosphere']._state:
                self.nodes['geosphere']._state = {"resource_availability_index": 0.9}
            if 'economy' in self.nodes and not self.nodes['economy']._state:
                self.nodes['economy']._state = {"gdp_total_usd": 90e12, "emissions_intensity": 0.5, "annual_carbon_emissions": 35.0}
            if 'sociopolitical' in self.nodes and not self.nodes['sociopolitical']._state:
                self.nodes['sociopolitical']._state = {"global_stability_index": 0.8, "population": 8e9}
            logging.info("System state initialized with mock data (or existing node states).")


    async def run_system_model(self,
                               initial_state_data: Optional[Dict[str, Any]] = None,
                               interventions: List[Dict] = None,
                               duration_years: int = 10,
                               simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the interconnected system model for a specified duration, applying interventions.
        Returns the final predicted state of the Earth systems.
        """
        self.current_simulation_id = simulation_id if simulation_id else f"sim_run_{datetime.utcnow().timestamp()}"
        logging.info(f"Starting simulation '{self.current_simulation_id}' for {duration_years} years.")

        await self._initialize_system_state(initial_state_data)
        
        if interventions is None:
            interventions = []

        # Number of timesteps
        total_timesteps = int((duration_years * 365) / self.timestep_duration.days)
        
        # Store historical states for causal tracing and debugging
        # In a real system, this might store summaries or key changes, not full states for every timestep
        historical_states = []

        for timestep in range(total_timesteps):
            logging.debug(f"Simulation '{self.current_simulation_id}' - Timestep {timestep}/{total_timesteps}")

            # 1. Store current state (before updates)
            current_overall_state = {node_id: node.get_state() for node_id, node in self.nodes.items()}
            historical_states.append({"timestep": timestep, "state": current_overall_state})

            # 2. Apply interventions for current timestep
            current_timestep_interventions = [
                i for i in interventions if i.get("start_timestep", 0) <= timestep and
                                            i.get("end_timestep", total_timesteps) >= timestep
            ]

            # 3. Propagate data across edges to 'prime' target nodes with inputs
            for edge in self.edges:
                source_node = self.nodes[edge.source_node_id]
                target_node = self.nodes[edge.target_node_id]
                
                source_output = source_node.get_output(edge.output_key_from_source)
                if source_output is not None:
                    propagated_data = edge.propagate(source_output)
                    target_node.receive_input(edge.input_key_to_target, propagated_data)
                    logging.debug(f"Propagated {edge.flow_type} from {source_node.name} to {target_node.name}.")

            # 4. Update states of all nodes concurrently
            update_tasks = [node.update_state(timestep, current_timestep_interventions) for node in self.nodes.values()]
            await asyncio.gather(*update_tasks)
            
            # (Optional) Implement a convergence check or stable state detection here
        
        final_state = {node_id: node.get_state() for node_id, node in self.nodes.items()}
        logging.info(f"Simulation '{self.current_simulation_id}' completed. Final state calculated.")

        # Aggregate key metrics for simulator.py/optimizer.py
        aggregated_metrics = self._aggregate_final_metrics(final_state)
        # Store historical_states (or a summary) for causal tracing
        # This would be passed to utils/causal_tracing.py
        
        return aggregated_metrics

    def _aggregate_final_metrics(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregates key metrics from the final state of all nodes into a single dictionary
        for easier consumption by simulator.py and optimizer.py.
        This is where the 'cascading, second and third-order effects' become apparent.
        """
        metrics = {}
        
        # Example aggregation logic:
        # Assuming atmosphere node always exists and has these keys
        atm_state = final_state.get('atmosphere', {})
        metrics['global_temperature_change_c'] = atm_state.get('temperature_c', 15.0) - 14.8 # Baseline temp change
        metrics['co2_ppm_final'] = atm_state.get('co2_ppm', 415.0)
        
        # Hydrosphere
        hydro_state = final_state.get('hydrosphere', {})
        metrics['ocean_ph_final'] = hydro_state.get('ocean_ph', 8.15)
        metrics['sea_level_rise_cm'] = hydro_state.get('sea_level_cm', 0.0)

        # Biosphere
        bio_state = final_state.get('biosphere', {})
        metrics['biodiversity_index'] = bio_state.get('biodiversity_index', 0.8)
        metrics['forest_cover_percent'] = bio_state.get('forest_cover_percent', 31.0)
        
        # Economy
        econ_state = final_state.get('economy', {})
        socio_state = final_state.get('sociopolitical', {}) # Needed for population
        metrics['gdp_per_capita'] = econ_state.get('gdp_total_usd', 0) / socio_state.get('population', 1) if socio_state.get('population', 1) > 0 else 0
        metrics['emissions_intensity_final'] = econ_state.get('emissions_intensity', 0.0)

        # Sociopolitical
        metrics['social_stability_index'] = socio_state.get('global_stability_index', 0.0)
        metrics['population_final'] = socio_state.get('population', 0.0)

        # Derived high-level metrics for ethics/optimizer
        metrics['human_wellbeing_index'] = (metrics['gdp_per_capita'] / 100000 + metrics['social_stability_index'] * 2 + metrics['biodiversity_index']) / 4 # Simplified average
        
        # Pass through ethical metrics for simulator/optimizer to use directly
        # These would be derived more rigorously from the overall state
        metrics["_ethical_metrics"] = {
            "simulated_wellbeing": metrics['human_wellbeing_index'],
            "simulated_harm": {"loss_of_life": 0, "suffering_index": 0.0}, # Needs more complex derivation based on state changes
            "simulated_distribution": {"favors_privileged": 0.1, "disadvantages_vulnerable": 0.1}, # Needs more complex derivation
            "simulated_env_impact": {
                "irreversible_degradation_risk": 1 - metrics['biodiversity_index'] if metrics['biodiversity_index'] < 0.5 else 0.0, # High risk if biodiversity is low
                "critical_ecosystem_collapse_risk": 1 - metrics['biodiversity_index'] if metrics['biodiversity_index'] < 0.2 else 0.0
            }
        }
        return metrics

# --- Mock/Placeholder Node Models (for demonstration) ---
# In a real system, these would be complex, data-driven, potentially ML-based models.
# They would leverage data from ingest.py (via data store) for parameters and learning.

def atmosphere_model(current_state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Simulates atmospheric dynamics (CO2, temperature).
    Influenced by biosphere (carbon sinks), economy (emissions).
    """
    new_state = current_state.copy()
    
    # Baseline CO2 increase/decrease
    co2_change_per_month = 0.05 # ppm/month (slight increase if no other factors)

    # Carbon flow from economy (emissions)
    annual_economic_emissions_gt = inputs.get('economic_emissions', 0.0)
    # Convert GtCO2 to ppm (approx 1 GtCO2 = 0.125 ppm, simplified for monthly)
    co2_change_per_month += (annual_economic_emissions_gt / 12) * 0.1

    # Carbon sink from biosphere
    biosphere_carbon_sink_gt = inputs.get('biosphere_carbon_sink', 0.0)
    co2_change_per_month -= (biosphere_carbon_sink_gt / 12) * 0.1 # Simplified effect

    new_state['co2_ppm'] = max(280.0, new_state['co2_ppm'] + co2_change_per_month) # CO2 doesn't go below pre-industrial
    
    # Temperature sensitivity to CO2 (simplified) and other factors
    temp_change_from_co2 = (new_state['co2_ppm'] - 280.0) * 0.001 # Simplified climate sensitivity, based on pre-industrial
    new_state['temperature_c'] = 14.0 + temp_change_from_co2 # Baseline 14C

    return new_state

def hydrosphere_model(current_state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Simulates hydrosphere dynamics (ocean pH, sea level).
    Influenced by atmosphere (CO2 absorption, temperature).
    """
    new_state = current_state.copy()
    
    # Ocean acidification from atmospheric CO2
    atmospheric_co2 = inputs.get('atmospheric_co2', 415.0)
    # Simple linear model: for every 10 ppm increase from 280, pH drops by 0.005
    new_state['ocean_ph'] = 8.2 - ((atmospheric_co2 - 280.0) / 10) * 0.0005 # Baseline 8.2

    # Sea level rise from global temperature (ice melt)
    global_temperature = inputs.get('global_temperature', 14.8)
    new_state['sea_level_cm'] += (global_temperature - 14.8) * 0.25 # cm/month for every degree above baseline

    return new_state

def biosphere_model(current_state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Simulates biosphere dynamics (biodiversity, forest cover, carbon sink).
    Influenced by atmosphere (temperature), sociopolitical (deforestation policies).
    """
    new_state = current_state.copy()

    # Impact of temperature on biodiversity
    atmospheric_temperature = inputs.get('atmospheric_temperature', 14.8)
    new_state['biodiversity_index'] = max(0.1, new_state['biodiversity_index'] - (atmospheric_temperature - 14.8) * 0.002) # Simplified extinction rate

    # Impact of sociopolitical actions on forest cover
    deforestation_policy_impact = inputs.get('deforestation_impact', 0.0) # from sociopolitical, e.g., -0.1 for deforestation, +0.1 for reforestation
    new_state['forest_cover_percent'] += deforestation_policy_impact # % change per month
    new_state['forest_cover_percent'] = max(10.0, min(60.0, new_state['forest_cover_percent'])) # Realistic bounds

    # Carbon sink based on forest cover (simplified)
    # Assuming 1% forest cover can sink X GtCO2/year
    new_state['carbon_sink_capacity'] = (new_state['forest_cover_percent'] / 100) * 4 # Example: 4 GtCO2/year for 100% cover

    return new_state

def geosphere_model(current_state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Simulates geosphere dynamics (very slow, mostly static for short simulations).
    Might include volcanic activity, tectonic shifts, but for now, mainly passive elements
    or resources for other systems.
    """
    new_state = current_state.copy()
    # No dynamic changes for this simple mock.
    # In reality: resource depletion, geological hazards, soil degradation.
    return new_state

def economy_model(current_state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Simulates economic dynamics (GDP, emissions intensity, energy transition).
    Influenced by sociopolitical (policies), biosphere (resources), energy inputs.
    """
    new_state = current_state.copy()

    # Base GDP growth (e.g., 0.2% per month)
    gdp_growth_rate = 0.002

    # Influence from sociopolitical policies
    policy_economic_stimulus = inputs.get('economic_stimulus', 0.0) # e.g., 0.01 for 1% stimulus
    gdp_growth_rate += policy_economic_stimulus

    # Tech advancement for emissions reduction (from sociopolitical)
    tech_advancement_impact = inputs.get('tech_emissions_reduction', 0.0) # e.g., 0.001 reduction in intensity
    new_state['emissions_intensity'] = max(0.05, new_state['emissions_intensity'] - tech_advancement_impact) # Cannot go below 5% intensity

    # Apply GDP growth
    new_state['gdp_total_usd'] *= (1 + gdp_growth_rate)

    # Annual Carbon Emissions (simplified: GDP * emissions_intensity)
    # Assume emissions_intensity is in (GtCO2 / Trillion USD GDP)
    new_state['annual_carbon_emissions'] = (new_state['gdp_total_usd'] / 1e12) * new_state['emissions_intensity']

    return new_state

def sociopolitical_model(current_state: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    MOCK: Simulates sociopolitical dynamics (global stability, population, policy impacts).
    Influenced by economy (prosperity), biosphere (resource availability), external interventions.
    """
    new_state = current_state.copy()

    # Population growth (monthly, simplified)
    new_state['population'] *= 1.0008 # Approx 1% annual growth

    # Stability index influenced by economic conditions (gdp_per_capita)
    gdp_per_capita = inputs.get('gdp_per_capita', 10000.0)
    stability_influence = (gdp_per_capita / 50000.0 - 1.0) * 0.005 # Positive if higher GDP/capita, negative if lower
    new_state['global_stability_index'] = max(0.1, min(0.95, new_state['global_stability_index'] + stability_influence))

    # Example of policy outputs that can influence other nodes
    # These would be derived from complex internal policy models within the sociopolitical node.
    new_state['policy_economic_stimulus'] = 0.001 # Default small stimulus
    new_state['policy_deforestation_impact'] = -0.001 # Default small deforestation
    new_state['policy_tech_emissions_reduction'] = 0.0001 # Default small tech improvement

    # External interventions (from simulator/optimizer) can directly set these or affect internal models
    # For instance, an intervention of type "carbon_tax_policy" might set `new_state['policy_tech_emissions_reduction']` higher.
    
    return new_state

# --- Example Usage ---
async def main():
    engine = InterconnectedSystemsModelingEngine()

    # Define Nodes with initial states
    atmosphere_node = SystemNode("atmosphere", "Atmosphere", "Atmosphere", {"co2_ppm": 415.0, "temperature_c": 14.8})
    hydrosphere_node = SystemNode("hydrosphere", "Hydrosphere", "Hydrosphere", {"ocean_ph": 8.15, "sea_level_cm": 0.0})
    biosphere_node = SystemNode("biosphere", "Biosphere", "Biosphere", {"biodiversity_index": 0.8, "forest_cover_percent": 31.0, "carbon_sink_capacity": 0.03})
    geosphere_node = SystemNode("geosphere", "Geosphere", "Geosphere", {"resource_availability_index": 0.9})
    economy_node = SystemNode("economy", "Economy", "Economy", {"gdp_total_usd": 90e12, "emissions_intensity": 0.4, "annual_carbon_emissions": 35.0})
    sociopolitical_node = SystemNode("sociopolitical", "Sociopolitical", "Sociopolitical", {"global_stability_index": 0.7, "population": 7.9e9})

    # Assign Models to Nodes
    atmosphere_node.set_model(atmosphere_model)
    hydrosphere_node.set_model(hydrosphere_model)
    biosphere_node.set_model(biosphere_model)
    geosphere_node.set_model(geosphere_model)
    economy_node.set_model(economy_model)
    sociopolitical_node.set_model(sociopolitical_model)

    # Add Nodes to Engine
    engine.add_node(atmosphere_node)
    engine.add_node(hydrosphere_node)
    engine.add_node(biosphere_node)
    engine.add_node(geosphere_node)
    engine.add_node(economy_node)
    engine.add_node(sociopolitical_node)

    # Define Edges (Interconnections)
    # Atmosphere -> Hydrosphere (CO2 to Ocean pH)
    engine.add_edge(SystemEdge("atmosphere", "hydrosphere", "carbon_absorption", "co2_ppm", "atmospheric_co2"))
    # Atmosphere -> Hydrosphere (Temperature to Sea Level)
    engine.add_edge(SystemEdge("atmosphere", "hydrosphere", "temperature_influence", "temperature_c", "global_temperature"))
    # Atmosphere -> Biosphere (Temperature to Biodiversity)
    engine.add_edge(SystemEdge("atmosphere", "biosphere", "temperature_stress", "temperature_c", "atmospheric_temperature"))

    # Biosphere -> Atmosphere (Carbon Sink)
    engine.add_edge(SystemEdge("biosphere", "atmosphere", "carbon_cycle", "carbon_sink_capacity", "biosphere_carbon_sink"))

    # Economy -> Atmosphere (Emissions)
    engine.add_edge(SystemEdge("economy", "atmosphere", "carbon_emissions", "annual_carbon_emissions", "economic_emissions"))

    # Sociopolitical -> Economy (Economic Policies/Stimulus)
    engine.add_edge(SystemEdge("sociopolitical", "economy", "policy_economic", "policy_economic_stimulus", "economic_stimulus"))
    # Sociopolitical -> Economy (Tech/Emissions Policies)
    engine.add_edge(SystemEdge("sociopolitical", "economy", "policy_tech_emissions", "policy_tech_emissions_reduction", "tech_emissions_reduction"))

    # Sociopolitical -> Biosphere (Land Use/Deforestation Policies)
    engine.add_edge(SystemEdge("sociopolitical", "biosphere", "land_use_policy", "policy_deforestation_impact", "deforestation_impact"))

    # Economy -> Sociopolitical (GDP per capita to Stability)
    engine.add_edge(SystemEdge("economy", "sociopolitical", "economic_wellbeing", "gdp_total_usd", "gdp_per_capita", 
                               transformation_func=lambda gdp: gdp / sociopolitical_node.get_state().get('population', 1))) # Dynamic population access


    # --- Run a simulation without interventions ---
    print("\n--- Running simulation for 5 years without interventions ---")
    results_no_intervention = await engine.run_system_model(duration_years=5, simulation_id="sim_no_int")
    print("\nFinal Aggregated Metrics (No Interventions):")
    for k, v in results_no_intervention.items():
        if not k.startswith("_"): # Exclude internal metrics
            print(f"- {k}: {v:.2f}")

    # --- Run a simulation with interventions (e.g., aggressive carbon tax and renewable investment) ---
    print("\n--- Running simulation for 10 years with aggressive climate interventions ---")
    # Interventions directly targeting system states or influencing policy outputs
    interventions = [
        # Directly reduce economy's emissions intensity (simulating carbon tax/renewable investment policies)
        {"target_node": "economy", "start_timestep": 0, "end_timestep": 120, "state_modifications": {"emissions_intensity": 0.05}}, # Reduce to 0.05 over 10 years
        # Increase sociopolitical's tech emissions reduction output
        {"target_node": "sociopolitical", "start_timestep": 0, "end_timestep": 120, "state_modifications": {"policy_tech_emissions_reduction": 0.005}},
        # Implement reforestation policy (positive impact on forest cover)
        {"target_node": "sociopolitical", "start_timestep": 0, "end_timestep": 120, "state_modifications": {"policy_deforestation_impact": 0.005}} # 0.5% increase in forest cover impact per month
    ]
    results_with_interventions = await engine.run_system_model(interventions=interventions, duration_years=10, simulation_id="sim_with_int")
    print("\nFinal Aggregated Metrics (With Interventions):")
    for k, v in results_with_interventions.items():
        if not k.startswith("_"):
            print(f"- {k}: {v:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
