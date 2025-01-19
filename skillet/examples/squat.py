"""Example script to perform a squat sequence using predefined positions.

Make sure you have configured and zeroed the joints before running this script.
"""

# Standard library imports
import json
import logging
import time
import traceback
import pykos  # type: ignore[import-untyped]

# Third-party imports
import colorlogging

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

def move_to_position(kos: pykos.KOS, position_dict: dict) -> list[str]:
    """Move all joints to specified positions and return list of failed joints."""
    failed_joints = []
    
    for joint_name, joint_data in position_dict.items():
        try:
            actuator_id = joint_data["id"]
            target_position = joint_data["position"]
            
            # Configure actuator first
            if not configure_actuator(kos, actuator_id):
                failed_joints.append(joint_name)
                continue
                
            # Command the position
            command = {"actuator_id": actuator_id, "position": target_position}
            result = kos.actuator.command_actuators([command])
            
            if not result.results[0].success:
                failed_joints.append(joint_name)
                logger.error(f"Failed to move joint {joint_name}")
            else:
                logger.info(f"Successfully moved joint {joint_name} to position {target_position}")
                
        except Exception as e:
            logger.error(f"Error moving joint {joint_name}: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            failed_joints.append(joint_name)
            
    return failed_joints

def main() -> None:
    """
    Execute the squat sequence using positions from squat_positions.json.
    ASSUMES THE ROBOT WAS CALIBRATED
    """
    logging.basicConfig(level=logging.INFO)
    colorlogging.configure()
    
    try:
        # Load squat positions
        with open("squat_positions.json", "r") as f:
            squat_sequence = json.load(f)
            
        kos = pykos.KOS(ip="192.168.42.1")
        
        # Execute each position in sequence
        for i, position in enumerate(squat_sequence):
            logger.info(f"\nMoving to position {i+1}/{len(squat_sequence)}")
            
            failed_joints = move_to_position(kos, position)
            
            if failed_joints:
                logger.error("=== Failed Joints for Position %d ===", i+1)
                logger.error("Failed to move %d joints: %s", 
                           len(failed_joints), ", ".join(failed_joints))
            else:
                logger.info("All joints moved successfully for position %d", i+1)
            
            # Wait between positions
            if i < len(squat_sequence) - 1:  # Don't wait after last position
                logger.info("Waiting 2 seconds before next position...")
                time.sleep(2)
                
    except FileNotFoundError:
        logger.error("squat_positions.json not found!")
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in squat_positions.json!")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
