"""Example script to move all joints a little bit.

Make sure you have configured and zeroed the joints before running this script.
"""

# Standard library imports
import logging
import time
import traceback

# Third-party imports
import colorlogging

# Local imports
from skillet.examples.move_joint_a_little import move_joint_a_little
from skillet.setup.maps import ACTUATOR_NAME_TO_ID

# Constants
MOVE_DEGREES = 5.0  # A small, safe amount to move each joint

logger = logging.getLogger(__name__)


def main() -> None:
    """Move all joints a little bit, with error handling for each joint."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    colorlogging.configure()

    failed_joints = []

    for joint_name in ACTUATOR_NAME_TO_ID:
        try:
            logger.info("Attempting to move joint: %s", joint_name)
            move_joint_a_little(joint_name, MOVE_DEGREES)
            logger.info("Successfully moved joint: %s", joint_name)
            time.sleep(0.5)
        except Exception as e:
            logger.error("Failed to move joint %s: %s", joint_name, str(e))
            logger.error("Traceback:\n%s", traceback.format_exc())
            failed_joints.append(joint_name)
            logger.info("Continuing with next joint...")

    # Log summary
    if failed_joints:
        logger.error("\n=== Failed Joints ===")
        logger.error("Failed to move %d joints: %s", len(failed_joints), ", ".join(failed_joints))


if __name__ == "__main__":
    main()
