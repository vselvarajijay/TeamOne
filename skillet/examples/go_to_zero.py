"""Script to move all actuators to zero position and enable torque.

Make sure the robot is in a safe position before running this script.
"""

# Standard library imports
import logging
import time
import traceback

# Third-party imports
import colorlogging
import pykos  # type: ignore[import-untyped]

# Local imports
from skillet.setup.maps import ACTUATOR_NAME_TO_ID

logger = logging.getLogger(__name__)

def configure_actuator(kos: pykos.KOS, actuator_id: int) -> bool:
    """Configure a single actuator with standard parameters."""
    try:
        result = kos.actuator.configure_actuator(
            actuator_id=actuator_id,
            kp=32.0,  # Proportional gain
            kd=32.0,  # Derivative gain
            ki=32.0,  # Integral gain
            max_torque=100.0,  # Maximum torque limit
            torque_enabled=True,
        )
        return result.success
    except Exception as e:
        logger.error(f"Failed to configure actuator {actuator_id}: {str(e)}")
        return False

def move_to_zero(kos: pykos.KOS) -> list[str]:
    """Move all joints to zero position and return list of failed joints."""
    failed_joints = []
    
    for joint_name, actuator_id in ACTUATOR_NAME_TO_ID.items():
        try:
            # Configure actuator first
            if not configure_actuator(kos, actuator_id):
                failed_joints.append(joint_name)
                continue
                
            # Command zero position
            command = {"actuator_id": actuator_id, "position": 0.0}
            result = kos.actuator.command_actuators([command])
            
            if not result.results[0].success:
                failed_joints.append(joint_name)
                logger.error(f"Failed to zero joint {joint_name}")
            else:
                logger.info(f"Successfully zeroed joint {joint_name}")
                
        except Exception as e:
            logger.error(f"Error zeroing joint {joint_name}: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            failed_joints.append(joint_name)
            
    return failed_joints

def main() -> None:
    """Move all actuators to zero position."""
    logging.basicConfig(level=logging.INFO)
    colorlogging.configure()
    
    try:
        kos = pykos.KOS(ip="192.168.42.1")
        
        logger.info("Starting to zero all joints...")
        failed_joints = move_to_zero(kos)
        
        if failed_joints:
            logger.error("=== Failed Joints ===")
            logger.error("Failed to zero %d joints: %s", 
                        len(failed_joints), ", ".join(failed_joints))
        else:
            logger.info("All joints successfully zeroed")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
