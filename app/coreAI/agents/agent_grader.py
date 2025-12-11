from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from coreAI import llm
from dconfig import config_object, config_agents, config_prompts
import dlog


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


class Grader:
    def __init__(self):
        system = config_prompts.GRADER_AGENT
        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            ]
        )
        structured_llm_grader = llm.with_structured_output(GradeDocuments)
        self.chain = grade_prompt | structured_llm_grader


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """
    dlog.dlog_i("---GRADER---")
    dlog.dlog_i("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

    message = state["human_message"]
    documents = state["documents"]
    # chat_history = state["chat_history"]

    # Score each doc
    filtered_docs = []
    grader_status = "No"
    grader = Grader()
    for d in documents:
        document = d['content']
        score = grader.chain.invoke(
            {"question": message, "document": document}
        )
        grade = score.binary_score
        if grade == "yes":
            dlog.dlog_i("---GRADE: DOCUMENT RELEVANT---")
            grader_status = "Yes"
            filtered_docs.append(d)
        else:
            dlog.dlog_i("---GRADE: DOCUMENT NOT RELEVANT---")
            continue

    state["grader_status"] = grader_status
    state["documents"] = filtered_docs

    return state


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    dlog.dlog_i("---ASSESS GRADED DOCUMENTS---")

    grader_status = state["grader_status"]

    if grader_status == "No":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        dlog.dlog_i("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, ANSWER NOT ENOUGH INFORMATION---")

        return config_agents.AGENT_NOT_ENOUGH_INFO
    else:
        # We have relevant documents, so generate answer
        dlog.dlog_i("---DECISION: GENERATE---")

        return config_agents.AGENT_GENERATOR
