"""Example script to move all joints a little bit.

Make sure you have configured and zeroed the joints before running this script.
"""

# Standard library imports
import logging
import time
import traceback
import pykos  # type: ignore[import-untyped]

# Third-party imports
import colorlogging

# Local imports
import move_joint_a_little 
from skillet.setup.maps import ACTUATOR_NAME_TO_ID

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Do a squat.
    Start by resetting everything into a standing position
    Then do the squat
    """
    logging.basicConfig(level=logging.INFO)
    colorlogging.configure()
    kos = pykos.KOS(ip="192.168.42.1")

    failed_joints = []

    locs = [-90, 90, -90, 90, -90, -90, 90, -90, 90, -90, -90, 90, -90, 90, -90, -90, 90, -90, 90, -90]
    for loc in locs:
        # Reset all joints to a standing position
        move_joint_a_little.move_joint(kos, "left_hip_yaw", loc)
        move_joint_a_little.move_joint(kos, "right_hip_yaw", loc)
        move_joint_a_little.move_joint(kos, "left_hip_roll", loc)
        move_joint_a_little.move_joint(kos, "right_hip_roll", loc)
        move_joint_a_little.move_joint(kos, "left_hip_pitch", loc)
        move_joint_a_little.move_joint(kos, "right_hip_pitch", loc)
        move_joint_a_little.move_joint(kos, "left_knee_pitch", loc)
        move_joint_a_little.move_joint(kos, "right_knee_pitch", loc)
        move_joint_a_little.move_joint(kos, "left_ankle_pitch", loc)
        move_joint_a_little.move_joint(kos, "right_ankle_pitch", loc)
        time.sleep(1)  # Wait a moment to ensure movement completes

    # Log summary
    if failed_joints:
        logger.error("=== Failed Joints ===")
        logger.error("Failed to move %d joints: %s", len(failed_joints), ", ".join(failed_joints))
    else:
        logger.info("All joints moved successfully")


if __name__ == "__main__":
    main()
