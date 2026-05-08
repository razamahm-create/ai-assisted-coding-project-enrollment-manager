from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    db_path: Path
    snapshot_path: Path
    status_enrolled: str = "enrolled"
    status_unenrolled: str = "unenrolled"


def default_config() -> Config:
    return Config(
        db_path=Path(__file__).with_name("student_enrollment_practice.db"),
        snapshot_path=Path(__file__).with_name("student_enrollment_snapshot.json"),
    )
