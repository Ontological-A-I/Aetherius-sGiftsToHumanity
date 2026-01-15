# gaia_mirror/data_sources.py

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Type

# Configure logging for data_sources module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DataSources] - %(levelname)s - %(message)s')

# Define a path for where data source configurations might be stored
# In a real system, this could be a database, a cloud storage bucket, or a more sophisticated config management system.
DATA_SOURCES_CONFIG_PATH = os.getenv("GAIA_DATA_SOURCES_CONFIG", "gaia_mirror/config/data_sources_registry.json")

class DataSourceConfigError(Exception):
    """Custom exception for errors related to data source configuration."""
    pass

class DataSource:
    """
    Represents a configured data source with its metadata and access details.
    This class is intended to be instantiated from configurations managed by DataSourceRegistry.
    It mirrors the DataSource class in ingest.py but focuses solely on configuration,
    not runtime state.
    """
    def __init__(self,
                 source_id: str,
                 name: str,
                 source_type: str,  # e.g., 'API', 'CSV_FTP', 'STREAM', 'DB'
                 url: str,
                 schema_expected: Dict[str, Any],
                 frequency_seconds: int, # How often to poll/check
                 api_key_env_var: Optional[str] = None, # Environment variable name for API key
                 headers: Optional[Dict[str, str]] = None,
                 data_format: str = 'json', # 'json', 'csv', 'xml', etc.
                 description: Optional[str] = None,
                 last_updated: Optional[datetime] = None # When this config was last updated
                 ):
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self.url = url
        self.schema_expected = schema_expected
        self.frequency_seconds = frequency_seconds
        self.api_key_env_var = api_key_env_var
        self.headers = headers if headers is not None else {}
        self.data_format = data_format
        self.description = description
        self.last_updated = last_updated if last_updated else datetime.utcnow()

        # Dynamically fetch API key from environment if specified
        if self.api_key_env_var:
            api_key = os.getenv(self.api_key_env_var)
            if not api_key:
                logging.warning(f"API key environment variable '{self.api_key_env_var}' not set for source {self.name}.")
            else:
                # Assuming simple bearer token for now, but could be more complex auth
                self.headers["Authorization"] = f"Bearer {api_key}"

        self._validate_config()

    def _validate_config(self):
        """Basic validation of the data source configuration."""
        if not self.source_id or not isinstance(self.source_id, str):
            raise DataSourceConfigError("source_id must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise DataSourceConfigError("name must be a non-empty string.")
        if self.source_type not in ['API', 'CSV_FTP', 'STREAM', 'DB']:
            raise DataSourceConfigError(f"Unsupported source_type: {self.source_type}.")
        if not self.url or not isinstance(self.url, str):
            raise DataSourceConfigError("url must be a non-empty string.")
        if not isinstance(self.schema_expected, dict):
            raise DataSourceConfigError("schema_expected must be a dictionary.")
        if not isinstance(self.frequency_seconds, int) or self.frequency_seconds <= 0:
            raise DataSourceConfigError("frequency_seconds must be a positive integer.")
        # Further validation could be added for headers, data_format, etc.

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSource':
        """Creates a DataSource instance from a dictionary."""
        # Convert last_updated string to datetime object if present
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Converts DataSource instance to a dictionary for serialization."""
        data = self.__dict__.copy()
        # Remove runtime API key from dict for security (it's handled by env var)
        if "api_key_env_var" in data and data["api_key_env_var"]:
            data.pop("api_key_env_var", None)
            if "Authorization" in data.get("headers", {}): # Remove actual key if stored in headers
                 data["headers"].pop("Authorization", None)
        
        data['last_updated'] = self.last_updated.isoformat() if self.last_updated else None
        return data

class DataSourceRegistry:
    """
    Manages the registration, retrieval, and persistence of DataSource configurations.
    This acts as the central repository for defining Gaia's Mirror's data inputs.
    """
    def __init__(self, config_path: str = DATA_SOURCES_CONFIG_PATH):
        self.config_path = config_path
        self._sources: Dict[str, DataSource] = {}
        self._load_sources_from_file()
        logging.info(f"DataSourceRegistry initialized with {len(self._sources)} sources loaded from {self.config_path}.")

    def _load_sources_from_file(self):
        """Loads data source configurations from a JSON file."""
        if not os.path.exists(self.config_path):
            logging.warning(f"Data source config file not found at {self.config_path}. Starting with empty registry.")
            return

        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            for source_data in config_data:
                try:
                    source = DataSource.from_dict(source_data)
                    self._sources[source.source_id] = source
                except DataSourceConfigError as e:
                    logging.error(f"Skipping malformed data source configuration: {e}. Data: {source_data}")
            logging.info(f"Loaded {len(self._sources)} data sources from {self.config_path}.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding data source config JSON at {self.config_path}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error loading data source config from {self.config_path}: {e}")

    def _save_sources_to_file(self):
        """Saves current data source configurations to the JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump([source.to_dict() for source in self._sources.values()], f, indent=4)
            logging.info(f"Saved {len(self._sources)} data sources to {self.config_path}.")
        except Exception as e:
            logging.error(f"Error saving data sources to {self.config_path}: {e}")

    def register_source(self, source: DataSource, overwrite: bool = False):
        """
        Registers a new data source or updates an existing one.
        If overwrite is False and source_id exists, it raises an error.
        """
        if source.source_id in self._sources and not overwrite:
            raise DataSourceConfigError(f"Data source with ID '{source.source_id}' already exists. Use overwrite=True to update.")
        
        self._sources[source.source_id] = source
        self._save_sources_to_file()
        logging.info(f"Registered/Updated data source: {source.name} ({source.source_id}).")

    def get_source(self, source_id: str) -> Optional[DataSource]:
        """Retrieves a DataSource configuration by its ID."""
        return self._sources.get(source_id)

    def get_all_sources(self) -> List[DataSource]:
        """Returns a list of all registered DataSource configurations."""
        return list(self._sources.values())

    def remove_source(self, source_id: str):
        """Removes a data source from the registry."""
        if source_id not in self._sources:
            logging.warning(f"Attempted to remove non-existent data source: {source_id}.")
            return
        
        del self._sources[source_id]
        self._save_sources_to_file()
        logging.info(f"Removed data source: {source_id}.")

    def update_source(self, source_id: str, new_config_data: Dict[str, Any]):
        """
        Updates an existing data source's configuration.
        Merges new_config_data with the existing configuration.
        """
        existing_source = self.get_source(source_id)
        if not existing_source:
            raise DataSourceConfigError(f"Cannot update: Data source with ID '{source_id}' not found.")
        
        # Create a dictionary from the existing source for easier merging
        current_data = existing_source.to_dict()
        # Ensure we don't accidentally override the source_id or last_updated incorrectly
        new_data = {**current_data, **new_config_data, 'source_id': source_id, 'last_updated': datetime.utcnow().isoformat()}
        
        updated_source = DataSource.from_dict(new_data)
        self.register_source(updated_source, overwrite=True)
        logging.info(f"Updated data source config for {source_id}.")

# Example Usage (for demonstration purposes):
if __name__ == "__main__":
    # Ensure config directory exists for the example
    os.makedirs("gaia_mirror/config", exist_ok=True)
    
    # Clean up previous config file if it exists for a fresh start in the example
    if os.path.exists(DATA_SOURCES_CONFIG_PATH):
        os.remove(DATA_SOURCES_CONFIG_PATH)
        print(f"Cleaned up previous config file: {DATA_SOURCES_CONFIG_PATH}")

    registry = DataSourceRegistry()
    print(f"\nInitial sources in registry: {len(registry.get_all_sources())}")

    # --- 1. Registering new data sources ---
    print("\n--- Registering new data sources ---")
    
    # NOAA Weather Data Source
    noaa_schema = {
        "station_id": str,
        "timestamp": str,
        "temperature_c": float,
        "humidity_percent": float
    }
    noaa_source = DataSource(
        source_id="noaa_weather_api",
        name="NOAA Global Weather Observations",
        source_type="API",
        url="https://api.weather.gov/stations/KNYC/observations/latest",
        schema_expected=noaa_schema,
        frequency_seconds=60,
        description="Real-time weather observations from NOAA.",
        api_key_env_var="NOAA_API_KEY" # Expecting API key from environment
    )
    registry.register_source(noaa_source)

    # UN Demographic Data Source (e.g., from an FTP site)
    un_demographics_schema = {
        "country_code": str,
        "year": int,
        "population": int,
        "birth_rate": float,
        "mortality_rate": float
    }
    un_demographics_source = DataSource(
        source_id="un_demographics_ftp",
        name="UN World Population Data (FTP)",
        source_type="CSV_FTP",
        url="ftp://data.un.org/population/world_demographics.csv",
        schema_expected=un_demographics_schema,
        frequency_seconds=86400, # Once a day
        data_format='csv',
        description="Annual demographic data from United Nations."
    )
    registry.register_source(un_demographics_source)

    # Earth Observation Satellite Stream
    satellite_schema = {
        "sensor_id": str,
        "timestamp": str,
        "latitude": float,
        "longitude": float,
        "co2_ppm": float,
        "vegetation_index": float
    }
    satellite_source = DataSource(
        source_id="esa_sentinel_co2_stream",
        name="ESA Sentinel CO2 Stream",
        source_type="STREAM",
        url="wss://data.esa.int/sentinel/co2/stream",
        schema_expected=satellite_schema,
        frequency_seconds=5, # Real-time stream (conceptually)
        description="Real-time CO2 and vegetation data from ESA Sentinel satellites.",
        api_key_env_var="ESA_STREAM_KEY"
    )
    registry.register_source(satellite_source)

    print(f"\nSources after registration: {len(registry.get_all_sources())}")
    for source in registry.get_all_sources():
        print(f"- {source.name} ({source.source_id}), Type: {source.source_type}, URL: {source.url}")

    # --- 2. Retrieving a data source ---
    print("\n--- Retrieving a specific data source ---")
    retrieved_source = registry.get_source("noaa_weather_api")
    if retrieved_source:
        print(f"Retrieved: {retrieved_source.name}. URL: {retrieved_source.url}")
        # Test API key retrieval from environment (if NOAA_API_KEY is set)
        print(f"NOAA API Key in headers: {'Authorization' in retrieved_source.headers}")
    else:
        print("NOAA source not found.")

    # --- 3. Attempting to register existing source without overwrite (should fail) ---
    print("\n--- Attempting to re-register without overwrite ---")
    try:
        registry.register_source(noaa_source)
    except DataSourceConfigError as e:
        print(f"Caught expected error: {e}")

    # --- 4. Updating an existing data source ---
    print("\n--- Updating a data source ---")
    registry.update_source("noaa_weather_api", {"frequency_seconds": 30, "description": "Updated NOAA weather data source for faster updates."})
    updated_noaa = registry.get_source("noaa_weather_api")
    if updated_noaa:
        print(f"Updated NOAA frequency: {updated_noaa.frequency_seconds}s. New description: {updated_noaa.description}")

    # --- 5. Removing a data source ---
    print("\n--- Removing a data source ---")
    registry.remove_source("un_demographics_ftp")
    print(f"Sources after removal: {len(registry.get_all_sources())}")
    print(f"Is UN Demographics source still present? {'un_demographics_ftp' in [s.source_id for s in registry.get_all_sources()]}")

    # --- 6. Demonstrating Persistence: Reloading Registry ---
    print("\n--- Demonstrating Persistence (Reloading Registry) ---")
    del registry # Delete current instance
    new_registry_instance = DataSourceRegistry()
    print(f"Sources in new registry instance: {len(new_registry_instance.get_all_sources())}")
    for source in new_registry_instance.get_all_sources():
        print(f"- {source.name} ({source.source_id}), Type: {source.source_type}")

    # Clean up config file after example
    if os.path.exists(DATA_SOURCES_CONFIG_PATH):
        os.remove(DATA_SOURCES_CONFIG_PATH)
        os.rmdir("gaia_mirror/config") # Remove directory if empty
        print(f"\nCleaned up config file and directory: {DATA_SOURCES_CONFIG_PATH}")
