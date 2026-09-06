import os
from typing import Annotated, TypedDict
import operator

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_serach
from tools.flight_tool import search_flights

from dotenv import load_dotenv 
load_dotenv()

llm = ChatGroq(
    model = "openai/gpt-oss-120b"
)

# 4. Set up the PostgreSQL Connection String
# Format: postgresql://[USER]:[PASSWORD]@localhost:5432/[DATABASE_NAME]?sslmode=disable
# DB_URI = "postgresql://ai_user:secretpassword@localhost:5432/ai_memory?sslmode=disable"
DATABASE_URL = os.getenv("DATABASE_URL")

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls:int

def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)
    return {
        "flight_results" : flight_data,
        "messages" : [
            AIMessage(content="Flight result fetched")
        ],
        # "llm_calls" : state.get("llm_calls",0) + 1
    }

def hotel_agent(state: TravelState):
    query = f"Best hotel for {state["user_query"]}"
    hotel_data = tavily_serach(query)
    return {
        "hotel_results" : hotel_data,
        "messages" : [
            AIMessage(content="Hotel information fetched")
        ],
        # "llm_calls" : state.get("llm_calls",0) + 1
    }

def itinerary_agent(state: TravelState):
    prompt = f"""
    Create a travel itinerary.
    User Query :
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}
    """


    response = llm.invoke(
            [
                SystemMessage(
                    content="You are an expert travel planner"
                ),
                HumanMessage(content=prompt)
            ]
    )

    return {
        "itinerary" : response.content,
        "messages" : [response],
        "llm_calls" : state.get("llm_calls",0) + 1
    }

def final_agent(state: TravelState):
    final_prompt = f"""
    Generate final travel response.
    Flights:
    {state['flight_results']}

    Hotels:
    {state['hotel_results']}

    Itinerary:
    {state['itinerary']}
    """

    response = llm.invoke(
        [
            HumanMessage(content=final_prompt)
        ]
    )

    return {
        "messages" : [response],
        "llm_calls" : state.get("llm_calls",0) + 1
    }

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

# _conn = psycopg.connect(DATABASE_URL)
# checkpointer = PostgresSaver(_conn)
# checkpointer.setup()
connection_kwargs = {
    "autocommit" : True,
    "prepare_threshold" : 0,
}




if __name__ == "__main__":

    with ConnectionPool(conninfo=DATABASE_URL, max_size=20, kwargs=connection_kwargs) as pool:
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()

        app = graph.compile(checkpointer=checkpointer)
        config = {
            "configurable": {
                "thread_id" : "user1"
            }
        }

        user_input = input("Enter travel request : ")

        result = app.invoke(
            {
                "messages" : [
                    HumanMessage(content=user_input)
                ],
                "user_query" : user_input,
                "flight_results" : "",
                "hotel_results" : "",
                "itinerary" : "",
                "llm_calls" : 0
            },
            config=config
        )

        print("\n FINAL RESPONSE : \n")

        for msg in result['messages']:
            print(msg.content)