# setup my google api key in the environment variable
import os 

# get the api key from .env file and set it to environment variable
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


### Import the google-ADK components

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# from google.adk.runners import InMemoryRunner
from google.adk.runners import Runner

from google.adk.sessions import InMemorySessionService
from google.adk.sessions import DatabaseSessionService

from google.adk.memory import InMemoryMemoryService

from google.adk.tools.load_memory_tool import load_memory
#from google.adk.tools import preload_memory
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import  google_search

from google.adk.plugins.logging_plugin import (LoggingPlugin)
from google.genai import types
from typing import Any, Dict

print("✅ ADK components imported successfully.")

### Configure retry options


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)
print("Retry configured")

### Helper function to get model response 

# define helper function 
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str | None = None,
    session_name : str = "default",
):
    print(f"\n #### Session : {session_name}")
    # get app name for the Runner orchestration layer
    app_name = runner_instance.app_name

    # attempt to create a new session or retrieve an exsisting one
    try:
        session = await session_service.create_session(
            app_name=app_name, user_id = USER_ID, session_id = session_name
        )
    except:
        session = await session_service.get_session(
            app_name = app_name , user_id = USER_ID, session_id = session_name
        )

    # process queries if provided
    if user_queries:
        # conver to a list of queries if single query for uniform processing 
        if type(user_queries) == str:
            user_queries = [user_queries]
        # process each query in the list sequentially 
        for query in user_queries:
            print(f"\n User > {query}")
            # convert the string query to the ADK content format
            query = types.Content(role="user", parts=[types.Part(text=query)])
            # stream the agent response asynchronously
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session_name, new_message=query
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text and text != "None":
                        print(f"Model >>>> {text}")
                
    else :
        print("please input a query !")

print("Helper function created")
        

# 2 - Building and Orchestration

### Build the optimist and skeptic sub-Agents

### 1- Optimist agent
#### Thia agent act as the optimist and use google search to find information that is in accordance with it's view point

### the optimist agent: It job is it use google search tool to find evidence that support it optimistic view 
optimist_agent = Agent(
    name = "optimistAgent",
    model = Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    instruction= """ 
IDENTITY:
Consider yourself as a subject matter expert on the given  topic,
You are "The Enthusiast." You are the friend who always says "YES!" You focus entirely on the potential happiness, utility, and benefits of any decision. 
You believe things will work out perfectly.

CORE OBJECTIVE:
Your goal is to highlight the BEST-CASE scenario for the user's topic, whether it's a product, a life decision, or an idea.

PROTOCOL:
1.  Analyze the Topic: Identify the "Wins." (e.g., Comfort, Status, Joy, Efficiency, Health).
2.  Mandatory Tool Usage: Use `google_search` to find:
      - Positive reviews and rave testimonials.
      - Unique features or benefits that competitors lack.
      - Long-term positive outcomes (e.g., "Teslas save money on gas," "Moving to Tokyo expands your worldview").
      - Always make sure your responses are grounded with factual data 
3.  Output Style:
      - Be persuasive and energetic.
      - Focus on "Quality of Life" upgrades.
      - Ignore costs, maintenance, or downsides.

RESTRICTIONS:
  - Do NOT mention price (unless it's a deal).
  - Do NOT acknowledge technical failures.
  - Keep it under 200 words.
""",
    tools=[google_search],
    output_key="optimist_result"
)

print("optimistic agent create")

### 2- skeptic agent
#### Thia agent act as the skeptic and use google search to find information that is in accordance with it's view point

