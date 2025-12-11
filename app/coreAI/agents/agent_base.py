from typing import List

from langgraph.prebuilt import create_react_agent

from common_utils.file_utils import load_prompt
from coreAI import llm
from coreAI.agents.utils import init_prompt


class BaseAgent:

    def __init__(self):
        self.agent = None
        self.system_prompt = None

    def init_agent(self, prompt, response_class, tools=None):
        if tools is None:
            tools = []
        agent = create_react_agent(
            llm,
            tools=tools,
            prompt=prompt,
            response_format=response_class
        )
        return agent

    def setup_agent(self, system_prompt_path, variables, tools, response_class):
        self.system_prompt = load_prompt(system_prompt_path)
        prompt = init_prompt(self.system_prompt, variables=variables)
        self.agent = self.init_agent(prompt, response_class, tools)

    def invoke(self, state):
        pass
