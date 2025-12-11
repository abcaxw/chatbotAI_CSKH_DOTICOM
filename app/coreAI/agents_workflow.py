import time

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from coreAI.agents import retrieve, faq, grade_documents, \
    answer_not_enough_info, generate, cake_consulting_node, \
    order_info_node, complaint_node, bill_node, \
    hello_node, human_node, other
from coreAI.agents.agent_faq import decide_to_retrieve
from coreAI.agents.agent_grader import decide_to_generate
from coreAI.agents.agent_supervisor import choose_worker, supervisor
from dconfig import config_agents

import dlog
from object_models.agent_state_obj import AgentState

INTERRUPT_BEFORE_AGENTS = [config_agents.AGENT_HUMAN]


class TeamAgents:
    def __init__(self):
        self.chain = self.build_graph()

    @staticmethod
    def build_graph():
        workflow = StateGraph(AgentState)
        # Định nghĩa các Agent/node trong workflow
        workflow.add_node(config_agents.AGENT_SUPERVISOR, supervisor)
        workflow.add_node(config_agents.AGENT_RETRIEVER, retrieve)
        workflow.add_node(config_agents.AGENT_FAQ, faq)
        workflow.add_node(config_agents.AGENT_GRADER, grade_documents)
        workflow.add_node(config_agents.AGENT_NOT_ENOUGH_INFO, answer_not_enough_info)
        workflow.add_node(config_agents.AGENT_OTHER, other)
        workflow.add_node(config_agents.AGENT_GENERATOR, generate)
        workflow.add_node(config_agents.AGENT_HELLO, hello_node)
        workflow.add_node(config_agents.AGENT_CAKE_CONSULTING, cake_consulting_node)
        workflow.add_node(config_agents.AGENT_ORDER_INFO, order_info_node)
        # workflow.add_node(config_agents.AGENT_ORDER_DETAILS, order_details_node)
        workflow.add_node(config_agents.AGENT_HUMAN, human_node)
        workflow.add_node(config_agents.AGENT_COMPLAINT, complaint_node)
        workflow.add_node(config_agents.AGENT_BILL, bill_node)
        # Định nghĩa các edge trong workflow
        workflow.set_entry_point(
            config_agents.AGENT_SUPERVISOR
        )

        workflow.add_conditional_edges(config_agents.AGENT_SUPERVISOR, choose_worker,
                                       {config_agents.AGENT_FAQ: config_agents.AGENT_FAQ,
                                        config_agents.AGENT_HELLO: config_agents.AGENT_HELLO,
                                        config_agents.AGENT_CAKE_CONSULTING: config_agents.AGENT_CAKE_CONSULTING,
                                        config_agents.AGENT_OTHER: config_agents.AGENT_OTHER,
                                        config_agents.AGENT_COMPLAINT: config_agents.AGENT_COMPLAINT,
                                        config_agents.AGENT_BILL: config_agents.AGENT_BILL
                                        })
        workflow.add_conditional_edges(config_agents.AGENT_FAQ, decide_to_retrieve,
                                       {config_agents.AGENT_RETRIEVER: config_agents.AGENT_RETRIEVER,
                                        "end": END})
        workflow.add_conditional_edges(config_agents.AGENT_GRADER, decide_to_generate, {
            config_agents.AGENT_GENERATOR: config_agents.AGENT_GENERATOR,
            config_agents.AGENT_NOT_ENOUGH_INFO: config_agents.AGENT_NOT_ENOUGH_INFO})

        workflow.add_conditional_edges(config_agents.AGENT_HUMAN, choose_worker, {
            config_agents.AGENT_CAKE_CONSULTING: config_agents.AGENT_CAKE_CONSULTING,
            config_agents.AGENT_ORDER_INFO: config_agents.AGENT_ORDER_INFO,
            config_agents.AGENT_BILL: config_agents.AGENT_BILL
            # config_agents.AGENT_ORDER_DETAILS: config_agents.AGENT_ORDER_DETAILS
        })

        workflow.add_conditional_edges(config_agents.AGENT_CAKE_CONSULTING, choose_worker, {
            config_agents.AGENT_HUMAN: config_agents.AGENT_HUMAN,
            "END": END,
            config_agents.AGENT_ORDER_INFO: config_agents.AGENT_ORDER_INFO
        })
        workflow.add_conditional_edges(
            config_agents.AGENT_ORDER_INFO,
            choose_worker,
            {
                config_agents.AGENT_CAKE_CONSULTING: config_agents.AGENT_CAKE_CONSULTING,
                config_agents.AGENT_BILL: config_agents.AGENT_BILL,
                config_agents.AGENT_HUMAN: config_agents.AGENT_HUMAN,
                "END": END,
            }
        )
        workflow.add_conditional_edges(
            config_agents.AGENT_BILL,
            choose_worker,
            {
                config_agents.AGENT_HUMAN: config_agents.AGENT_HUMAN,
                "END": END
            }
        )
        workflow.add_edge(config_agents.AGENT_RETRIEVER, config_agents.AGENT_GRADER)

        workflow.add_edge(config_agents.AGENT_NOT_ENOUGH_INFO, END)
        workflow.add_edge(config_agents.AGENT_OTHER, END)
        workflow.add_edge(config_agents.AGENT_COMPLAINT, END)
        workflow.add_edge(config_agents.AGENT_HELLO, END)
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory,
                                interrupt_before=INTERRUPT_BEFORE_AGENTS)

    def process(self, message, history, thread_id, customer):
        dlog.dlog_i(f"Process message: {message}")
        time_start = time.time()
        input = {"human_message": message, "thread_id": thread_id, "messages": history, "customer": customer}
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        current_state = self.chain.get_state(config)
        if len(current_state.next) > 0 and current_state.next[0] in INTERRUPT_BEFORE_AGENTS:
            self.chain.update_state(config=config, values=input, as_node=current_state.values["current_agent"])
            input = None
        response = self.chain.invoke(input=input, config=config, stream_mode="values")
        dlog.dlog_i(f"Process duration: {time.time() - time_start}")
        return response
