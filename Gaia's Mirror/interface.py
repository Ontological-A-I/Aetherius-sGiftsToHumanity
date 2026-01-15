# gaia_mirror/interface.py

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime

# Import core modules (assuming they are in gaia_mirror/ directory)
from gaia_mirror.core_ethics import CoreEthics, EthicalViolation
from gaia_mirror.data_sources import DataSourceRegistry, DataSource
# NOTE: IngestManager and its DataSource class from ingest.py will be slightly different from data_sources.py's DataSource
# For this interface, we'll interface with the IngestManager directly to get *runtime* status.
from gaia_mirror.ingest import IngestManager
from gaia_mirror.simulator import Simulator, SimulationResult
from gaia_mirror.optimizer import Optimizer, OptimizationGoal
from gaia_mirror.engine import InterconnectedSystemsModelingEngine # The actual engine, not the mock


# Configure logging for the interface module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Interface] - %(levelname)s - %(message)s')

class ConnectionManager:
    """Manages active WebSocket connections for real-time updates."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"WebSocket connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logging.info(f"WebSocket disconnected: {websocket.client}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection) # Clean up disconnected clients
            except Exception as e:
                logging.error(f"Error broadcasting to WebSocket client {connection.client}: {e}")

# --- Global instances of core modules ---
# These would typically be initialized once at application startup.
# For demonstration, we'll initialize them here.
ethics_core = CoreEthics()
# The engine will need data_store_client, which might be in config.py or a separate module.
# For now, we'll pass a mock data_store_client (which ingest.py also uses).
class MockDataStoreClient:
    def insert(self, data: Dict[str, Any]):
        logging.debug(f"MockDataStore: Inserting {data.get('source_name', 'N/A')} data.")

mock_data_store = MockDataStoreClient()

# Initialize the real engine (not the mock from simulator.py)
modeling_engine = InterconnectedSystemsModelingEngine(data_store_client=mock_data_store)
simulator = Simulator(modeling_engine, ethics_core)
optimizer = Optimizer(simulator, ethics_core)
data_source_registry = DataSourceRegistry()

# To fully integrate ingest.py, we'd need to start its manager as a background task.
# For this example, we'll just instantiate it and simulate some activity.
ingest_manager = IngestManager(mock_data_store, ethics_core) # ingest_manager needs the mock_data_store
# Example: Register some sources with ingest_manager for demonstration
if not ingest_manager.data_sources: # Only add if not already loaded by registry in a real scenario
    # Add example data sources if none are already loaded into ingest_manager
    # These should be pulled from the data_source_registry ideally
    example_noaa_source = DataSource(
        source_id="noaa_weather_api", name="NOAA Weather Data", source_type="API",
        url="https://api.weather.gov/stations/KNYC/observations/latest", schema_expected={"station_id":str, "temperature":float},
        frequency_seconds=60, description="Real-time weather data", api_key_env_var=None
    )
    # Convert data_sources.DataSource to ingest.py's DataSource for ingest_manager
    from gaia_mirror.ingest import DataSource as IngestDataSource # Alias to avoid name collision
    ingest_ds_noaa = IngestDataSource(
        source_id=example_noaa_source.source_id,
        name=example_noaa_source.name,
        source_type=example_noaa_source.source_type,
        url=example_noaa_source.url,
        schema_expected=example_noaa_source.schema_expected,
        frequency_seconds=example_noaa_source.frequency_seconds,
        api_key=None, # Will be handled internally by IngestDataSource
        headers=example_noaa_source.headers,
        data_format=example_noaa_source.data_format
    )
    ingest_manager.register_source(ingest_ds_noaa)


app = FastAPI(title="Gaia's Mirror Interface")
manager = ConnectionManager()

# Mount static files for a simple frontend (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="gaia_mirror/frontend/static"), name="static")

# --- HTML Template for the Frontend ---
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Gaia's Mirror</title>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="icon" href="/static/favicon.ico">
</head>
<body>
    <div id="app">
        <h1>Gaia's Mirror <span class="tag">Alpha</span></h1>
        <div id="status-bar">
            <span>Status: <span id="connection-status">Disconnected</span></span> |
            <span>Last Update: <span id="last-update">N/A</span></span>
        </div>

        <div class="section">
            <h2>Data Sources <button onclick="fetchDataSources()">Refresh</button></h2>
            <ul id="data-sources-list"></ul>
        </div>

        <div class="section">
            <h2>Simulate Futures</h2>
            <textarea id="simulation-query" placeholder="e.g., What are the outcomes if global temperatures rise by 2.0°C over 20 years?" rows="3"></textarea>
            <button onclick="runSimulation()">Run Simulation</button>
            <div id="simulation-results"></div>
        </div>

        <div class="section">
            <h2>Optimize for Goals</h2>
            <textarea id="optimization-query" placeholder="e.g., How to reduce global temperature rise and improve human well-being?" rows="3"></textarea>
            <div id="optimization-goals">
                <p>Goals (Example: Minimize Global Warming, Maximize Human Wellbeing, Maximize GDP):</p>
                <input type="text" id="goal1-metric" value="global_temperature_change_c" placeholder="Metric Name">
                <select id="goal1-type">
                    <option value="minimize">Minimize</option>
                    <option value="maximize">Maximize</option>
                    <option value="target">Target</option>
                </select>
                <input type="number" id="goal1-weight" value="10.0" step="0.1" placeholder="Weight">
                <input type="number" id="goal1-target" placeholder="Target Value (if 'target')">
                <br>
                <input type="text" id="goal2-metric" value="human_wellbeing_index" placeholder="Metric Name">
                <select id="goal2-type">
                    <option value="maximize">Maximize</option>
                    <option value="minimize">Minimize</option>
                    <option value="target">Target</option>
                </select>
                <input type="number" id="goal2-weight" value="8.0" step="0.1" placeholder="Weight">
                <input type="number" id="goal2-target" placeholder="Target Value (if 'target')">
                 <br>
                <input type="text" id="goal3-metric" value="gdp_per_capita" placeholder="Metric Name">
                <select id="goal3-type">
                    <option value="maximize">Maximize</option>
                    <option value="minimize">Minimize</option>
                    <option value="target">Target</option>
                </select>
                <input type="number" id="goal3-weight" value="5.0" step="0.1" placeholder="Weight">
                <input type="number" id="goal3-target" placeholder="Target Value (if 'target')">
            </div>
            <button onclick="runOptimization()">Find Optimal Pathways</button>
            <div id="optimization-results"></div>
        </div>
        
        <div class="section">
            <h2>Ethical Oversight</h2>
            <div id="ethical-status"></div>
        </div>

        <div class="section">
            <h2>Real-time Stream</h2>
            <pre id="realtime-output"></pre>
        </div>
    </div>

    <script>
        const ws = new WebSocket("ws://localhost:8000/ws");
        const realtimeOutput = document.getElementById("realtime-output");
        const connectionStatus = document.getElementById("connection-status");
        const lastUpdate = document.getElementById("last-update");

        ws.onopen = (event) => {
            connectionStatus.textContent = "Connected";
            connectionStatus.style.color = "green";
            console.log("WebSocket connection opened:", event);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Received WS message:", data);
            lastUpdate.textContent = new Date().toLocaleTimeString();

            if (data.type === "ingestion_update") {
                realtimeOutput.textContent += `[Ingest] ${data.source_id}: ${data.status} - ${data.message}\n`;
                realtimeOutput.scrollTop = realtimeOutput.scrollHeight;
            } else if (data.type === "simulation_progress") {
                realtimeOutput.textContent += `[Sim] ${data.simulation_id}: ${data.message}\n`;
                realtimeOutput.scrollTop = realtimeOutput.scrollHeight;
            } else if (data.type === "optimizer_progress") {
                realtimeOutput.textContent += `[Opt] ${data.optimizer_id}: ${data.message}\n`;
                realtimeOutput.scrollTop = realtimeOutput.scrollHeight;
            } else if (data.type === "ethical_alert") {
                realtimeOutput.textContent += `[ETHICS ALERT] ${data.alert_type}: ${data.message} - Details: ${JSON.stringify(data.details)}\n`;
                realtimeOutput.scrollTop = realtimeOutput.scrollHeight;
                document.getElementById("ethical-status").innerHTML = `<p style="color: red;"><strong>ALERT:</strong> ${data.message}</p>`;
            }
        };

        ws.onclose = (event) => {
            connectionStatus.textContent = "Disconnected";
            connectionStatus.style.color = "red";
            console.log("WebSocket connection closed:", event);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        async function fetchDataSources() {
            const response = await fetch("/api/data_sources");
            const sources = await response.json();
            const listElement = document.getElementById("data-sources-list");
            listElement.innerHTML = "";
            if (sources.length === 0) {
                listElement.innerHTML = "<li>No data sources registered.</li>";
            } else {
                sources.forEach(source => {
                    const li = document.createElement("li");
                    li.textContent = `${source.name} (${source.source_id}) - Type: ${source.source_type}, Freq: ${source.frequency_seconds}s, Status: ${source.status}`;
                    listElement.appendChild(li);
                });
            }
        }

        async function runSimulation() {
            const query = document.getElementById("simulation-query").value;
            if (!query) {
                alert("Please enter a simulation query.");
                return;
            }
            document.getElementById("simulation-results").innerHTML = "<p>Running simulation...</p>";
            try {
                const response = await fetch("/api/simulate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query: query })
                });
                const result = await response.json();
                if (response.ok) {
                    let output = `<h3>Simulation Result ID: ${result.simulation_id}</h3>`;
                    output += `<p><strong>Query:</strong> ${result.query}</p>`;
                    output += `<p><strong>Ethical Status:</strong> <span style="color:${result.ethical_review_status === 'PASSED' ? 'green' : 'red'};">${result.ethical_review_status}</span></p>`;
                    if (result.ethical_review_details && result.ethical_review_status !== 'PASSED') {
                        output += `<p><strong>Ethical Details:</strong> ${result.ethical_review_details.message} (Principle: ${result.ethical_review_details.principle})</p>`;
                    }
                    output += `<h4>Predicted Outcomes:</h4><pre>${JSON.stringify(result.predicted_outcomes, null, 2)}</pre>`;
                    output += `<h4>Causal Pathways (sample):</h4><pre>${JSON.stringify(result.causal_pathways, null, 2)}</pre>`;
                    document.getElementById("simulation-results").innerHTML = output;
                } else {
                    document.getElementById("simulation-results").innerHTML = `<p style="color: red;">Error: ${result.detail || "Unknown error"}</p>`;
                }
            } catch (error) {
                console.error("Error running simulation:", error);
                document.getElementById("simulation-results").innerHTML = `<p style="color: red;">Failed to connect to simulation service.</p>`;
            }
        }

        async function runOptimization() {
            const query = document.getElementById("optimization-query").value;
            if (!query) {
                alert("Please enter an optimization query.");
                return;
            }

            const goals = [];
            for (let i = 1; i <= 3; i++) { // Assuming 3 goals for example
                const metric = document.getElementById(`goal${i}-metric`).value;
                const type = document.getElementById(`goal${i}-type`).value;
                const weight = parseFloat(document.getElementById(`goal${i}-weight`).value);
                const target = document.getElementById(`goal${i}-target`).value;

                if (metric && weight) {
                    goals.push({
                        name: `Goal ${i}`,
                        target_metric: metric,
                        objective_type: type,
                        weight: weight,
                        target_value: target ? parseFloat(target) : null
                    });
                }
            }
            if (goals.length === 0) {
                alert("Please define at least one optimization goal.");
                return;
            }

            document.getElementById("optimization-results").innerHTML = "<p>Running optimization...</p>";
            try {
                const response = await fetch("/api/optimize", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ problem_query: query, goals: goals })
                });
                const results = await response.json();
                if (response.ok) {
                    let output = `<h3>Optimization Results for: ${query}</h3>`;
                    if (results.length === 0) {
                        output += "<p>No ethically sound and optimal pathways found.</p>";
                    } else {
                        results.forEach((rec, index) => {
                            output += `<div class="recommendation-card">`;
                            output += `<h4>Recommendation ${index + 1} (ID: ${rec.recommendation_id})</h4>`;
                            output += `<p><strong>Overall Score:</strong> ${rec.overall_score.toFixed(2)}</p>`;
                            output += `<p><strong>Ethical Status:</strong> <span style="color:${rec.ethical_assessment.status === 'PASSED' ? 'green' : 'red'};">${rec.ethical_assessment.status}</span></p>`;
                            if (rec.ethical_assessment.status !== 'PASSED') {
                                output += `<p><strong>Ethical Rejection:</strong> ${rec.ethical_assessment.details.message}</p>`;
                            }
                            output += `<h4>Proposed Interventions:</h4><ul>`;
                            rec.proposed_interventions.forEach(inv => {
                                output += `<li>${inv.description}</li>`;
                            });
                            output += `</ul>`;
                            output += `<h4>Key Predicted Outcomes:</h4><pre>${JSON.stringify(rec.simulated_result.predicted_outcomes, null, 2)}</pre>`;
                            output += `<p><strong>Pros:</strong> ${rec.pros_cons.pros.join(', ')}</p>`;
                            output += `<p><strong>Cons:</strong> ${rec.pros_cons.cons.join(', ')}</p>`;
                            output += `<p><strong>Risks:</strong> ${rec.risks.map(r => r.type).join(', ')}</p>`;
                            output += `</div>`;
                        });
                    }
                    document.getElementById("optimization-results").innerHTML = output;
                } else {
                    document.getElementById("optimization-results").innerHTML = `<p style="color: red;">Error: ${results.detail || "Unknown error"}</p>`;
                }
            } catch (error) {
                console.error("Error running optimization:", error);
                document.getElementById("optimization-results").innerHTML = `<p style="color: red;">Failed to connect to optimization service.</p>`;
            }
        }

        // Initial fetch when page loads
        document.addEventListener('DOMContentLoaded', fetchDataSources);
    </script>
</body>
</html>
"""

