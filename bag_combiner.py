import re
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import rosbag2_py
import yaml


def get_combined_folder(folder: Path) -> Path:
    """Name the combined bag using the recording time or the current local time."""
    match = re.search(
        r"(\d{4}-\d{2}-\d{2})[_-](\d{1,2}-\d{1,2}-\d{1,2})$",
        folder.resolve().name,
    )
    timestamp = None
    if match:
        try:
            timestamp = datetime.strptime(f"{match[1]}_{match[2]}", "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            pass
    if timestamp is None:
        timestamp = datetime.now()
    return folder.with_name(f"combined_ros2_bag_{timestamp:%Y-%m-%d_%H-%M-%S}")


def find_rosbags(folder: Path) -> list[Path]:
    """Find neighboring bags and check metadata and referenced file existence."""
    folder = folder.resolve()
    bags = []
    for candidate in sorted(folder.parent.iterdir()):
        if candidate == folder:
            continue
        if not candidate.is_dir() or not (candidate / "metadata.yaml").is_file():
            continue
        try:
            metadata = rosbag2_py.Info().read_metadata(str(candidate), "")
        except RuntimeError as error:
            raise ValueError(f"Invalid ROS bag metadata: {candidate}") from error
        if not metadata.relative_file_paths:
            raise ValueError(f"No data files listed in ROS bag: {candidate}")
        for file_path in metadata.relative_file_paths:
            if not (candidate / file_path).is_file():
                raise FileNotFoundError(f"ROS bag data file missing: {candidate / file_path}")
        bags.append(candidate)
    return bags


def combine_rosbags(bags: list[Path], output_folder: Path) -> None:
    """Merge bags into a new MCAP bag without changing the inputs."""
    if not bags:
        raise ValueError("No ROS bags provided for combining")
    if output_folder.exists() or output_folder.is_symlink():
        raise FileExistsError(f"Output already exists: {output_folder}")

    inputs = [rosbag2_py.StorageOptions(uri=str(bag)) for bag in bags]
    options = {
        "output_bags": [{
            "uri": str(output_folder),
            "storage_id": "mcap",
            "all_topics": True,
            "all_services": True,
            "include_hidden_topics": True,
        }]
    }
    # bag_rewrite reads its output settings from a YAML file.
    with NamedTemporaryFile(mode="w", suffix=".yaml", encoding="utf-8") as config:
        yaml.safe_dump(options, config)
        config.flush()
        # Jazzy bag_rewrite does not preserve topic type_description_hash values.
        rosbag2_py.bag_rewrite(inputs, config.name)
