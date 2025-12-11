from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

import dlog
from common_utils.datetime_utils import get_current_date_info
from coreAI.agents.agent_base import BaseAgent
from coreAI.tools.cake_consulting_tools import retriever_cake_information_tool, get_cake_information_tool, \
    suggest_cake_type, get_available_cake_info, check_order_cake_by_image, get_best_seller_cakes

from dconfig import config_agents, config_object, config_prompts_path
import re

from object_models.agent_state_obj import OrderCakeInformation


class CakeConsultingAgentResponse(BaseModel):
    ai_message: str = Field(
        description="Nội dung trả lời của agent, câu hỏi làm rõ. Nêu là tư vấn bánh kem thì chỉ cần **gửi danh sách link**, **không cần phải ghi bánh số**"
    )
    next_agent: str = Field(
        description=f"""**QUAN TRỌNG:** Quyết định agent tiếp theo DỰA TRÊN KẾT QUẢ KIỂM TRA ƯU TIÊN:\n
        \t- `'{config_agents.AGENT_ORDER_INFO}'`: **Hành động của Bước 1** (Khách xác nhận đặt bánh cụ thể, xác định được mã bánh).\n
        \t- `'END'`: **Hành động của Bước 2B** (Khách muốn kết thúc).\n
        \t- `'HUMAN'`: **CHO TẤT CẢ CÁC TRƯỜNG HỢP CÒN LẠI** (khi thực hiện hành động của Bước 2A, 2C - tức là sau khi hiển thị bánh, trả lời giá/size, hoặc hỏi làm rõ).""",
        examples=[config_agents.AGENT_ORDER_INFO, 'HUMAN', 'END']
    )
    order_cakes_information: list[OrderCakeInformation] = Field(
        default_factory=list[OrderCakeInformation],
        description="**BẮT BUỘC TRẢ VỀ.** Đối tượng chứa TOÀN BỘ thông tin đơn hàng đã thu thập được **tính đến thời điểm hiện tại**, bao gồm cả thông tin khách hàng vừa cung cấp. Agent ở lượt sau sẽ đọc thông tin này để xác định bước checklist tiếp theo."
    )

    # Hàm to_dict để dễ cập nhật state nếu cần
    def to_dict(self):
        return self.model_dump(exclude_none=True)


class CakeConsultingAgent(BaseAgent):
    def invoke(self, state):
        current_time, day_of_week = get_current_date_info()

        config: RunnableConfig = {"configurable": {"thread_id": state["thread_id"]}}
        human_message = state["messages"][-1].content
        input = {
            "messages": state["messages"],
            "current_time": str(current_time),
            "day_of_week": str(day_of_week),
            "presented_cake_names": state.get("presented_cake_names", []),
            "RECOMMEND_NUMB": config_object.TOP_K_RECOMMENDATION_CAKE,
            "image_link": human_message if human_message.startswith("https://") else "N/A",
            "order_cakes_information": [OrderCakeInformation(**order_cake).model_dump(exclude_none=True) for
                                        order_cake in state.get("order_cakes_information", [])]
        }

        self.setup_agent(
            system_prompt_path=config_prompts_path.CAKE_CONSULTING_PROMPT_TEMPLATE,
            tools=[retriever_cake_information_tool, get_cake_information_tool, get_best_seller_cakes,
                   suggest_cake_type, get_available_cake_info, check_order_cake_by_image],
            variables=input,
            response_class=CakeConsultingAgentResponse
        )
        response = self.agent.invoke(input=input, config=config)

        # Add AI message to messages history
        ai_message = response["structured_response"].ai_message.replace("(", "").replace(")", "")
        state["messages"].append(AIMessage(content=ai_message, type="ai"))

        state["current_agent"] = config_agents.AGENT_CAKE_CONSULTING
        state["next_agent"] = response["structured_response"].next_agent.upper()
        order_cakes_information = response["structured_response"].order_cakes_information
        state["order_cakes_information"] = [order.model_dump(exclude_none=True) for order in order_cakes_information]
        # Trích xuất mã bánh VỪA ĐƯỢC HIỂN THỊ từ message trả về
        state["presented_cake_names"] = extract_cake_code(ai_message, state.get("presented_cake_names"))

        if state["next_agent"] != config_agents.AGENT_ORDER_INFO:
            state["ai_message"] = ai_message
        return state


def cake_consulting_node(state):
    state = CakeConsultingAgent().invoke(state)
    return state


def extract_cake_code(ai_message, presented_cake_names_old=None):
    if not presented_cake_names_old:
        presented_cake_names_old = []
    current_presented_set = set(presented_cake_names_old)
    # Sử dụng regex để tìm tất cả các link ảnh trong nội dung
    presented_in_this_turn = re.findall(r'/ImgBig/([A-Za-z0-9.-]+)\.jpg', ai_message)
    dlog.dlog_i(f"Bánh được hiển thị lượt này: {presented_in_this_turn}")

    # Cập nhật danh sách các bánh đã hiển thị (dùng set để tránh trùng lặp)
    if presented_in_this_turn:
        current_presented_set.update(presented_in_this_turn)
    return list(current_presented_set)
