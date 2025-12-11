import copy

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from common_utils.datetime_utils import get_current_date_info
from coreAI import llm
from coreAI.agents.utils import init_prompt
from dconfig import config_prompts, config_messages
import dlog


def router(state):
    dlog.dlog_i(f"---ROUTER---")
    state["ai_message"] = config_messages.ROUTING_HUMAN_MESSAGE_OUTPUT
    state["url"] = config_messages.ROUTING_HUMAN_URL
    return state


def chatter(state):
    prompt = ChatPromptTemplate.from_template(config_prompts.CHATTER_PROMPT)

    chain = prompt | llm
    dlog.dlog_i(f"---CHATTER---")

    message = state["human_message"]
    # chat_history = state["chat_history"]

    response = chain.invoke({"input": message})
    response = response.content

    state["ai_message"] = response
    return state


def other(state):
    dlog.dlog_i(f"---OTHER---")
    state["ai_message"] = config_messages.OUTPUT_AGENT_OTHER

    return state


def answer_not_enough_info(state):
    dlog.dlog_i(f"---ANSWER_NOT_ENOUGH_INFO---")
    state["ai_message"] = config_messages.OUTPUT_AGENT_NOT_ENOUGH_INFO
    return state


def human_node(state):
    dlog.dlog_i(f"---HUMAN---")
    # state["ai_message"] = config
    state["next_agent"] = state["current_agent"]
    return state


def hello_node(state):
    dlog.dlog_i(f"---HELLO---")
    current_time, day_of_week = get_current_date_info()
    system_prompt = copy.deepcopy(config_prompts.HELLO_PROMPT_TEMPLATE).format(current_time=current_time,
                                                                               day_of_week=day_of_week)
    prompt = init_prompt(system_prompt)

    chain = prompt | llm
    messages = state["messages"]
    config: RunnableConfig = {"configurable": {"thread_id": state["thread_id"]}}
    input = {
        "messages": messages, }
    response = chain.invoke(input=input, config=config)
    state["ai_message"] = response.content
    return state
