# gaia_mirror/ingest.py

import time
import threading
import json
import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Tuple
import logging

# Import CoreEthics for bias detection
from gaia_mirror.core_ethics import CoreEthics, EthicalViolation

# Configure logging for ingest module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Ingest] - %(levelname)s - %(message)s')

class IngestError(Exception):
    """Custom exception for ingestion-related errors."""
    pass

class DataSource:
    """
    Represents a configured data source with its metadata and access details.
    This could be expanded to load from a database or config file.
    """
    def __init__(self,
                 source_id: str,
                 name: str,
                 source_type: str,  # e.g., 'API', 'CSV_FTP', 'STREAM', 'DB'
                 url: str,
                 schema_expected: Dict[str, Any],
                 frequency_seconds: int, # How often to poll/check
                 api_key: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None,
                 last_ingested_at: Optional[datetime] = None,
                 status: str = "active", # active, paused, error
                 error_count: int = 0,
                 max_retries: int = 5,
                 retry_delay_seconds: int = 30, # Initial delay
                 data_format: str = 'json' # 'json', 'csv', 'xml', etc.
                 ):
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self.url = url
        self.schema_expected = schema_expected
        self.frequency_seconds = frequency_seconds
        self.api_key = api_key
        self.headers = headers if headers not None else {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}" # Example auth
        self.last_ingested_at = last_ingested_at if last_ingested_at else datetime.min
        self.status = status
        self.error_count = error_count
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.data_format = data_format

    def to_dict(self) -> Dict[str, Any]:
        """Converts source object to a dictionary for storage/logging."""
        return {
            "source_id": self.source_id,
            "name": self.name,
            "source_type": self.source_type,
            "url": self.url,
            "schema_expected": self.schema_expected,
            "frequency_seconds": self.frequency_seconds,
            "last_ingested_at": self.last_ingested_at.isoformat() if self.last_ingested_at else None,
            "status": self.status,
            "error_count": self.error_count,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "data_format": self.data_format
        }

