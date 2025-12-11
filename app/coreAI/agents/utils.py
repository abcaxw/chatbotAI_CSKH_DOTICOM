from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate


def init_prompt(system_prompt, variables=None) -> ChatPromptTemplate:
    if variables is None:
        variables = {}
    messages = [
        {"role": "system", "content": system_prompt},
        MessagesPlaceholder(variable_name="messages")
    ]
    prompt = ChatPromptTemplate(
        messages=messages,
        partial_variables=variables,
    )
    return prompt
