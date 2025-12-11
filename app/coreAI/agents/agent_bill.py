from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from common_utils.datetime_utils import get_current_date_info
from coreAI.agents.agent_base import BaseAgent
from coreAI.tools.bill_tools import update_order_tool, get_customer_bill_history_tool, submit_order_api_tool
from dconfig import config_agents, config_prompts_path
from object_models.agent_state_obj import OrderCakeInformation

class BillAgentResponse(BaseModel):
    """Response model cho Agent hoàn thiện chi tiết và chốt đơn."""
    message: str = Field(
        description="Tin nhắn gửi tới khách hàng rằng đặt hoàn tất đơn hàng, đã cập nhật đơn hàng, hoặc hủy đặt bánh...")
    next_agent: str = Field(
        description=f"""
        `next_agent` : Là biến xác định agent tiếp theo.
        Quyết định agent tiếp theo:\n
            \t- `'END'`: khi đã hoàn thành đơn và update đơn hệ thống, hoặc hủy đặt bánh, hoặc lây lịch sử danh sách bánh đã đặt.\n
            \t- `'HUMAN'`: khi nhân viên Hỏi lại các xác nhận sửa hoặc hủy đơn không""",
        examples=['HUMAN', 'END']
    )
    order_cakes_information: list[OrderCakeInformation] = Field(
        default_factory=list[OrderCakeInformation],
        description="**BẮT BUỘC TRẢ VỀ.** Đối tượng chứa TOÀN BỘ thông tin đơn hàng đã thu thập được **tính đến thời điểm hiện tại**, bao gồm cả thông tin khách hàng vừa cung cấp."
    )


class BillAgent(BaseAgent):
    def invoke(self, state):
        current_time, day_of_week = get_current_date_info()
        config: RunnableConfig = {"configurable": {"thread_id": state["thread_id"]}}
        order_cakes_information = state.get("order_cakes_information", [])
        final_price = 0
        for order_cake in order_cakes_information:
            price_summary = order_cake.get("price_summary", 0)
            if price_summary == 0 or price_summary is None or price_summary == 'None':
                if order_cake.get("cake_price", 0):
                    price_summary = int(order_cake.get("cake_price", 0))
                if order_cake.get("delivery_fee") is not None:
                    price_summary += int(order_cake.get("delivery_fee", 0))
            final_price += price_summary

        input = {
            "messages": state["messages"],
            "current_time": current_time,
            "day_of_week": day_of_week,
            "order_cakes_information": order_cakes_information,
            "customer_id": state["customer"],
            "final_price": final_price
        }

        self.setup_agent(
            system_prompt_path=config_prompts_path.BILL_PROMPT_TEMPLATE,
            tools=[update_order_tool, get_customer_bill_history_tool, submit_order_api_tool],
            variables=input,
            response_class=BillAgentResponse
        )
        response = self.agent.invoke(input=input, config=config)

        next_agent = response["structured_response"].next_agent.upper()
        ai_message = response["structured_response"].message
        order_cakes_information = response["structured_response"].order_cakes_information
        state["order_cakes_information"] = order_cakes_information
        state["next_agent"] = next_agent
        state["current_agent"] = config_agents.AGENT_BILL
        if next_agent == config_agents.AGENT_ORDER_INFO:
            state["current_agent"] = config_agents.AGENT_ORDER_INFO
            state["next_agent"] = config_agents.AGENT_HUMAN

        state["messages"].append(AIMessage(content=ai_message))
        state["ai_message"] = ai_message
        return state


def bill_node(state):
    state = BillAgent().invoke(state)
    return state
