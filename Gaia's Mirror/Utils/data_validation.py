# gaia_mirror/utils/data_validation.py

import logging
from typing import Dict, Any, List, Union, Callable, Optional, Tuple
from datetime import datetime, date

# Configure logging for the data_validation module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DataValidation] - %(levelname)s - %(message)s')

class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.details = details if details is not None else {}
        logging.warning(f"Data Validation Error: {message} (Field: {field}, Value: {value}, Details: {details})")

class DataValidator:
    """
    Provides a suite of robust data validation methods to ensure data quality
    before it is processed by other Gaia's Mirror modules (e.g., engine, simulator).
    """
    def __init__(self):
        logging.info("DataValidator initialized.")

    def _get_type_validator(self, expected_type: Union[Type, Tuple[Type, ...]]) -> Callable[[Any], bool]:
        """Returns a callable that checks if a value matches the expected type(s)."""
        def validator_func(value: Any) -> bool:
            if isinstance(expected_type, tuple):
                return isinstance(value, expected_type)
            return isinstance(value, expected_type)
        return validator_func

    def validate_schema(self, data: Dict[str, Any], schema: Dict[str, Union[Type, Tuple[Type, ...]]], strict: bool = False) -> bool:
        """
        Validates if a dictionary adheres to a specified schema.
        :param data: The dictionary data to validate.
        :param schema: A dictionary where keys are expected fields and values are expected types (or tuples of types).
                       Example: {'name': str, 'age': int, 'score': (int, float)}
        :param strict: If True, flags extra fields not present in the schema as errors.
        :return: True if data is valid, False otherwise. Raises DataValidationError on first failure.
        """
        if not isinstance(data, dict):
            raise DataValidationError("Data must be a dictionary for schema validation.", value=data)

        # Check for missing or incorrect types for required fields
        for field, expected_type in schema.items():
            if field not in data:
                raise DataValidationError(f"Missing required field: '{field}'", field=field)
            
            value = data[field]
            type_validator = self._get_type_validator(expected_type)
            if not type_validator(value):
                raise DataValidationError(
                    f"Field '{field}' has incorrect type. Expected {expected_type}, got {type(value)}",
                    field=field, value=value
                )
        
        # Check for extra fields if strict mode is enabled
        if strict:
            extra_fields = set(data.keys()) - set(schema.keys())
            if extra_fields:
                raise DataValidationError(f"Unexpected field(s) found: {', '.join(extra_fields)}", details={"extra_fields": list(extra_fields)})

        logging.debug("Schema validation passed.")
        return True

    def validate_range(self, value: Union[int, float], field_name: str, min_val: Optional[Union[int, float]] = None, max_val: Optional[Union[int, float]] = None) -> bool:
        """
        Validates if a numerical value falls within a specified range.
        :param value: The numerical value to check.
        :param field_name: The name of the field being validated.
        :param min_val: The minimum allowed value (inclusive).
        :param max_val: The maximum allowed value (inclusive).
        :return: True if valid, False otherwise. Raises DataValidationError.
        """
        if not isinstance(value, (int, float)):
            raise DataValidationError(f"Field '{field_name}' must be numeric for range validation.", field=field_name, value=value)

        if min_val is not None and value < min_val:
            raise DataValidationError(f"Value for '{field_name}' ({value}) is below minimum ({min_val}).", field=field_name, value=value, details={"min_expected": min_val})
        if max_val is not None and value > max_val:
            raise DataValidationError(f"Value for '{field_name}' ({value}) is above maximum ({max_val}).", field=field_name, value=value, details={"max_expected": max_val})
        
        logging.debug(f"Range validation passed for '{field_name}'.")
        return True

    def validate_enum(self, value: Any, field_name: str, allowed_values: List[Any]) -> bool:
        """
        Validates if a value is one of the allowed enumerated values.
        :param value: The value to check.
        :param field_name: The name of the field being validated.
        :param allowed_values: A list of values considered valid.
        :return: True if valid, False otherwise. Raises DataValidationError.
        """
        if value not in allowed_values:
            raise DataValidationError(
                f"Value for '{field_name}' ({value}) is not in allowed values: {allowed_values}",
                field=field_name, value=value, details={"allowed_values": allowed_values}
            )
        logging.debug(f"Enum validation passed for '{field_name}'.")
        return True

    def validate_format(self, value: str, field_name: str, pattern: Optional[str] = None, format_type: Optional[str] = None) -> bool:
        """
        Validates the format of a string, e.g., email, UUID, date string, custom regex.
        :param value: The string value to check.
        :param field_name: The name of the field being validated.
        :param pattern: A regex pattern to match.
        :param format_type: Predefined format types like 'email', 'iso_datetime'.
        :return: True if valid, False otherwise. Raises DataValidationError.
        """
        if not isinstance(value, str):
            raise DataValidationError(f"Field '{field_name}' must be a string for format validation.", field=field_name, value=value)

        if pattern:
            import re
            if not re.match(pattern, value):
                raise DataValidationError(f"Value for '{field_name}' ({value}) does not match regex pattern '{pattern}'.", field=field_name, value=value)
        elif format_type == 'email':
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, value):
                raise DataValidationError(f"Value for '{field_name}' ({value}) is not a valid email format.", field=field_name, value=value)
        elif format_type == 'iso_datetime':
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00')) # Handles Z for UTC
            except ValueError:
                raise DataValidationError(f"Value for '{field_name}' ({value}) is not a valid ISO 8601 datetime format.", field=field_name, value=value)
        else:
            logging.warning(f"No specific format or pattern provided for '{field_name}'. Skipping format validation.")
            return True # If no specific validation is requested, consider it passed

        logging.debug(f"Format validation passed for '{field_name}'.")
        return True

    def check_for_missing_values(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Checks if any of the specified required fields are missing or have None/empty string values.
        :param data: The dictionary data to check.
        :param required_fields: A list of field names that must be present and not empty.
        :return: True if all required fields are present and not empty, False otherwise. Raises DataValidationError.
        """
        missing = []
        empty = []
        for field in required_fields:
            if field not in data:
                missing.append(field)
            elif data[field] is None:
                empty.append(field)
            elif isinstance(data[field], str) and not data[field].strip():
                empty.append(field)
            elif isinstance(data[field], (list, dict)) and not data[field]:
                 empty.append(field) # Treat empty lists/dicts as empty if context implies
        
        if missing:
            raise DataValidationError(f"Missing required fields: {', '.join(missing)}", details={"missing_fields": missing})
        if empty:
            raise DataValidationError(f"Required fields are empty: {', '.join(empty)}", details={"empty_fields": empty})
        
        logging.debug("Missing value check passed.")
        return True

    def check_consistency(self, data: Dict[str, Any], consistency_rules: List[Callable[[Dict[str, Any]], bool]]) -> bool:
        """
        Applies a list of custom consistency rules (functions) to the data.
        Each rule function should take the data dict and return True if consistent, False otherwise.
        :param data: The dictionary data to check.
        :param consistency_rules: A list of callable functions (rules).
        :return: True if all rules pass, False otherwise. Raises DataValidationError on first failure.
        """
        for i, rule in enumerate(consistency_rules):
            try:
                if not rule(data):
                    raise DataValidationError(f"Consistency rule failed (Rule index: {i})", details={"rule_index": i, "rule_name": rule.__name__})
            except Exception as e:
                # Catch errors within the rule function itself
                raise DataValidationError(f"Consistency rule raised an error (Rule index: {i}): {e}", details={"rule_index": i, "rule_name": rule.__name__, "error": str(e)})
        logging.debug("Consistency checks passed.")
        return True

    def validate_data_point(self, data_point: Dict[str, Any], validation_rules: Dict[str, Any]) -> bool:
        """
        Performs a comprehensive validation on a single data point using a set of defined rules.
        :param data_point: The dictionary representing a single data record.
        :param validation_rules: A dictionary containing rules for schema, range, enum, format, etc.
                                 Example:
                                 {
                                     "schema": {"field1": str, "field2": float},
                                     "schema_strict": True,
                                     "required_fields": ["field1"],
                                     "field_ranges": {"field2": {"min": 0, "max": 100}},
                                     "field_enums": {"field3": ["typeA", "typeB"]},
                                     "field_formats": {"timestamp": {"format_type": "iso_datetime"}},
                                     "consistency_rules": [lambda d: d['field1'] != d['field2']]
                                 }
        :return: True if the data point passes all validations, False otherwise. Raises DataValidationError.
        """
        if "schema" in validation_rules:
            self.validate_schema(data_point, validation_rules["schema"], validation_rules.get("schema_strict", False))
        
        if "required_fields" in validation_rules:
            self.check_for_missing_values(data_point, validation_rules["required_fields"])

        if "field_ranges" in validation_rules:
            for field, bounds in validation_rules["field_ranges"].items():
                if field in data_point:
                    self.validate_range(data_point[field], field, bounds.get("min"), bounds.get("max"))

        if "field_enums" in validation_rules:
            for field, allowed in validation_rules["field_enums"].items():
                if field in data_point:
                    self.validate_enum(data_point[field], field, allowed)

        if "field_formats" in validation_rules:
            for field, format_spec in validation_rules["field_formats"].items():
                if field in data_point:
                    self.validate_format(data_point[field], field, format_spec.get("pattern"), format_spec.get("format_type"))
        
        if "consistency_rules" in validation_rules:
            self.check_consistency(data_point, validation_rules["consistency_rules"])

        logging.info("Data point passed all validation rules.")
        return True


# Example Usage (typically ingest.py would use this):
if __name__ == "__main__":
    validator = DataValidator()

    # --- Define a sample schema and rules ---
    sample_schema = {
        "id": str,
        "temperature": (int, float),
        "humidity": (int, float),
        "sensor_status": str,
        "timestamp": str,
        "location": str,
        "measurements": list,
        "optional_note": Optional[str] # Fields not in schema but present in data will be flagged if strict=True
    }

    validation_rules_set1 = {
        "schema": sample_schema,
        "schema_strict": True,
        "required_fields": ["id", "temperature", "timestamp", "location", "measurements"],
        "field_ranges": {
            "temperature": {"min": -50.0, "max": 70.0},
            "humidity": {"min": 0, "max": 100}
        },
        "field_enums": {
            "sensor_status": ["operational", "maintenance", "error"]
        },
        "field_formats": {
            "timestamp": {"format_type": "iso_datetime"}
        },
        "consistency_rules": [
            lambda d: all(isinstance(m, (int, float)) for m in d.get('measurements', [])) # All measurements must be numeric
        ]
    }

    print("\n--- Test Case 1: Valid Data ---")
    valid_data = {
        "id": "sensor_001",
        "temperature": 25.5,
        "humidity": 60,
        "sensor_status": "operational",
        "timestamp": "2023-10-27T10:00:00Z",
        "location": "North America",
        "measurements": [10, 20, 30],
        "optional_note": "Everything looks good."
    }
    try:
        validator.validate_data_point(valid_data, validation_rules_set1)
        print("Valid data passed all checks.")
    except DataValidationError as e:
        print(f"Valid data failed validation (unexpected): {e}")

    print("\n--- Test Case 2: Missing Required Field ---")
    missing_field_data = {**valid_data, "location": None} # Simulate missing 'location'
    del missing_field_data['location']
    try:
        validator.validate_data_point(missing_field_data, validation_rules_set1)
        print("Missing field data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Missing field data failed as expected: {e}")

    print("\n--- Test Case 3: Incorrect Data Type ---")
    incorrect_type_data = {**valid_data, "temperature": "twenty-five"}
    try:
        validator.validate_data_point(incorrect_type_data, validation_rules_set1)
        print("Incorrect type data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Incorrect type data failed as expected: {e}")

    print("\n--- Test Case 4: Out of Range Value ---")
    out_of_range_data = {**valid_data, "humidity": 101}
    try:
        validator.validate_data_point(out_of_range_data, validation_rules_set1)
        print("Out of range data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Out of range data failed as expected: {e}")

    print("\n--- Test Case 5: Invalid Enum Value ---")
    invalid_enum_data = {**valid_data, "sensor_status": "broken"}
    try:
        validator.validate_data_point(invalid_enum_data, validation_rules_set1)
        print("Invalid enum data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Invalid enum data failed as expected: {e}")

    print("\n--- Test Case 6: Invalid Date Format ---")
    invalid_date_data = {**valid_data, "timestamp": "2023/10/27 10-00-00"}
    try:
        validator.validate_data_point(invalid_date_data, validation_rules_set1)
        print("Invalid date format data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Invalid date format data failed as expected: {e}")

    print("\n--- Test Case 7: Extra Field (Strict Schema) ---")
    extra_field_data = {**valid_data, "extra_field": "unwanted_data"}
    try:
        validator.validate_data_point(extra_field_data, validation_rules_set1)
        print("Extra field data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Extra field data failed as expected: {e}")
    
    print("\n--- Test Case 8: Consistency Rule Failure ---")
    inconsistent_data = {**valid_data, "measurements": ["a", "b", 1]} # Fails consistency rule: all measurements must be numeric
    try:
        validator.validate_data_point(inconsistent_data, validation_rules_set1)
        print("Inconsistent data passed validation (unexpected).")
    except DataValidationError as e:
        print(f"Inconsistent data failed as expected: {e}")
