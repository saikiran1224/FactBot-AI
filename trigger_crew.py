from crewai import Crew, LLM, Agent, Task
from crewai_tools import SerperDevTool

from dotenv import load_dotenv
load_dotenv()

import json
import os

def trigger_crew():
    
    # Define the agent 
    orchestration_agent = Agent(
        role = "Orchestration Specialist",
        goal = "Trigger the agent to perform a task when neccessary at the correct time.",
        backstory='''You are a highly skilled orchestration specialist. You are responsible 
        for coordinating the efforts of various agents to ensure that tasks are completed efficiently 
        and effectively. You have a deep understanding of the capabilities and strengths of each agent, 
        and you use this knowledge to assign tasks and manage workflows. Your goal is to ensure that all agents are working together seamlessly to achieve the desired outcomes.'''
    )

    # Define the task
    orchestration_specialist_task = Task(
        description="Trigger the agent to perform a task when neccessary at the correct time.",
        tools=[SerperDevTool()],   
        expected_output="The agent should be triggered to perform the task at the correct time.",
    )