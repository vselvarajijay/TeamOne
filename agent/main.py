from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing import Literal
from langgraph.prebuilt import create_react_agent

# Initialize the model
model = ChatOpenAI(model="gpt-4", temperature=0)

# Define robot action tools
@tool
def squat():
    """Makes the robot squat down to prepare for picking up an item."""
    return "Robot has squatted down"

@tool
def walk_forward():
    """Makes the robot walk forward 3 steps."""
    return "Robot walked forward 3 steps"

@tool
def stand_up():
    """Makes the robot stand up from squatting position."""
    return "Robot has stood up"

@tool
def grip_item():
    """Makes the robot grip an item in front of it."""
    return "Robot has gripped the item"

@tool
def ungrip_item():
    """Makes the robot release its grip on the currently held item."""
    return "Robot has released the item"

# Collect all tools
tools = [squat, walk_forward, stand_up, grip_item, ungrip_item]

# Create the agent graph
graph = create_react_agent(model, tools=tools)

# Helper function to print the stream of actions
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# Example usage
def execute_pickup_and_deliver():
    # Task: Pick up an item and deliver it
    inputs = {
        "messages": [
            ("user", "Pick up the item in front of you and deliver it 3 steps forward")
        ]
    }
    print_stream(graph.stream(inputs, stream_mode="values"))

if __name__ == "__main__":
    execute_pickup_and_deliver()
    
# The agent will typically execute these steps in sequence:
# 1. Squat down to reach the item
# 2. Grip the item
# 3. Stand up while holding the item
# 4. Walk forward 3 steps
# 5. Squat down for safe placement
# 6. Ungrip to release the item
# 7. Stand up to complete the task