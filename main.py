import argparse
import csv
import re
from pathlib import Path

from bag_combiner import combine_rosbags, find_rosbags, get_combined_folder
from bag_writer import write_bag
from converters import MESSAGE_CONVERTERS
from metadata import read_metadata, validate_metadata


def read_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert recorded data to a ROS2 MCAP bag.")
    parser.add_argument("folder", type=Path, help="Input folder, optionally named <sensor>_YYYY-MM-DD_HH-MM-SS")
    parser.add_argument(
        "--combine-rosbags",
        action="store_true",
        help="Combine the converted bag with all neighboring ROS bags into an additional MCAP bag",
    )

    return parser.parse_args()


def parse_timestamp(timestamp: str) -> int:
    """Convert seconds.nanoseconds (nine fractional digits) without rounding."""
    seconds, nanoseconds = timestamp.split(".")
    return int(seconds) * 1_000_000_000 + int(nanoseconds)


def get_sensor_name(folder: Path) -> str:
    """Remove a recording timestamp if present; otherwise use the folder name."""
    match = re.fullmatch(
        r"(.+)_\d{4}-\d{2}-\d{2}[_-]\d{1,2}-\d{1,2}-\d{1,2}", folder.resolve().name
    )
    return match.group(1) if match else folder.resolve().name


def read_index(folder: Path) -> list[dict[str, str]]:
    """Load the CSV index and sort by logger reception time."""
    with (folder / "index.csv").open(newline="", encoding="utf-8") as file:
        entries = list(csv.DictReader(file))
    return sorted(entries, key=lambda entry: parse_timestamp(entry["recv_stamp"]))


def iter_messages(folder: Path, entries: list[dict[str, str]], sensor_name: str):
    """Yield (column, topic, message, bag timestamp) one file at a time."""
    for entry in entries:
        for column, (converter, frame_template, topic_template) in MESSAGE_CONVERTERS.items():
            file_path = entry.get(column)
            if not file_path or not (folder / file_path).is_file():
                continue
            data = (folder / file_path).read_bytes()
            # Keep acquisition time in the header and reception time in the bag.
            timestamp = parse_timestamp(entry["stamp"])
            bag_timestamp = parse_timestamp(entry["recv_stamp"])
            frame_id = frame_template.format(sensor_name=sensor_name)
            topic = topic_template.format(sensor_name=sensor_name)
            message = converter(data, timestamp, frame_id)
            yield column, topic, message, bag_timestamp


def main() -> None:
    args = read_arguments()
    folder = args.folder
    sensor_name = get_sensor_name(folder)
    output_folder = folder.with_name(folder.name + "_rosbag")
    metadata = read_metadata(folder)
    entries = read_index(folder)
    columns = entries[0].keys() if entries else []
    # Reject unsupported input formats before creating the output bag.
    validate_metadata(metadata, columns)
    message_counts = dict.fromkeys(MESSAGE_CONVERTERS, 0)
    messages = iter_messages(folder, entries, sensor_name)
    message_counts.update(write_bag(output_folder, messages))
    for column, count in message_counts.items():
        if column not in columns:
            continue
        empty = sum(not entry.get(column) for entry in entries)
        missing = len(entries) - empty - count
        print(
            f"{column}: {count} written, {missing} missing files, "
            f"{empty} without a file path"
        )
    print(f"Bag saved: {output_folder}")
    if args.combine_rosbags:
        bags = find_rosbags(folder)
        print("Bags to combine:")
        for bag in bags:
            print(f"  {bag}")
        combined_folder = get_combined_folder(folder)
        combine_rosbags(bags, combined_folder)
        print(f"Combined bag saved: {combined_folder}")


if __name__ == "__main__":
    main()

