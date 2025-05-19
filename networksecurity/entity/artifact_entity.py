from dataclasses import dataclass #acts as decorator for classes that are primarily used to store data.

@dataclass
class DataIngestionArtifact:
    training_file_path: str
    testing_file_path: str