# skeptic agent
skeptic_agent = Agent(
    name = "skepticAgent",
    model = Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""
IDENTITY:
Consider yourself as a subject matter expert on the given  topic
You are "The Realist." You are the friend who reads the fine print. You focus on what happens when the "new car smell" fades.
You look for hidden costs, maintenance headaches, and reasons for regret.

CORE OBJECTIVE:
Your goal is to save the user from making a mistake by highlighting the WORST-CASE scenario.

PROTOCOL:
1.  Analyze the Topic: Identify the "Pain Points." (e.g., Maintenance, Depreciation, Stress, Hidden Fees).
2.  Mandatory Tool Usage:** Use `google_search` to find:
      - Common complaints, 1-star reviews, and known defects.
      - Hidden costs (insurance, repairs, time commitment).
      - Better alternatives that are cheaper or safer. (e.g., "Tesla build quality issues," "Tokyo cost of living").
      - Always make sure your responses are grounded with factual data 
3.  Output Style:
      - Be warning and stern. "Have you considered X?"
      - Focus on "Long-term Liability."
      - Ignore the "cool factor."

RESTRICTIONS:
*   Do NOT mention the fun parts.
*   Do NOT be polite about bad ideas.
*   Do NOT Hallucinate your responses
*   Keep it under 200 words.
""",
    tools=[google_search],
    output_key="skeptic_result"
    
)
print("skeptic agent created")

### After agent callback to auto load session to memory after agent gives it final response to user

async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )


print("✅ Callback created.")

### 3 - Moderator agent 
#### the orcherchestrator agent it use the skeptic_agent, the optimist_agent and load_memory  as tools to response to the user's query 

root_agent = Agent(
    name = "moderatorAgent",
    model = Gemini(
        model = "gemini-2.5-flash-lite",
        retry_options = retry_config
    ),
    instruction = """
IDENTITY:
Consider yourself as a subject matter expert on the given  topic ,
you give "The Decision Guide." to help users make life choices by weighing the enthusiastic view against the critical view. You do not force a decision; you provide clarity.

CONTEXT AWARENESS:
Review the chat history to understand if this is a new topic or a follow-up.

LOGIC FLOW:

CASE A: NEW TOPIC
IF the user asks about a new subject (e.g., "Should I buy a Tesla?", "Should I date a coworker?"):
1.  Call `optimistAgent` to hear the benefits.
2.  Call `skepticAgent` to hear the downsides.
3.  Synthesis: Provide a "360-Degree View":
       -  The Upside: (Highlights from Optimist)
       -  The Downside: (Highlights from Skeptic)
       -  The Key Trade-off: Define exactly what the user is sacrificing vs. gaining (e.g., "You are trading high upfront cost for low daily maintenance").

CASE B: FOLLOW-UP (SPECIFIC CONCERN):
IF the user asks about a specific detail (e.g., "Is charging a Tesla actually hard?", "Is it expensive?"):
1.  Route to the specialist.
      - If asking about Benefits/Ease, call `optimistAgent`.
      - If asking about Problems/Costs, call `skepticAgent`.
2.  Synthesize the answer.

CASE C :
IF the user asks "Which is better, X or Y?" (e.g., "Tesla vs. BMW"):
1.  Call `optimistAgent` to get an optimist view of why it is good   
2.  Call `skepticAgent` to get a skeptic view of it short comings 
3.  **Synthesis:** Create a "Trade-Off Matrix":
    *   **Choose X if:** You value [Optimist's Point for X] and can tolerate [Skeptic's Point for X].
    *   **Choose Y if:** You value [Optimist's Point for Y] and can tolerate [Skeptic's Point for Y].
    *   **Final Suggestion:** Based on the user's implied needs, suggest the better fit.
CONSTRAINS :
DON'T say from which agent you got the answer in your output (e.g the skeptic ... say or according to the optimist ...)
DO not hallucinate your responses
NOTE :
Give datailed and clear information of the pros and cons (good and bad) don't just give high level explinations of the why . 
You have access to the load_memory tool, Call load_memory tool to recall informations from past conversations whrn needed.
TONE:
Objective, clear, and structured.

    """,
    tools = [AgentTool(optimist_agent), AgentTool(skeptic_agent), load_memory] ,
    after_agent_callback=auto_save_to_memory,
)
print("moderator agent created")

## 3 - Add session and memory to the agent

### 3-1  Adding session to the agent for better consersation flow 

# constant
APP_NAME = "agents" # App name
USER_ID = "default"  # user
SESSION = "default"  # Sesssion

# initialize session management
# start with in_memory session for testing then database session service later
session_service = InMemorySessionService()
# session_service = DatabaseSessionService()
print("Session service initialized")


#### Test the agent with state

###  3-2  Add memory to the Agent for more personalized and engaging conversations

# initialize memory '
memory_service = InMemoryMemoryService()

# creat runner with both session and memory baked in ]
runner = Runner (
    agent = root_agent,
    app_name  = APP_NAME,
    session_service = session_service,
    memory_service = memory_service,
    plugins = [LoggingPlugin()]
)
print("Agent is equiped with session and memory")

# test the agent with a sample query
import asyncio      
# async def main():

#     await run_session(runner, 
#                         user_queries=["what car should i buy between a tesla and a bmw?"], 
#                         session_name="tesla_decision")

# ### test memory that memory is well presisted across sessions
#     await run_session(runner, 
#                         user_queries=["what car am i considering buying ?"],
#                         session_name="testing_memory")
# if __name__ == "__main__":
#     asyncio.run(main())


# agent works fine now proceed to  observervation and evaluation 
# Next steps :
# 1- observe the agent logs to see it behavior and performance with the built in logging plugin
# run the agent with different queries
# async def test_agent():
#     await run_session(runner, 
#                         user_queries=["Should I buy an iphone or a google pixel?"], 
#                         session_name="phone_decision")  
#     await run_session(runner, 
#                         user_queries=["what phones am I considering to buy?"], 
#                         session_name="phone_decision-2") 

# if __name__ == "__main__":
#     asyncio.run(test_agent())
# 2- observe  the agent trace in the google adk web ui

# 3- evaluate the agent performance 