import os
from openai import OpenAI
import streamlit as st
from duckduckgo_search import DDGS  

# Function to search the web automatically
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results:
                return "\n".join([f"Source: {r.get('title')} ({r.get('href')})\nSummary: {r.get('body')}" for r in results])
    except Exception:
        pass
    return "No web search results available."
# Custom styling for the main button
st.markdown("""
<style>
/* Style all primary action buttons in Streamlit */
div.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%) !important;
    color: white !important;
    border: none !important;
    padding: 12px 28px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    box-shadow: 0px 4px 15px rgba(168, 85, 247, 0.4) !important;
    transition: all 0.3s ease-in-out !important;
    width: 100% !important;
}

/* Hover and active state animations */
div.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0px 6px 20px rgba(236, 72, 153, 0.6) !important;
    cursor: pointer !important;
}

div.stButton > button:active {
    transform: translateY(1px) scale(0.99) !important;
}
</style>
""", unsafe_allow_html=True)
# Streamlit Page Configuration
st.set_page_config(
    page_title="Symestro - AI Synthesis Platform", page_icon="🪄", layout="wide"
)

st.title("🪄 Symestro")
st.caption(
    "Orchestrating multiple AI models to deliver unified, synthesized answers."
)
st.write(
    "Ask a question, and this app will consult multiple AI models and synthesize"
    " the ultimate answer for you!"
)

# Sidebar for API Key input so users can provide their own key safely
st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input(
    "OpenRouter API Key",
    type="password",
    value=os.getenv("OPENROUTER_API_KEY", ""),
)

user_prompt = st.text_area(
    "What do you want to ask the AI collective?",
    placeholder="e.g., Explain quantum computing in simple terms.",
)

if st.button("Resonate & Generate Answer"):
  if not api_key_input:
    st.error("Please enter your OpenRouter API Key in the sidebar.")
  elif not user_prompt:
    st.warning("Please enter a prompt first.")
  else:
    # 1. Fetch live web search results first
    with st.spinner("Searching the web for live context..."):
        search_context = search_web(user_prompt)
        
    # 2. Combine the user's question with the live web search context
    enhanced_prompt = f"""User Question: {user_prompt}

Live Web Search Context (Use this for up-to-date facts or missing details):
{search_context}"""

    # Initialize OpenRouter Client with user-provided key
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key_input)

    models = [
        "nvidia/nemotron-3.5-lightning:free",
        "thinkingmachines/inkling-small:free",
        "dots-studio/dots-3-note-preview:free",
    ]

    responses = {}
    status_container = st.status(
        "Consulting multiple AI models...", expanded=True
    )
   for model in models:
        try:
            status_container.write(f"Querying `{model}`...")
            completion = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt,
                }],
            )
            responses[model] = completion.choices[0].message.content
        except Exception as e:
            responses[model] = f"Error: {str(e)}"
    

    status_container.write("Synthesizing final response...")

    synthesis_prompt = f"""
        You are the master synthesizer AI. Below are responses from several different AI models to the same user prompt: '{user_prompt}'.
        
        Analyze all perspectives, cross-check facts, discard errors or contradictions, and synthesize the ultimate, highest-quality, most comprehensive answer possible.
        
        Model Responses:
        {responses}
        """

    try:
      final_synthesis = client.chat.completions.create(
          model="openrouter/free",
          messages=[{"role": "user", "content": synthesis_prompt}],
      )
      status_container.update(
          label="Done! Answer generated successfully.",
          state="complete",
          expanded=False,
      )

      st.subheader("✨ Final Synthesized Answer")
      st.markdown(final_synthesis.choices[0].message.content)

    except Exception as e:
      st.error(f"Synthesis failed: {str(e)}")