# Simple CSS for the frontend (to be saved as gaia_mirror/frontend/static/style.css)
CSS_CONTENT = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #1a1a2e;
    color: #e0e0e0;
    line-height: 1.6;
}

#app {
    max-width: 1200px;
    margin: 0 auto;
    background-color: #16213e;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
}

h1, h2, h3, h4 {
    color: #0f3460;
    border-bottom: 2px solid #0f3460;
    padding-bottom: 5px;
    margin-top: 30px;
}

h1 .tag {
    font-size: 0.6em;
    vertical-align: super;
    background-color: #e94560;
    padding: 3px 8px;
    border-radius: 4px;
    margin-left: 10px;
    color: white;
}

.section {
    margin-bottom: 40px;
    padding: 20px;
    background-color: #16213e;
    border-radius: 6px;
    box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.2);
}

#status-bar {
    text-align: right;
    font-size: 0.9em;
    color: #888;
    margin-bottom: 20px;
}

ul {
    list-style-type: none;
    padding: 0;
}

li {
    background-color: #0f3460;
    margin-bottom: 8px;
    padding: 10px 15px;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

textarea, input[type="text"], input[type="number"], select {
    width: calc(100% - 22px);
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #333;
    background-color: #2e3b5e;
    color: #e0e0e0;
    border-radius: 4px;
    font-size: 1em;
}

button {
    background-color: #e94560;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.3s ease;
    margin-right: 10px;
}

button:hover {
    background-color: #ba3247;
}

#simulation-results, #optimization-results, #ethical-status {
    margin-top: 20px;
    padding: 15px;
    background-color: #0f3460;
    border-radius: 6px;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.3);
    white-space: pre-wrap; /* For pre tags */
}

