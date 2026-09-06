# 🌍✈️ Traveller Sathi AI

Traveller Sathi AI is an autonomous, multi-agent travel planner designed to eliminate the hassle of managing endless browser tabs while researching a trip. By orchestrating a team of specialized AI agents, it instantly searches for real-time flights, finds top-rated accommodations, and generates complete day-by-day itineraries based on your budget and preferences.

Instead of relying on a single large language model prompt to do all the heavy lifting, Traveller Sathi breaks down the travel planning process into focused micro-tasks. The result is faster, highly accurate, and hallucination-free trip planning with a sleek, live-streaming user interface.

## ✨ Features

* **Multi-Agent Orchestration:** Specialized agents (Flight, Hotel, and Itinerary) pass structured state context to one another to build a comprehensive final plan.
* **Real-Time Data Extraction:** Integrates with live APIs to pull actual flight schedules and current hotel recommendations.
* **Persistent User Memory:** Utilizes PostgreSQL to save conversation states. The AI remembers your previous chats, preferences, and generated itineraries across sessions via unique User IDs.
* **Live Streaming UI:** A custom Streamlit frontend that visually unpacks the pipeline, displaying each agent's thought process and output in real-time as they complete their specific tasks.
* **Lightning-Fast Inference:** Powered by Groq's API and the LLaMA-3 model for near-zero latency reasoning.

## 🛠️ Tech Stack

* **AI & Orchestration:** [LangGraph](https://python.langchain.com/docs/langgraph) (StateGraph), [Groq LLaMA-3](https://groq.com/)
* **APIs & Tools:** [AviationStack](https://aviationstack.com/) (Flights), [Tavily](https://tavily.com/) (Search/Hotels)
* **Database & Memory:** PostgreSQL, `langgraph-checkpoint-postgres`, `psycopg_pool`
* **Frontend:** [Streamlit](https://streamlit.io/)

## ⚙️ Agent Pipeline Architecture

1. **Flight Agent:** Extracts departure/arrival locations and dates from the user query, calls the AviationStack API, and formats the top 5 flight options.
2. **Hotel Agent:** Uses Tavily Search to find the best hotels matching the user's destination and budget criteria.
3. **Itinerary Agent:** Synthesizes the user query, flight data, and hotel data to generate a cohesive day-by-day travel plan.
4. **Final Agent:** Packages the complete output into an engaging, structured response for the user.

## 🚀 Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/Traveller_Sathi_AI.git
cd Traveller_Sathi_AI

```

**2. Create a virtual environment**

```bash
python3 -m venv traveller_sathi_env
source traveller_sathi_env/bin/activate

```

**3. Install dependencies**

```bash
pip install -r requirements.txt

```

*(Ensure your `requirements.txt` includes `streamlit`, `langgraph`, `langgraph-checkpoint-postgres`, `psycopg_pool`, `langchain-groq`, `requests`, `python-dotenv`)*

**4. Configure PostgreSQL**
You must have PostgreSQL installed and running. Create a database and user with appropriate permissions:

```sql
CREATE DATABASE ai_memory;
CREATE USER ai_user WITH PASSWORD 'yourpassword';
ALTER DATABASE ai_memory OWNER TO ai_user;
GRANT ALL ON SCHEMA public TO ai_user;

```

**5. Set up Environment Variables**
Create a `.env` file in the root directory and add your API keys and database URL:

```env
GROQ_API_KEY=your_groq_api_key_here
AVIATIONSTACK_API_KEY=your_aviationstack_key_here
TAVILY_API_KEY=your_tavily_key_here
DATABASE_URL=postgresql://ai_user:yourpassword@localhost:5432/ai_memory?sslmode=disable

```

## 💻 Running the Application

To launch the interactive Streamlit frontend, run:

```bash
streamlit run app.py

```

The application will start a local web server (usually at `http://localhost:8501`). Enter your desired travel request in the prompt box, provide a unique Session ID, and watch the agents build your trip in real-time.
