from dataclasses import dataclass #acts as decorator for classes that are primarily used to store data.

@dataclass
class DataIngestionArtifact:
    training_file_path: str
    testing_file_path: str
    
@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str
