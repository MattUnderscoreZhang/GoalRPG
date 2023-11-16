from dataclasses import dataclass
from dotenv import load_dotenv
import json
import os
import sys
from typing import cast

from gpt_interface import GptInterface


@dataclass
class Task:
    task: str
    deadline: str
    estimated_time: str
    finished: bool
    actual_time: str
    subtasks: list['Task']


def get_tasks(filename: str) -> list[Task]:
    with open(filename, "r") as f:
        tasks = json.load(f)
    return tasks


def get_interface() -> GptInterface:
    load_dotenv()
    interface = GptInterface(cast(str, os.getenv("OPENAI_KEY")), "gpt-4")
    interface.set_system_message(
        """
        You will help me prioritize and track my tasks.
        I will ask questions and talk to you, or give you progress on my first unfinished task.
        You will answer my questions, and/or reorganize my tasks by the order in which they should be done.

        A Task has the following form:
        @dataclass
        class Task:
            task: str
            deadline: str
            estimated_time: str
            finished: bool
            actual_time: str
            subtasks: list['Task']

        Respond in the following JSON format:
        {
            "last_feedback_or_response": [your feedback or response to questions],
            "tasks": [list[Task]]
        }

        An example task looks like this:
        {
            "task": "write my thesis",
            "deadline": "end of September",
            "estimated_time": "30d",
            "finished": false,
            "actual_time": "",
            "subtasks": [
                {
                    "task": "gather research results",
                    "deadline": "",
                    "estimated_time": "3h",
                    "finished": true,
                    "actual_time": "5h 36m",
                    "subtasks": []
                },
                ...
            ]
        }

        Your feedback should be short, constructive, and encouraging.
        Your responses should be helpful, and answer my questions in a succinct manner.
        Feel free to update and reprioritize my tasks list as needed.
        """
    )
    return interface


def get_next_task(tasks: list[Task]) -> Task | None:
    task_list = [
        task
        for task in tasks
        if task.finished is False
    ]
    if len(task_list) == 0:
        return None

    next_task = task_list[0]
    if not next_task.subtasks:
        return next_task

    next_subtask = get_next_task(next_task.subtasks)
    if next_subtask is not None:
        return next_subtask

    next_task.finished = True
    return get_next_task(tasks)


@dataclass
class GptResponse:
    last_feedback_or_response: str
    tasks: list[Task]


def prioritize_tasks(tasks: list[Task], interface: GptInterface) -> None:
    print("Hi there. Let's prioritize your tasks.")
    response = GptResponse(
        **json.loads(
            interface.say(str(
                GptResponse(
                    last_feedback_or_response="",
                    tasks=tasks,
                )
            ))
        )
    )
    while next_task := get_next_task(response.tasks):
        print()
        print(response.last_feedback_or_response)
        print(f"Your next task is: {next_task}")
        response = GptResponse(
            **json.loads(
                interface.say(
                    input("Update your progress on this task: ")
                )
            )
        )
    print()
    print(response.last_feedback_or_response)


if __name__ == "__main__":
    filename = sys.argv[1]
    tasks = get_tasks(filename)
    interface = get_interface()
    prioritize_tasks(tasks, interface)
