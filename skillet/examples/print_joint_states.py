"""Script to print the current states of all joints in the robot."""

# Standard library imports
import logging
import time
import json  # Add this import at the top of the file

# Third-party imports
import colorlogging
import pykos  # type: ignore[import-untyped]

import move_joint_a_little

# Local imports
from skillet.setup.maps import ACTUATOR_NAME_TO_ID

logger = logging.getLogger(__name__)

def configure_joint_for_tracking(kos: pykos.KOS, joint_name: str) -> None:
    """Configure a joint for position tracking with minimal resistance."""
    actuator_id = ACTUATOR_NAME_TO_ID[joint_name]
    
    result = kos.actuator.configure_actuator(
        actuator_id=actuator_id,
        kp=1.0,  # Very low proportional gain
        kd=0.1,  # Very low derivative gain
        ki=0.0,  # No integral gain
        max_torque=5.0,  # Low torque to allow manual movement
        torque_enabled=True  # Important: enable torque for position tracking
    )
    
    if not result.success:
        logger.warning("Failed to configure joint %s: %s", joint_name, result.error)

def print_all_joint_states() -> None:
    """Get and print the states of all joints in JSON format."""

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    colorlogging.configure()

    # Instantiate the KOS client
    kos = pykos.KOS(ip="192.168.42.1")

    # Initialize dictionary to store joint states
    joint_states = {}

    # First configure all joints for tracking
    logger.info("Configuring joints for position tracking...")
    for joint_name in ACTUATOR_NAME_TO_ID:
        try:
            configure_joint_for_tracking(kos, joint_name)
        except Exception as e:
            logger.error("Failed to configure joint %s: %s", joint_name, str(e))

    # Small delay to allow configurations to take effect
    time.sleep(0.5)

    # Print the JSON output
    logger.info("Joint States:")
    print(json.dumps(joint_states, indent=2))

def main() -> None:
    """Main function to print all joint states."""
    print_all_joint_states()

if __name__ == "__main__":
    main()
