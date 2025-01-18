from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing import Literal, List, Optional
from langgraph.prebuilt import create_react_agent
import logging
import time
import traceback
import pykos
import colorlogging
import move_joint_a_little
from skillet.setup.maps import ACTUATOR_NAME_TO_ID

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
colorlogging.configure()

@dataclass
class RobotController:
    """Class to manage robot state and control"""
    kos: pykos.KOS
    failed_joints: List[str]
    
    @classmethod
    def initialize(cls, ip: str = "192.168.42.1") -> 'RobotController':
        """Initialize robot connection and controller"""
        kos = pykos.KOS(ip=ip)
        return cls(kos=kos, failed_joints=[])
    
    def execute_squat(self) -> None:
        """Execute the squat movement sequence"""
        joint_names = [
            "left_hip_yaw", 
            "right_hip_yaw",
            "left_hip_roll", 
            "right_hip_roll",
            "left_hip_pitch", 
            "right_hip_pitch",
            "left_knee_pitch", 
            "right_knee_pitch",
            "left_ankle_pitch", 
            "right_ankle_pitch"
        ]
        
        locs = [-90, 90, -90, 90, -90, -90, 90, -90, 90, -90, -90, 90, -90, 90, -90, -90, 90, -90, 90, -90]
        
        for loc in locs:
            try:
                for joint in joint_names:
                    move_joint_a_little.move_joint(self.kos, joint, loc)
            except Exception as e:
                logger.error(f"Failed to move joint {joint}: {str(e)}")
                self.failed_joints.append(joint)
                traceback.print_exc()
            time.sleep(1)  # Wait for movement to complete

# Initialize robot controller
robot = RobotController.initialize()

# Define robot action tools
@tool
def squat() -> str:
    """Makes the robot squat down to prepare for picking up an item."""
    try:
        robot.execute_squat()
        return "Robot has squatted down"
    except Exception as e:
        logger.error(f"Squat failed: {str(e)}")
        traceback.print_exc()
        return f"Failed to squat: {str(e)}"

@tool
def walk_forward() -> str:
    """Makes the robot walk forward 3 steps (mock implementation)."""
    logger.info("Mock: Robot walking forward 3 steps")
    return "Robot walked forward 3 steps"

@tool
def stand_up() -> str:
    """Makes the robot stand up from squatting position (mock implementation)."""
    logger.info("Mock: Robot standing up")
    return "Robot has stood up"

@tool
def grip_item() -> str:
    """Makes the robot grip an item in front of it (mock implementation)."""
    logger.info("Mock: Robot gripping item")
    return "Robot has gripped the item"

@tool
def ungrip_item() -> str:
    """Makes the robot release its grip on the currently held item (mock implementation)."""
    logger.info("Mock: Robot releasing item")
    return "Robot has released the item"

# Collect all tools
tools = [squat, walk_forward, stand_up, grip_item, ungrip_item]

# Create the agent graph
model = ChatOpenAI(model="gpt-4", temperature=0)
graph = create_react_agent(model, tools=tools)

def print_stream(stream):
    """Helper function to print the stream of actions"""
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

def execute_pickup_and_deliver():
    """Execute the pickup and delivery task"""
    inputs = {
        "messages": [
            ("user", "Pick up the item in front of you and deliver it 3 steps forward")
        ]
    }
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    # Log summary of any failed joints
    if robot.failed_joints:
        logger.error("=== Failed Joints ===")
        logger.error("Failed to move %d joints: %s", 
                    len(robot.failed_joints), 
                    ", ".join(robot.failed_joints))
    else:
        logger.info("All joints moved successfully")

if __name__ == "__main__":
    execute_pickup_and_deliver()