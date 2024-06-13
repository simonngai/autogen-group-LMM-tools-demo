import autogen
from autogen.agentchat.contrib.multimodal_conversable_agent import (
    MultimodalConversableAgent,
)
from autogen.agentchat.contrib.capabilities.vision_capability import VisionCapability
from oai_models import config_list_gpt4_turbo

# Based on example:
# https://microsoft.github.io/autogen/docs/notebooks/agentchat_lmm_gpt-4v/

gpt4_llm_config = {"config_list": config_list_gpt4_turbo, "cache_seed": 42}

agent1 = MultimodalConversableAgent(
    name="image-explainer-1",
    max_consecutive_auto_reply=10,
    llm_config={
        "config_list": config_list_gpt4_turbo,
        "temperature": 0.5,
        "max_tokens": 300,
    },
    system_message="Your image description is poetic and engaging.",
)

# No used
agent2 = MultimodalConversableAgent(
    name="image-explainer-2",
    max_consecutive_auto_reply=10,
    llm_config={
        "config_list": config_list_gpt4_turbo,
        "temperature": 0.5,
        "max_tokens": 300,
    },
    system_message="Your image description is factual and to the point.",
)

agent3 = autogen.AssistantAgent(
    name="agent-3",
    llm_config={
        "config_list": config_list_gpt4_turbo,
        "temperature": 0,
    },
    system_message="""
    Your job is to comment on the responses of the image explainers. Then use print_response to print the response.
    """,
)

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="Desribe image for me.",
    human_input_mode="TERMINATE",  # Try between ALWAYS, NEVER, and TERMINATE
    max_consecutive_auto_reply=10,
    code_execution_config={
        "use_docker": False
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

# We set max_round to 5
groupchat = autogen.GroupChat(
    agents=[agent1, agent3, user_proxy], messages=[], max_round=5
)

vision_capability = VisionCapability(
    lmm_config={
        "config_list": config_list_gpt4_turbo,
        "temperature": 0.5,
        "max_tokens": 300,
    }
)

group_chat_manager = autogen.GroupChatManager(
    groupchat=groupchat, llm_config=gpt4_llm_config
)
vision_capability.add_to_agent(group_chat_manager)


@user_proxy.register_for_execution()
@agent3.register_for_llm(description="print the response")
async def print_response():
    print("hello world")

    return "response printed"


rst = user_proxy.initiate_chat(
    group_chat_manager,
    message="""Write a poet for my image:
                        <img https://th.bing.com/th/id/R.422068ce8af4e15b0634fe2540adea7a?rik=y4OcXBE%2fqutDOw&pid=ImgRaw&r=0>.""",
)