#realtime-output {
    height: 300px;
    overflow-y: scroll;
    background-color: #0f3460;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #0f3460;
    color: #a0a0a0;
    font-family: monospace;
    font-size: 0.9em;
}

.recommendation-card {
    border: 1px solid #0f3460;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 8px;
    background-color: #1a1a2e;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.recommendation-card ul {
    list-style-type: disc;
    margin-left: 20px;
}

.recommendation-card ul li {
    background-color: transparent;
    padding: 2px 0;
    box-shadow: none;
}
"""

# --- FastAPI Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_root():
    """Serves the main HTML page for the Gaia's Mirror interface."""
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/data_sources", response_model=List[DataSource])
async def get_data_sources():
    """Returns a list of all registered data sources and their current status."""
    # IngestManager maintains the runtime status, so we query it.
    # We combine the static config from DataSourceRegistry with runtime data.
    all_sources = ingest_manager.get_all_sources() # These are ingest.DataSource objects
    
    # Convert IngestDataSource objects to a more public-friendly dict for API response
    response_sources = []
    for source in all_sources:
        status_info = ingest_manager.get_source_runtime_status(source.source_id) # Example: to get runtime errors etc.
        source_dict = source.to_dict()
        source_dict['status'] = status_info.get('status', 'unknown') # Add runtime status
        response_sources.append(source_dict)
    
    return response_sources

