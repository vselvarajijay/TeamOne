"""Script to continuously read and maintain actuator positions.

This is useful when manually positioning the robot.
"""

import logging
import time
import pykos
import colorlogging
from skillet.setup.maps import ACTUATOR_NAME_TO_ID
from skillet.examples.move_joint_a_little import move_joint

logger = logging.getLogger(__name__)

def main() -> None:
    """Continuously read and maintain actuator positions."""
    logging.basicConfig(level=logging.INFO)
    colorlogging.configure()
    
    kos = pykos.KOS(ip="192.168.42.1")
    
    try:
        while True:
            for joint_name, actuator_id in ACTUATOR_NAME_TO_ID.items():
                # Get current position
                state = kos.actuator.get_actuators_state([actuator_id])
                if state and state.states:
                    current_pos = state.states[0].position
                    # Command the current position
                    move_joint(kos, joint_name, current_pos)
            
            time.sleep(0.1)  # Small delay between updates
            
    except KeyboardInterrupt:
        logger.info("Stopping position maintenance")

if __name__ == "__main__":
    main()
