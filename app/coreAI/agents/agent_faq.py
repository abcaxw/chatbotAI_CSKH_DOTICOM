from pydantic import BaseModel, Field
from pyvi.ViTokenizer import tokenize

from coreAI import embedding_service
from database.dao.milvus.faq_dao import FaqDAO
from dconfig import config_object, config_agents
import dlog


class FAQOutput(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Find similar questions, 'yes' or 'no'"
    )


def faq(state):
    dlog.dlog_i("---FAQ---")

    question = state["human_message"]
    faq_dao = FaqDAO()
    vector = embedding_service.create_embedding(question)
    faq_documents = faq_dao.search_by_vector(vector, limit=1)
    faq_data = faq_documents[0][0]
    score = faq_data["distance"]

    entity = faq_data["entity"]
    answer = entity["answer"]

    if score >= config_object.FAQ_THRESHOLD:
        state["ai_message"] = answer
        state["agent_status"] = "yes"

    else:
        state["agent_status"] = "no"

    return state


def decide_to_retrieve(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    agent_status = state["agent_status"]

    if agent_status == "yes":
        dlog.dlog_i("---DECISION: FAQ find correct answer for question---")

        return "end"
    else:
        # We have relevant documents, so generate answer
        dlog.dlog_i("---DECISION: RETRIEVE---")

        return config_agents.AGENT_RETRIEVER
