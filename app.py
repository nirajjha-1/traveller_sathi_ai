import streamlit as st
from langchain_core.messages import HumanMessage
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

# Import your graph and database settings from main.py
from main import graph, DATABASE_URL, connection_kwargs

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Traveller Sathi AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENHANCED CUSTOM CSS ---
st.markdown("""
<style>
    /* Global background and font */
    .stApp { 
        background-color: #0B0E14; 
        color: #E2E8F0;
    }
    
    /* Gradient Title */
    .main-title {
        background: -webkit-linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 10px;
    }
    
    /* Subtitle */
    .sub-title {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }
    
    .sidebar-badge {
        background: linear-gradient(145deg, #1F2937, #111827);
        padding: 12px 16px; 
        border-radius: 10px;
        margin-bottom: 12px; 
        font-size: 14px; 
        color: #E2E8F0;
        border: 1px solid #374151; 
        display: flex; 
        align-items: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .sidebar-badge:hover {
        transform: translateY(-2px);
        border-color: #4facfe;
    }
    .sidebar-badge span { margin-right: 12px; font-size: 18px; }
    
    /* Image Gallery Styling */
    .stImage > img {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .stImage > img:hover {
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = "Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2lakhs."

def set_prompt(prompt_text):
    st.session_state.user_prompt = prompt_text

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌍 Traveller Sathi</h2>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("**User Settings**")
    user_id = st.text_input("👤 Session ID", value="aarohi_user", help="Keeps track of your conversation history.")
    
    st.write("---")
    st.markdown("**Core Tech Stack**")
    st.markdown("""
        <div class="sidebar-badge"><span>🔗</span> LangGraph AI</div>
        <div class="sidebar-badge"><span>🧠</span> Groq LLaMA-3</div>
        <div class="sidebar-badge"><span>🗄️</span> PostgreSQL Memory</div>
        <div class="sidebar-badge"><span>🔍</span> Tavily Search API</div>
        <div class="sidebar-badge"><span>✈️</span> AviationStack</div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown('<div class="main-title">Traveller Sathi AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your multi-agent autonomous travel planner. Flights, hotels, and itineraries—sorted in seconds.</div>', unsafe_allow_html=True)

# --- DESTINATION GALLERY ---
st.markdown("#### 🌟 Popular Inspirations")
img_cols = st.columns(4)
with img_cols[0]:
    st.image("https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=400&fit=crop", caption="🇯🇵 Tokyo, Japan", use_container_width=True)
with img_cols[1]:
    st.image("https://unsplash.com/photos/eiffel-tower-at-paris-france-QAwciFlS1g4?w=600&h=400&fit=crop", caption="🇫🇷 Paris, France", use_container_width=True)
with img_cols[2]:
    st.image("https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&h=400&fit=crop", caption="🇮🇩 Bali, Indonesia", use_container_width=True)
with img_cols[3]:
    st.image("https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&h=400&fit=crop", caption="🇦🇪 Dubai, UAE", use_container_width=True)

st.write("---")

# --- INPUT SECTION ---
st.markdown("#### 🗺️ Design Your Next Adventure")

# Quick Prompts
btn_cols = st.columns(4)
if btn_cols[0].button("⛩️ 7-day Japan under ₹2L", use_container_width=True): set_prompt("Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2lakhs.")
if btn_cols[1].button("🥐 Paris trip for 5 days", use_container_width=True): set_prompt("Plan a complete 5 days Paris trip including flights, hotels and sightseeing.")
if btn_cols[2].button("🐪 Dubai weekend escape", use_container_width=True): set_prompt("Plan a weekend getaway to Dubai including flights and a luxury hotel.")
if btn_cols[3].button("🎒 Bali backpacking 10 days", use_container_width=True): set_prompt("Plan a 10 days backpacking trip to Bali with cheap flights and hostels.")

# Query Input
user_query = st.text_area("Tell us what you are looking for:", value=st.session_state.user_prompt, height=120)

# --- EXECUTION PIPELINE ---
if st.button("🚀 Generate My Travel Plan", type="primary", use_container_width=True):
    if user_query.strip():
        
        st.write("---")
        st.markdown("### ⚡ Live Agent Pipeline")
        
        # Create empty placeholders for live streaming
        flight_ui = st.empty()
        hotel_ui = st.empty()
        itinerary_ui = st.empty()
        final_ui = st.empty()

        # Connect to DB and run the graph
        with ConnectionPool(conninfo=DATABASE_URL, max_size=20, kwargs=connection_kwargs) as pool:
            checkpointer = PostgresSaver(pool)
            app = graph.compile(checkpointer=checkpointer)
            
            config = {"configurable": {"thread_id": user_id}}
            initial_state = {
                "messages": [HumanMessage(content=user_query)],
                "user_query": user_query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0
            }

            # Stream updates dynamically as each node completes
            for event in app.stream(initial_state, config=config, stream_mode="updates"):
                
                if "flight_agent" in event:
                    with flight_ui.expander("🛫 **Flight Agent Output**", expanded=True):
                        st.info("Flight data retrieved successfully.")
                        st.text(event["flight_agent"]["flight_results"])
                        
                elif "hotel_agent" in event:
                    with hotel_ui.expander("🏨 **Hotel Agent Output**", expanded=True):
                        st.info("Accommodation search completed.")
                        st.markdown(event["hotel_agent"]["hotel_results"])
                        
                elif "itinerary_agent" in event:
                    with itinerary_ui.expander("📅 **Itinerary Agent Output**", expanded=True):
                        st.info("Day-by-day plan drafted.")
                        st.markdown(event["itinerary_agent"]["itinerary"])
                        
                elif "final_agent" in event:
                    with final_ui.expander("🎯 **Final Travel Plan**", expanded=True):
                        st.success("Synthesis complete! Here is your final package.")
                        final_response = event["final_agent"]["messages"][-1].content
                        st.markdown(final_response)
                        
            st.balloons()
            st.success("✨ Trip plan successfully generated and saved to memory!")
    else:
        st.warning("Please describe your trip before generating a plan.")