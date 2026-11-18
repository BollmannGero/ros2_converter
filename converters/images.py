import struct

from builtin_interfaces.msg import Time
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Header

from .rvl import parse_rvl_file


def make_rgb_message(data: bytes, timestamp: int, frame_id: str) -> CompressedImage:
    """Wrap existing JPEG bytes in a ROS CompressedImage without recompression."""
    seconds, nanoseconds = divmod(timestamp, 1_000_000_000)
    return CompressedImage(
        header=Header(
            stamp=Time(sec=seconds, nanosec=nanoseconds),
            frame_id=frame_id,
        ),
        format="jpeg",
        data=data,
    )


def make_depth_message(data: bytes, timestamp: int, frame_id: str) -> CompressedImage:
    """Replace the RVL1 file header with a ROS compressedDepth RVL header."""
    width, height, payload = parse_rvl_file(data)
    # Jazzy ConfigHeader: INV_DEPTH=0; the two float parameters are unused for 16UC1.
    compression_header = struct.pack("<iff", 0, 0.0, 0.0)
    image_size = struct.pack("<II", width, height)
    seconds, nanoseconds = divmod(timestamp, 1_000_000_000)
    return CompressedImage(
        header=Header(
            stamp=Time(sec=seconds, nanosec=nanoseconds),
            frame_id=frame_id,
        ),
        format="16UC1; compressedDepth rvl",
        data=compression_header + image_size + payload,
    )


# Each stream defines its converter, frame template, and full topic template.
IMAGE_CONVERTERS = {
    "rgb_file": (
        make_rgb_message,
        "{sensor_name}_color_optical_frame",
        "/camera/{sensor_name}/color/image_raw/compressed",
    ),
    "depth_file": (
        make_depth_message,
        "{sensor_name}_depth_optical_frame",
        "/camera/{sensor_name}/depth/image_raw/compressedDepth",
    ),
}
