from dataclasses import dataclass
from dotenv import load_dotenv
import json
import os
import sys
from typing import cast

from gpt_interface import GptInterface


@dataclass
class Tasks:
    context: str
    tasks: list[str]


def get_tasks(filename: str) -> Tasks:
    with open(filename, "r") as f:
        tasks = [task.strip() for task in f.readlines()]
        context = tasks.pop(0)
    return Tasks(context, tasks)


def get_interface() -> GptInterface:
    load_dotenv()
    interface = GptInterface(cast(str, os.getenv("OPENAI_KEY")), "gpt-4")
    interface.set_system_message(
        """
        You will help me prioritize my tasks.
        I will give you progress on my tasks, or ask questions and talk to you.
        You will prioritize the tasks by the order in which they should be done.
        Respond in the following JSON format:
        {
            "feedback_or_response": [your feedback or response to questions],
            "prioritized_task_list": [the prioritized list],
            "completed_tasks": [completed list]
        }
        Your feedback should be short, constructive, and encouraging.
        Your responses should be helpful, and answer my questions in a succinct manner.
        Feel free to update and reprioritize my tasks list as needed.
        """
    )
    return interface


def prioritize_tasks(tasks: Tasks, interface: GptInterface) -> None:
    print("Hi there. Let's prioritize your tasks.")
    response = json.loads(
        interface.say(
            f"""
            My overall goal is: {tasks.context}
            My task list is: {tasks.tasks}
            """
        )
    )
    task_list = response["prioritized_task_list"]
    while len(task_list) > 0:
        print()
        print(response["feedback_or_response"])
        print(f"Your next task is: {task_list[0]}")
        response = json.loads(
            interface.say(
                input("Update your progress on this task: ")
            )
        )
        task_list = response["prioritized_task_list"]


if __name__ == "__main__":
    filename = sys.argv[1]
    tasks = get_tasks(filename)
    interface = get_interface()
    prioritize_tasks(tasks, interface)
