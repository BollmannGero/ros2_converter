from pathlib import Path

import rosbag2_py
from rclpy.serialization import serialize_message


def write_bag(output_folder: Path, messages) -> dict[str, int]:
    """Write streamed ROS messages to a new MCAP bag and return counts per column."""
    if output_folder.exists() or output_folder.is_symlink():
        raise FileExistsError(f"Output already exists: {output_folder}")

    writer = rosbag2_py.SequentialWriter()
    writer.open(
        rosbag2_py.StorageOptions(uri=str(output_folder), storage_id="mcap"),
        rosbag2_py.ConverterOptions("cdr", "cdr"),
    )
    topic_types = {}
    message_counts = {}
    try:
        for column, topic, message, bag_timestamp in messages:
            # Generated ROS message classes identify their package and message name.
            message_class = type(message)
            package = message_class.__module__.split(".")[0]
            type_name = f"{package}/msg/{message_class.__name__}"
            if topic not in topic_types:
                writer.create_topic(
                    rosbag2_py.TopicMetadata(
                        id=len(topic_types),
                        name=topic,
                        type=type_name,
                        serialization_format="cdr",
                    )
                )
                topic_types[topic] = type_name
            elif topic_types[topic] != type_name:
                raise ValueError(f"Message type changes within topic: {topic}")

            writer.write(topic, serialize_message(message), bag_timestamp)
            message_counts[column] = message_counts.get(column, 0) + 1
    finally:
        # Finalize the bag even if conversion or writing raises an exception.
        writer.close()

    return message_counts
