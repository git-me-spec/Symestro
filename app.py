import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

# Page Config & Custom CSS
st.set_page_config(page_title="Symestro", page_icon="ͳͱ", layout="wide")

# Custom CSS for modern UI and buttons
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for API Key & Configuration
with st.sidebar:
    st.subheader("⚙️ Configuration")
    api_key_input = st.text_input("OpenRouter API Key", type="password")
    st.markdown("---")
    st.markdown("### 🧠 Collective Models")
    st.info("Symestro queries multiple frontier free models simultaneously and synthesizes their logic.")

# Top-tier reasoning and multimodal models for your collective
models = [
    "nvidia/nemotron-3.5-lightning:free",
    "thinkingmachines/inkling-small:free",
    "dots-studio/dots-3-note-preview:free",
]

st.title("⚡ Symestro AI Orchestrator")
st.caption("Advanced Mixture-of-Agents Collective with Live Web Context & Multimodal Reasoning")

# User Input Section (Text + Optional Image Upload for Math/Logic/Diagrams)
user_prompt = st.text_area(
    "What do you want to ask the AI collective?",
    placeholder="e.g., Solve this complex calculus proof, analyze logic, or explain advanced theory...",
)

uploaded_file = st.file_uploader("Upload an image (optional — for math, logic puzzles, or diagrams)", type=["png", "jpg", "jpeg"])

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except Exception:
        return "Web search unavailable."

if st.button("Resonate & Generate Answer"):
    if not api_key_input:
        st.error("Please enter your OpenRouter API Key in the sidebar.")
    elif not user_prompt:
        st.warning("Please enter a prompt first.")
    else:
        # 1. Fetch live web search results first
        with st.spinner("Searching the web for live context..."):
            search_context = search_web(user_prompt)

        # 2. Combine question, web context, and handle image input if provided
        enhanced_prompt = f"""User Question: {user_prompt}

Live Web Search Context (Use this for up-to-date facts or missing details):
{search_context}"""

        # Initialize OpenRouter Client
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key_input)

        responses = {}
        status_container = st.status("Consulting multiple AI models...", expanded=True)
        
        for model in models:
            try:
                status_container.write(f"Querying `{model}`...")
                
                # Build message payload (supports text and images if uploaded)
                if uploaded_file:
                    import base64
                    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                    messages = [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": enhanced_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                        ]
                    }]
                else:
                    messages = [{"role": "user", "content": enhanced_prompt}]

                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                responses[model] = completion.choices[0].message.content
            except Exception as e:
                responses[model] = f"Error: {str(e)}"

        status_container.write("Synthesizing final response...")

        synthesis_prompt = f"""
You are the master synthesizer AI. Below are responses from several different AI models to the same user prompt:

Analyze all perspectives, cross-check facts, discard errors or contradictions, and synthesize the ultimate, highest-quality, mathematically/logically rigorous final answer.

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

            with st.expander("🔍 View Individual Model Responses"):
                for mod, resp in responses.items():
                    st.markdown(f"**Model: `{mod}`**")
                    st.write(resp)
                    st.markdown("---")

        except Exception as e:
            st.error(f"Synthesis failed: {str(e)}")