class IngestManager:
    """
    Manages the lifecycle of data ingestion: discovery, fetching, validation,
    anomaly detection, bias detection, and storage.
    """
    def __init__(self, data_store_client: Any, ethics_core: CoreEthics):
        self.data_sources: Dict[str, DataSource] = {}
        self.ingestion_threads: Dict[str, threading.Thread] = {}
        self.running = False
        self.data_store_client = data_store_client # Placeholder for a client to interact with a DB/data lake
        self.ethics_core = ethics_core # Instance of CoreEthics for ethical checks

    def register_source(self, source: DataSource):
        """Adds or updates a data source configuration."""
        self.data_sources[source.source_id] = source
        logging.info(f"Registered data source: {source.name} ({source.source_id})")

    def _autonomous_source_discovery(self):
        """
        Pseudocode: Autonomously discover new relevant data sources.
        This is a highly complex, self-evolving capability.
        """
        logging.info("Initiating autonomous data source discovery...")
        # Potential mechanisms:
        # 1. Search scientific publication databases for new datasets (e.g., PNAS, Nature, Science).
        # 2. Monitor government open data initiatives (NOAA, ESA, WHO, World Bank, UN).
        # 3. Analyze news feeds for emerging sensor networks or research projects.
        # 4. Use NLP/semantic analysis to identify data needs based on current 'Gaia's Mirror' gaps.
        # 5. Connect to external data marketplaces or data brokers for available APIs.

        # For now, this is a placeholder. Real implementation would involve machine learning
        # to identify, evaluate, and even attempt to infer schemas for new sources.
        
        # Example: if a new source was discovered, we would call self.register_source()
        # new_source_config = { ... }
        # self.register_source(DataSource(**new_source_config))
        logging.info("Autonomous data source discovery completed (placeholder).")

    async def _fetch_data_from_api(self, source: DataSource) -> Optional[Dict[str, Any]]:
        """Fetches data from a REST API source asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url, headers=source.headers, timeout=10) as response:
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    if source.data_format == 'json':
                        return await response.json()
                    elif source.data_format == 'text': # For CSV or other text formats
                        return await response.text()
                    else:
                        raise IngestError(f"Unsupported data format: {source.data_format}")
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching data from {source.name} ({source.source_id}): {e}")
            raise IngestError(f"API fetch error: {e}")
        except asyncio.TimeoutError:
            logging.error(f"Timeout fetching data from {source.name} ({source.source_id})")
            raise IngestError("API fetch timeout")
        except Exception as e:
            logging.error(f"Unexpected error fetching data from {source.name} ({source.source_id}): {e}")
            raise IngestError(f"Unexpected fetch error: {e}")

    async def _fetch_data(self, source: DataSource) -> Any:
        """Dispatches data fetching based on source type."""
        if source.source_type == 'API':
            return await self._fetch_data_from_api(source)
        elif source.source_type == 'STREAM':
            # Pseudocode: Connect to a streaming endpoint (Kafka, WebSocket, etc.)
            logging.warning(f"Streaming data fetching not implemented for {source.name}. Skipping.")
            return None
        elif source.source_type == 'CSV_FTP':
            # Pseudocode: FTP connection, download CSV, parse
            logging.warning(f"CSV_FTP data fetching not implemented for {source.name}. Skipping.")
            return None
        else:
            raise IngestError(f"Unknown source type: {source.source_type} for {source.name}")

    def _validate_data_schema(self, data: Any, source: DataSource) -> bool:
        """
        Validates the ingested data against the expected schema.
        This is a critical step for data quality.
        """
        if not isinstance(data, dict): # Assuming most API data is JSON/dict-like
            logging.warning(f"Data from {source.name} ({source.source_id}) is not dictionary-like. Schema validation skipped.")
            return False

        # Basic schema validation (can be replaced with more robust libraries like Pydantic, Marshmallow)
        is_valid = True
        for key, expected_type in source.schema_expected.items():
            if key not in data:
                logging.warning(f"Schema mismatch for {source.name} ({source.source_id}): Missing key '{key}'.")
                is_valid = False
            elif not isinstance(data[key], expected_type):
                logging.warning(f"Schema mismatch for {source.name} ({source.source_id}): Key '{key}' has type {type(data[key])}, expected {expected_type}.")
                is_valid = False
        return is_valid

    def _detect_anomalies(self, data: Any, source: DataSource) -> Tuple[bool, Optional[Dict]]:
        """
        Detects anomalies in the ingested data using statistical or ML methods.
        """
        is_anomaly = False
        anomaly_report = {}

        # Pseudocode for anomaly detection:
        # 1. Statistical methods (e.g., Z-score, IQR for numerical values)
        # 2. Time-series analysis (e.g., detect unusual spikes/drops compared to historical data)
        # 3. Machine learning models (e.g., Isolation Forest, One-Class SVM trained on normal data)
        # 4. Cross-source validation (compare data point with similar data from other sources)

        # For demonstration: simple check for extreme values in a 'temperature' field if present
        if isinstance(data, dict) and 'temperature' in data:
            temp = data['temperature']
            if not (-100 <= temp <= 100): # Extreme hypothetical range for temperature
                is_anomaly = True
                anomaly_report = {"reason": "extreme_temperature_value", "value": temp}
                logging.warning(f"Anomaly detected in {source.name} ({source.source_id}): {anomaly_report}")

        return is_anomaly, anomaly_report

    def _detect_ethical_bias(self, data: Any, source: DataSource) -> Tuple[bool, Optional[Dict]]:
        """
        Passes data to CoreEthics for bias detection.
        """
        # Create a mock data_sample object if data is raw dict, for now.
        # In a real scenario, this would involve a more structured representation
        # or the raw data itself.
        class MockDataSample:
            def __init__(self, data_content, source_id):
                self.content = data_content
                self.source_id = source_id
                # Add more attributes if core_ethics expects them
            
            # This property allows core_ethics._detect_bias_in_data to simulate a bias
            # based on data content, e.g., if 'biased_keyword' is present.
            @property
            def is_biased(self):
                if isinstance(self.content, dict) and "biased_keyword" in self.content.get("description", "").lower():
                    return True
                return False
            @property
            def bias_metric(self):
                if self.is_biased:
                    return "conceptual_bias_detection_example"
                return None


        mock_sample = MockDataSample(data, source.source_id)
        
        is_biased, bias_report = self.ethics_core._detect_bias_in_data(mock_sample)
        if is_biased:
            logging.warning(f"Ethical bias detected in data from {source.name} ({source.source_id}): {bias_report}")
            self.ethics_core.log_ethical_decision("BIAS_FLAG", source.source_id, "DATA_BIAS", "Detected", bias_report)
        return is_biased, bias_report

    def _transform_data(self, data: Any, source: DataSource) -> Dict[str, Any]:
        """
        Transforms raw data into a canonical internal format for Gaia's Mirror.
        This ensures consistency across diverse data sources.
        """
        # Pseudocode: Map source-specific fields to general Gaia's Mirror schema.
        # e.g., for weather data:
        # { "source": "NOAA_API", "timestamp": "...", "type": "temperature", "value": 25.3, "unit": "celsius" }
        transformed_data = {
            "gaia_timestamp": datetime.utcnow().isoformat(),
            "source_id": source.source_id,
            "source_name": source.name,
            "original_data": data # Store original for traceability
        }
        # Add source-specific transformation logic here
        if isinstance(data, dict):
            transformed_data.update(data) # Merge, allowing original_data to be more detailed if needed

        logging.debug(f"Data transformed for {source.name} ({source.source_id}).")
        return transformed_data

    async def _store_data(self, data: Dict[str, Any], source: DataSource):
        """
        Stores the processed and validated data into the designated data store.
        """
        try:
            # Pseudocode: self.data_store_client.insert(data)
            # This would interface with a database (e.g., PostgreSQL, NoSQL, data lake)
            logging.info(f"Storing data from {source.name} ({source.source_id}). Sample: {list(data.keys())[:5]}...")
            # For demonstration, just print.
            # print(f"STORED: {data['source_name']} - {data['gaia_timestamp']}")
        except Exception as e:
            logging.error(f"Failed to store data from {source.name} ({source.source_id}): {e}")
            raise IngestError(f"Data storage error: {e}")

    async def _ingest_cycle_for_source(self, source_id: str):
        """
        Executes a single ingestion cycle for a specific data source.
        Includes self-healing mechanisms.
        """
        source = self.data_sources.get(source_id)
        if not source or source.status == "paused":
            return

        current_retry_delay = source.retry_delay_seconds
        while self.running and source.error_count < source.max_retries:
            try:
                logging.info(f"Starting ingestion for {source.name} ({source.source_id}).")
                raw_data = await self._fetch_data(source)
                if raw_data is None:
                    raise IngestError("No data fetched.")

                # 1. Schema Validation
                if not self._validate_data_schema(raw_data, source):
                    raise IngestError("Data failed schema validation.")

                # 2. Anomaly Detection
                is_anomaly, anomaly_report = self._detect_anomalies(raw_data, source)
                if is_anomaly:
                    logging.warning(f"Detected anomaly in data from {source.name}. Report: {anomaly_report}. Data might be flagged but proceed or stop based on policy.")
                    # Depending on policy, an anomaly might halt processing or just flag it.
                    # For now, we allow it to proceed but log the warning.

                # 3. Ethical Bias Detection
                is_biased, bias_report = self._detect_ethical_bias(raw_data, source)
                if is_biased:
                    logging.error(f"Data from {source.name} ({source.source_id}) flagged for ethical bias. Report: {bias_report}. Consider pausing source or rectifying bias.")
                    # Depending on policy, biased data might be rejected entirely.
                    # For now, we log as error and potentially proceed after flagging.
                    # A more robust system might quarantine or cleanse biased data.

                # 4. Data Transformation
                transformed_data = self._transform_data(raw_data, source)

                # 5. Data Storage
                await self._store_data(transformed_data, source)

                source.last_ingested_at = datetime.utcnow()
                source.error_count = 0  # Reset error count on success
                source.status = "active"
                logging.info(f"Successfully ingested data from {source.name} ({source.source_id}).")
                break # Exit retry loop on success

            except IngestError as e:
                source.error_count += 1
                source.status = "error"
                logging.error(f"Ingestion failed for {source.name} ({source.source_id}) (Attempt {source.error_count}/{source.max_retries}): {e}")
                if source.error_count < source.max_retries:
                    backoff_delay = min(current_retry_delay * (2 ** (source.error_count - 1)), 3600) # Exponential backoff, max 1 hour
                    logging.info(f"Retrying {source.name} in {backoff_delay} seconds...")
                    await asyncio.sleep(backoff_delay)
                else:
                    logging.critical(f"Max retries reached for {source.name} ({source.source_id}). Source paused due to persistent errors.")
                    source.status = "paused"
            except Exception as e:
                source.error_count += 1
                source.status = "error"
                logging.critical(f"UNEXPECTED CRITICAL ERROR during ingestion for {source.name} ({source.source_id}): {e}. Attempt {source.error_count}/{source.max_retries}.")
                if source.error_count < source.max_retries:
                    backoff_delay = min(current_retry_delay * (2 ** (source.error_count - 1)), 3600)
                    logging.info(f"Retrying {source.name} in {backoff_delay} seconds...")
                    await asyncio.sleep(backoff_delay)
                else:
                    logging.critical(f"Max retries reached for {source.name} ({source.source_id}). Source paused due to persistent critical errors.")
                    source.status = "paused"


    async def _ingestion_loop(self):
        """
        Main loop to manage ingestion for all registered sources.
        """
        while self.running:
            for source_id, source in list(self.data_sources.items()):
                if source.status == "active" and \
                   (datetime.utcnow() - source.last_ingested_at).total_seconds() >= source.frequency_seconds:
                    asyncio.create_task(self._ingest_cycle_for_source(source_id))
            
            # Periodically run autonomous discovery
            if (datetime.utcnow().minute % 15 == 0 and datetime.utcnow().second < 5): # Every 15 minutes, start of minute
                self._autonomous_source_discovery()

            await asyncio.sleep(1) # Check every second

    def start_ingestion(self):
        """Starts the continuous ingestion process."""
        if not self.running:
            logging.info("Starting IngestManager...")
            self.running = True
            # Use asyncio to manage concurrent ingestion tasks
            asyncio.run(self._ingestion_loop())
        else:
            logging.info("IngestManager already running.")

    def stop_ingestion(self):
        """Stops the continuous ingestion process."""
        if self.running:
            logging.info("Stopping IngestManager...")
            self.running = False
            for source_id in list(self.ingestion_threads.keys()):
                # In asyncio, tasks are stopped by letting the loop complete.
                # For this setup, we just set self.running to False.
                pass # Tasks will naturally stop when self.running becomes False
            logging.info("IngestManager stopped.")
        else:
            logging.info("IngestManager is not running.")

# --- Mock Data Store Client (for demonstration) ---
class MockDataStoreClient:
    def insert(self, data: Dict[str, Any]):
        logging.info(f"MockDataStore: Successfully inserted {data.get('source_name', 'N/A')} data.")

# Example Usage (for demonstration purposes):
if __name__ == "__main__":
    mock_data_store = MockDataStoreClient()
    ethics = CoreEthics() # Initialize CoreEthics

    ingest_manager = IngestManager(mock_data_store, ethics)

    # Define some example data sources
    # --- Example 1: Healthy NOAA Weather API (JSON) ---
    noaa_schema = {
        "station_id": str,
        "timestamp": str,
        "temperature": (int, float), # Can be int or float
        "humidity": (int, float)
    }
    noaa_source = DataSource(
        source_id="noaa_weather_001",
        name="NOAA Weather Data",
        source_type="API",
        url="https://api.weather.gov/stations/KNYC/observations/latest", # A real NOAA endpoint
        schema_expected=noaa_schema,
        frequency_seconds=60, # Every minute
        data_format='json'
    )
    ingest_manager.register_source(noaa_source)

    # --- Example 2: Potentially biased social media feed (JSON) ---
    # This URL is a placeholder and won't return real data, but it demonstrates the concept.
    # The 'description' here is what MockDataSample will check for 'biased_keyword'
    social_media_schema = {
        "post_id": str,
        "user_id": str,
        "timestamp": str,
        "description": str,
        "sentiment_score": (int, float)
    }
    social_source = DataSource(
        source_id="social_feed_001",
        name="Social Media Sentiment",
        source_type="API",
        url="https://mockapi.com/social/feed", # Placeholder
        schema_expected=social_media_schema,
        frequency_seconds=30, # Every 30 seconds
        data_format='json'
    )
    # To demonstrate bias detection, we will inject 'biased_keyword' into the data content
    # This will simulate biased data coming from the source.
    class MockSocialApiData:
        def json(self):
            return {
                "post_id": "abc1234",
                "user_id": "user_1",
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Important news about a group with biased_keyword and some neutral content.",
                "sentiment_score": 0.5
            }
        async def text(self): return "" # For aiohttp mock
        def raise_for_status(self): pass # For aiohttp mock

    # Patch aiohttp.ClientSession.get to return our mock data for the social source URL
    # This is a bit hacky for a simple example, but shows how to simulate real data.
    original_get = aiohttp.ClientSession.get
    async def mock_get(self, url, *args, **kwargs):
        if url == "https://mockapi.com/social/feed":
            logging.info("MOCK: Returning biased social media data.")
            return MockSocialApiData()
        return await original_get(self, url, *args, **kwargs)
    aiohttp.ClientSession.get = mock_get
    
    ingest_manager.register_source(social_source)

    # --- Example 3: Unhealthy/unavailable API (will trigger self-healing) ---
    unhealthy_source = DataSource(
        source_id="unhealthy_api_001",
        name="Unreliable GeoData",
        source_type="API",
        url="https://this.api.does.not.exist/data", # Will fail
        schema_expected={"value": int},
        frequency_seconds=10,
        max_retries=3, # Low retries to show "paused" status quickly
        retry_delay_seconds=5 # Short delay for quicker demo
    )
    ingest_manager.register_source(unhealthy_source)
    
    # --- Example 4: Anomaly-prone temperature sensor (will trigger anomaly detection) ---
    anomaly_schema = {"sensor_id": str, "time": str, "temperature": float}
    anomaly_source = DataSource(
        source_id="anomaly_temp_001",
        name="Anomaly Temperature Sensor",
        source_type="API",
        url="https://mockapi.com/tempsensor", # Placeholder
        schema_expected=anomaly_schema,
        frequency_seconds=5
    )
    class MockAnomalyApiData:
        def __init__(self, is_anomaly=False):
            self._is_anomaly = is_anomaly
        def json(self):
            temp_val = 150.0 if self._is_anomaly else 25.0 # Injected anomaly
            return {
                "sensor_id": "temp_sensor_A",
                "time": datetime.utcnow().isoformat(),
                "temperature": temp_val
            }
        async def text(self): return ""
        def raise_for_status(self): pass

    original_get_anomaly = aiohttp.ClientSession.get
    async def mock_get_anomaly(self, url, *args, **kwargs):
        if url == "https://mockapi.com/tempsensor":
            if (datetime.utcnow().second % 10) < 3: # Make it anomalous for a few seconds
                 logging.info("MOCK: Returning anomalous temperature data.")
                 return MockAnomalyApiData(is_anomaly=True)
            logging.info("MOCK: Returning normal temperature data.")
            return MockAnomalyApiData(is_anomaly=False)
        return await original_get_anomaly(self, url, *args, **kwargs)
    aiohttp.ClientSession.get = mock_get_anomaly


    ingest_manager.register_source(anomaly_source)


    # Start the ingestion loop in a separate thread to keep main thread responsive
    ingestion_thread = threading.Thread(target=ingest_manager.start_ingestion)
    ingestion_thread.start()

    try:
        # Let it run for a while to demonstrate behavior
        print("\nIngestion Manager running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
            # You could add runtime commands here, like adding new sources, checking status
            # For example, print current status of sources:
            # for sid, source in ingest_manager.data_sources.items():
            #     print(f"Source {sid}: Status={source.status}, Errors={source.error_count}, Last Ingest={source.last_ingested_at}")
    except KeyboardInterrupt:
        print("\nStopping Ingestion Manager...")
        ingest_manager.stop_ingestion()
        ingestion_thread.join()
        print("Ingestion Manager stopped cleanly.")

    # Restore original aiohttp.ClientSession.get (good practice if in larger app)
    aiohttp.ClientSession.get = original_get
    aiohttp.ClientSession.get = original_get_anomaly # This will overwrite the first one, but for example, fine.
