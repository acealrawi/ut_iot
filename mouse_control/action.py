from enum import Enum

class Action(Enum):
    STILL = 0
    BACK = 1
    FRONT = 2
    LEFT = 3
    RIGHT = 4

action_map = {
    "still1": Action.STILL,
    "back1": Action.BACK,
    "front1": Action.FRONT,
    "left1": Action.LEFT,
    "right1": Action.RIGHT
}

string_map = {
    Action.STILL: "still1",
    Action.BACK: "back1",
    Action.FRONT: "front1",
    Action.LEFT: "left1",
    Action.RIGHT: "right1"
}

def map_action(action: str) -> Action | None:
    if action in action_map:
        return action_map[action]
    return None
