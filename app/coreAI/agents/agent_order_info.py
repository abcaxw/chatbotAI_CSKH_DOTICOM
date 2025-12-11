from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from common_utils.datetime_utils import get_current_date_info
from coreAI.agents.agent_base import BaseAgent
from coreAI.tools.cake_order_tools import get_store_locations_tool, calculate_delivery_fee_ors_tool, \
    calculate_final_price_tool, check_cake_availability_tool, get_cake_availability_tool, check_cake_order_info

import dlog
from dconfig import config_prompts, config_agents, config_prompts_path

from object_models.agent_state_obj import OrderCakeInformation

cake_info_fields = ["cake_id", "cake_size", "cake_price", "customer_name", "customer_phone", "receive_time",
                    "delivery_method", "address", "delivery_fee"]


class OrderInfoAgentResponse(BaseModel):
    ai_message: str = Field(
        description="Nội dung trả lời của agent. Thường là câu hỏi để thu thập thông tin cho bước checklist tiếp theo, hoặc là bản tóm tắt cuối cùng. Nhưng câu nói phải lịch sự, lễ phép với khách hàng."
    )
    next_agent: str = Field(
        description=f"""**QUAN TRỌNG:** Xác định agent tiếp theo dựa trên **bước checklist vừa hoàn thành** và **phản hồi của khách hàng**:\n
        \t- `'{config_agents.AGENT_CAKE_CONSULTING}'`: **CHỈ** đặt giá trị này ở Bước 0 nếu thông tin bánh ban đầu không đủ rõ ràng. Hoặc khách hàng muốn tư vấn bánh khác,\n
        \t- `'{config_agents.AGENT_BILL}'`: Sau khi AI đã hỏi hết các thông tin cần để đặt bánh và khách hàng xác nhận.\n
        \t- `'END'`: **KẾT THÚC** khi mà khách hàng không muốn đặt bánh nữa
        \t- `'HUMAN'`: **MẶC ĐỊNH CHO TẤT CẢ CÁC TRƯỜNG HỢP CÒN LẠI.** Đặt giá trị này sau khi bạn đặt bất kỳ câu hỏi nào trong các bước từ 0 đến 4 (trừ khi quyết định là 'end' hoặc 'consulting_cake'), hoặc khi yêu cầu khách hàng làm rõ/sửa đổi thông tin. Đây là trạng thái chờ khách hàng cung cấp input để tiếp tục checklist.""",
        examples=['HUMAN', config_agents.AGENT_BILL, config_agents.AGENT_CAKE_CONSULTING, 'END']
    )
    order_cakes_information: list[OrderCakeInformation] = Field(
        default_factory=list[OrderCakeInformation],
        description="**BẮT BUỘC TRẢ VỀ.** Đối tượng chứa TOÀN BỘ thông tin đơn hàng đã thu thập được **tính đến thời điểm hiện tại**, bao gồm cả thông tin khách hàng vừa cung cấp. Agent ở lượt sau sẽ đọc thông tin này để xác định bước checklist tiếp theo."
    )


class OrderInfoAgent(BaseAgent):

    def invoke(self, state):
        tools = [get_store_locations_tool, calculate_delivery_fee_ors_tool, calculate_final_price_tool,
                 check_cake_order_info, check_cake_availability_tool]
        current_time, day_of_week = get_current_date_info()
        config: RunnableConfig = {"configurable": {"thread_id": state["thread_id"]}}
        input = {
            "messages": state["messages"],
            "current_time": current_time,
            "day_of_week": day_of_week,
            "order_cakes_information": [OrderCakeInformation(**order_cake).model_dump(exclude_none=True) for
                                        order_cake in state.get("order_cakes_information", [])]
        }

        self.setup_agent(
            system_prompt_path=config_prompts_path.ORDER_INFO_PROMPT_TEMPLATE,
            tools=tools,
            variables=input,
            response_class=OrderInfoAgentResponse
        )
        response = self.agent.invoke(input=input, config=config)

        ai_message = response["structured_response"].ai_message
        state["messages"].append(AIMessage(content=ai_message))

        # Cập nhật trạng thái
        state["current_agent"] = config_agents.AGENT_ORDER_INFO
        next_agent = response["structured_response"].next_agent.upper()
        if next_agent == config_agents.AGENT_CAKE_CONSULTING:
            next_agent = config_agents.AGENT_HUMAN
            state["current_agent"] = config_agents.AGENT_CAKE_CONSULTING
        state["next_agent"] = next_agent
        order_cakes_information = response["structured_response"].order_cakes_information
        state["order_cakes_information"] = [order.model_dump(exclude_none=True) for order in order_cakes_information]

        state["ai_message"] = ai_message
        dlog.dlog_i(f"Next agent: {state['next_agent']}")
        return state


def order_info_node(state):
    order_info_agent = OrderInfoAgent()
    state = order_info_agent.invoke(state)
    return state
