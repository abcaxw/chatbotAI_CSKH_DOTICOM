from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, AIMessage
from pydantic import BaseModel, Field

import dlog
from common_utils.datetime_utils import get_current_date_info
from coreAI import llm
from coreAI.tools.complaint_tools import retriever_complaint_tool

from dconfig import config_prompts


class ComplaintAgentResponse(BaseModel):
    ai_message: str = Field(description="Nội dung trả lời của ai")
    next_agent: str = Field(
        description="Agent tiếp theo trong luồng xử lý, ví dụ: 'human', 'end'. Nếu cần khách hàng khách hàng cung cấp thêm thông tin thì chọn 'human'. Nếu đã trả lời được thì chọn 'end'")


def create_complaint_agent(complaint_llm, tools):
    def state_modifier(state):
        system_content = config_prompts.COMPLAINT_PROMPT_TEMPLATE
        system_message = SystemMessage(content=system_content)
        history = state.get("messages", [])

        return [system_message] + history

    base_agent = create_react_agent(
        complaint_llm,
        tools=tools,
        state_modifier=state_modifier,
        response_format=ComplaintAgentResponse

    )

    return base_agent


def complaint_node(state):
    dlog.dlog_i("---COMPLAINT---")
    tools = [
        retriever_complaint_tool
    ]

    complaint_agent = create_complaint_agent(llm, tools)
    current_time, day_of_week = get_current_date_info()
    response = complaint_agent.invoke({"messages": state["messages"],
                                       "current_time": current_time,
                                       "day_of_week": day_of_week
                                       })


    # Store tool messages in state


    # Add AI message to messages history
    ai_message = response["structured_response"].ai_message
    state["messages"].append(AIMessage(content=ai_message))
    state["ai_message"] = ai_message
    state["next_agent"] = response["structured_response"].next_agent.upper()
    dlog.dlog_i(f"Next agent: {state['next_agent']}")
    return state
