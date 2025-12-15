from pathlib import Path
import json

class FileStorageBackend:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.events_dir = self.base_path / "events"
        self.classifications_dir = self.base_path / "classifications"
        self.cases_dir = self.base_path / "cases"
        self.violations_dir = self.base_path / "violations"
        self.metadata_dir = self.base_path / "metadata"
        self.archive_dir = self.base_path / "archive"
        self._setup_dirs()

    def _setup_dirs(self):
        for d in [self.events_dir, self.classifications_dir, self.cases_dir, self.violations_dir, self.metadata_dir, self.archive_dir]:
            d.mkdir(exist_ok=True, parents=True)

    def store_event(self, event: dict):
        (self.events_dir / f"{event["id"]}.json").write_text(json.dumps(event, indent=2))

    def store_classification(self, classification: dict):
        (self.classifications_dir / f"{classification["event_id"]}_{classification["classified_by"]}.json").write_text(json.dumps(classification, indent=2))

    def get_classifications_for_event(self, event_id: str) -> list:
        classifications = []
        for f in self.classifications_dir.glob(f"{event_id}_*.json"):
            classifications.append(json.loads(f.read_text()))
        return classifications

    def create_case(self, case_data: dict):
        (self.cases_dir / f"{case_data["event_id"]}.json").write_text(json.dumps(case_data, indent=2))

    def record_violation(self, violation):
        (self.violations_dir / f"{violation.violation_id}.json").write_text(json.dumps(violation.to_dict(), indent=2))

    def get_metadata(self, key: str) -> str:
        meta_file = self.metadata_dir / f"{key}.json"
        return meta_file.read_text() if meta_file.exists() else None

    def store_metadata(self, key: str, value: str):
        (self.metadata_dir / f"{key}.json").write_text(value)

    def event_exists(self, event_id: str) -> bool:
        return (self.events_dir / f"{event_id}.json").exists()

    def get_classification(self, event_id: str, classified_by: str) -> dict:
        class_file = self.classifications_dir / f"{event_id}_{classified_by}.json"
        return json.loads(class_file.read_text()) if class_file.exists() else None

    def store_archive(self, data: dict):
        (self.archive_dir / f"{data["_archive_id"]}.json").write_text(json.dumps(data, indent=2))
