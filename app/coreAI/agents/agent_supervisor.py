from pydantic import BaseModel, Field

from coreAI import llm
from coreAI.agents.utils import init_prompt
from dconfig import config_prompts
import dlog


class SupervisorOut(BaseModel):
    worker: str = Field(
        description="Determines which worker to do the task.",
    )


class Supervisor:
    def __init__(self, messages):
        prompt = init_prompt(config_prompts.SUPERVISOR_PROMPT, {"messages": messages})
        structured_llm_supervisor = llm.with_structured_output(SupervisorOut)
        self.chain = prompt | structured_llm_supervisor


def supervisor(state):
    dlog.dlog_i("---SUPERVISOR---")

    messages = state.get("messages", [])

    supervisor_agent = Supervisor(messages)
    data_input = {"messages": messages}
    result = supervisor_agent.chain.invoke(input=data_input)

    state["ai_message"] = result.worker
    state["next_agent"] = result.worker
    return state


def choose_worker(state):
    """
    Determines which worker to do the task.

    Args:
        state (dict): The current graph state

    Returns:
        str: worker do the task
    """

    worker = state['next_agent']
    dlog.dlog_i(f"---DECISION: {worker} DO THE TASK---")

    return worker
