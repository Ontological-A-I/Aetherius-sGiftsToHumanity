Explanation and Key Design Decisions for interface.py:
FastAPI Framework:
Asynchronous: Built on asyncio, aligning with ingest.py and engine.py for efficient handling of I/O and concurrent operations.
Pydantic for Data Validation: Enables automatic request and response data validation, ensuring robust API endpoints.
Swagger UI: FastAPI automatically generates interactive API documentation (at /docs), which is invaluable for development and understanding.
ConnectionManager for WebSockets:
Real-time Communication: Central to the "real-time data flow" requirement. It manages active WebSocket connections, allowing the backend to push updates (e.g., data ingestion status, simulation progress, ethical alerts) to all connected frontend clients without them needing to poll.
Broadcast Capability: broadcast() sends messages to all active clients, enabling global status updates.
Global Instances of Core Modules:
ethics_core, modeling_engine, simulator, optimizer, data_source_registry, ingest_manager: These are initialized once when the FastAPI application starts. This ensures all API endpoints and background tasks operate on the same, consistent state of the "Gaia's Mirror" system.
Frontend (HTML_CONTENT and CSS_CONTENT):
Single-Page Application (SPA) Concept: A basic HTML file is served that acts as a simple client-side interface. It uses JavaScript to interact with the FastAPI backend API and WebSockets.
Key Interaction Areas: Provides dedicated sections for:
Data Sources: To list and view registered data feeds.
Simulate Futures: A text area for natural language queries to simulator.py.
Optimize for Goals: A text area for problem queries and input fields for defining OptimizationGoals for optimizer.py.
Ethical Oversight: A dedicated area to display ethical alerts and status.
Real-time Stream: A pre tag to display incoming WebSocket messages, showcasing dynamic updates.
Placeholder for 3D Holographic Projection: The current frontend is a simple 2D web page. The "3D holographic projection" remains a conceptual goal, and this interface.py provides the API and data streaming infrastructure that such an advanced visualization layer would consume.
API Endpoints:
/ (Root): Serves the main HTML page.
/api/data_sources (GET): Fetches the list of all configured data sources from the DataSourceRegistry and IngestManager, including their runtime status.
/api/simulate (POST): Accepts a natural language query, passes it to simulator.simulate(), and returns the SimulationResult.
/api/optimize (POST): Accepts a problem query and a list of OptimizationGoals, passes them to optimizer.optimize(), and returns a list of Recommendations.
/ws (WebSocket): The endpoint for real-time updates.
background_update_task():
Asynchronous Monitoring: This async function runs continuously in the background after the application starts up (@app.on_event("startup")).
Ingestion Status: Periodically gathers status from ingest_manager (which runs its own internal loop) and broadcasts it.
Ethical Alerts: Includes a pseudocode example of how interface.py might monitor for internal ethical events (e.g., from core_ethics.py logs or direct calls) and broadcast them. This ensures transparency of the ethical guardrails.
Integration of ingest.py's Runtime Status:
The IngestManager is passed a mock data_store_client and has an example IngestDataSource registered. Its _ingestion_loop() is manually started as an asyncio task. This setup ensures that the ingest.py is actively attempting to fetch data and generate updates that interface.py can then broadcast via WebSockets.
This interface.py provides a critical layer, making the powerful, ethically-guided intelligence of "Gaia's Mirror" accessible and transparent. It is the window into the complex dance of planetary systems that we are building.