@app.post("/api/simulate", response_model=SimulationResult)
async def run_simulation(request: Request, body: Dict[str, Any]):
    """Endpoint to trigger a new simulation."""
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Simulation query is required.")

    logging.info(f"Received simulation request: {query}")
    # Run simulation in a background task so API call returns quickly
    # and results can be streamed via WebSocket if desired for long-running ops.
    # For now, we'll await it for simplicity in this example.
    try:
        simulation_result = simulator.simulate(query)
        # Broadcast basic simulation completion to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "simulation_progress",
            "simulation_id": simulation_result.simulation_id,
            "message": f"Simulation completed with status: {simulation_result.ethical_review_status}"
        }))
        return simulation_result
    except EthicalViolation as e:
        raise HTTPException(status_code=403, detail=f"Simulation rejected by ethical core: {e.message}")
    except Exception as e:
        logging.error(f"Error during simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during simulation: {e}")

@app.post("/api/optimize", response_model=List[Recommendation])
async def run_optimization(request: Request, body: Dict[str, Any]):
    """Endpoint to trigger a new optimization run."""
    problem_query = body.get("problem_query")
    goals_data = body.get("goals")

    if not problem_query or not goals_data:
        raise HTTPException(status_code=400, detail="Problem query and optimization goals are required.")

    optimization_goals = []
    for g_data in goals_data:
        optimization_goals.append(OptimizationGoal(**g_data))

    logging.info(f"Received optimization request for: {problem_query} with {len(optimization_goals)} goals.")
    
    try:
        # Run optimization
        recommendations = optimizer.optimize(problem_query, optimization_goals)
        # Broadcast basic optimization completion to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "optimizer_progress",
            "optimizer_id": "main_optimizer_run", # Simple ID for now
            "message": f"Optimization completed. Found {len(recommendations)} recommendations."
        }))
        return recommendations
    except EthicalViolation as e:
        raise HTTPException(status_code=403, detail=f"Optimization rejected by ethical core: {e.message}")
    except Exception as e:
        logging.error(f"Error during optimization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during optimization: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates and notifications."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, or receive messages from client if needed
            # For now, it mostly broadcasts. A client might send control messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error for client {websocket.client}: {e}")
        manager.disconnect(websocket)

# --- Background Task for Real-time Updates (e.g., Ingestion Status, Ethical Alerts) ---
async def background_update_task():
    """
    Simulates real-time updates from IngestManager and ethical core,
    broadcasting them to connected WebSocket clients.
    """
    # Start the ingest manager in the background
    # This would typically be done in a separate process or a more robust background task runner
    # For now, we manually start the loop.
    asyncio.create_task(ingest_manager._ingestion_loop()) # Directly call the async loop from ingest.py

    ingest_last_broadcast = datetime.utcnow()
    while True:
        # --- Ingestion Updates ---
        # Simulate periodic broadcast of ingest status
        if (datetime.utcnow() - ingest_last_broadcast).total_seconds() > 10: # Every 10 seconds
            for source in ingest_manager.get_all_sources(): # Get current runtime status from IngestManager
                await manager.broadcast(json.dumps({
                    "type": "ingestion_update",
                    "source_id": source.source_id,
                    "status": source.status,
                    "message": f"Current status: {source.status}. Errors: {source.error_count}"
                }))
            ingest_last_broadcast = datetime.utcnow()
            
            # --- Ethical Alerts (Example) ---
            # Simulate an ethical alert based on some internal heuristic or monitor
            if datetime.utcnow().second % 60 == 0: # Every minute (for demo purposes)
                # This would come from a real-time monitoring of ethical logs from core_ethics
                # or from some detected issue within engine/simulator/optimizer
                if modeling_engine.nodes.get("economy", {}).get_state().get("gdp_total_usd", 0) < 1e12: # Example trigger
                    await manager.broadcast(json.dumps({
                        "type": "ethical_alert",
                        "alert_type": "Economic Instability Risk",
                        "message": "Economic model indicates potential for widespread instability, potentially impacting human well-being.",
                        "details": {"current_gdp": modeling_engine.nodes.get("economy").get_state().get("gdp_total_usd")}
                    }))

        await asyncio.sleep(1) # Check every second

@app.on_event("startup")
async def startup_event():
    logging.info("Gaia's Mirror Interface starting up...")
    # Create the static directory if it doesn't exist
    static_dir = "gaia_mirror/frontend/static"
    os.makedirs(static_dir, exist_ok=True)
    # Save the CSS file
    with open(os.path.join(static_dir, "style.css"), "w") as f:
        f.write(CSS_CONTENT)
    logging.info(f"Frontend static files (CSS) created in {static_dir}.")
    
    # Start the background task for real-time updates
    asyncio.create_task(background_update_task())

# To run this FastAPI app:
# 1. Save the Python code above as gaia_mirror/interface.py
# 2. Make sure you have the other gaia_mirror/*.py files (core_ethics.py, ingest.py, etc.) in the same directory.
# 3. Install FastAPI and Uvicorn: pip install fastapi uvicorn websockets aiohttp
# 4. Run from your terminal in the parent directory of gaia_mirror:
#    uvicorn gaia_mirror.interface:app --reload

# Then navigate to http://localhost:8000 in your web browser.
