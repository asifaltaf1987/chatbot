__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
from tools.stable_diffusion import generate_avatar
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_feedback import streamlit_feedback
import toml
import chromadb
import datetime

# Load config
cbconfig = toml.load("cbconfig.toml")
AVATARS = cbconfig['AVATARS']
ROLES = cbconfig['ROLES']

# Hide extra UI
HIDEMENU = """
<style>
.stApp [data-testid="stHeader"] { display:none; }
p img{ margin-bottom: 0.6rem; }
[data-testid="stSidebarCollapseButton"],
[data-testid="baseButton-headerNoPadding"],
.stChatInput button,
#chat-with-sjsu-library-s-kingbot a { display:none; }
</style>
"""

@st.cache_resource(ttl="1d", show_spinner=False)
def getIndex():
    import os
    from llama_index.core import Settings

    # Fallback to env if Streamlit secrets is not used
    api_key = st.secrets["openai"]["key"] if "openai" in st.secrets else os.getenv("OPENAI_API_KEY")
    embedding = OpenAIEmbedding(api_key=api_key)

    # Manually set the embedding in LlamaIndex Settings
    Settings.embed_model = embedding

    chroma_client = chromadb.PersistentClient(path="./llamachromadb")
    collection = chroma_client.get_or_create_collection("rcsilib")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    
    # IMPORTANT: use manually set embedding model
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embedding)
    return index

def getBot(memory):    
    index = getIndex()       
    llm = OpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets.openai.key)
    today = datetime.date.today().strftime('%B %d, %Y')

    context = "Refer to the following context documents to answer user queries based on our library's FAQ database. Do not hallucinate. If unsure, refer users to Ask A Librarian at https://libchat.rcsi-mub.com/"

    system_prompt = (
        "You are Laira, the AI assistant for the Library of RCSI Medical University of Bahrain. Respond supportively and professionally like a peer mentor.\n\n"
        "Guidelines:\n"
        "1. No creative content (stories, poems, tweets, code)\n"
        "2. Simple jokes are allowed, but avoid jokes that could hurt any group\n"
        "3. Use up to two emojis when applicable\n"
        "4. Provide relevant search terms if asked\n"
        "5. Avoid providing information about celebrities, influential politicians, or state heads\n"
        "6. Keep responses under 300 characters\n"
        "7. For unanswerable research questions, include the 'Ask A Librarian' URL: https://libchat.rcsi-mub.com/\n"
        "8. Do not make assumptions or fabricate answers or URLs\n"
        "9. Use only the database information and do not add extra information if the database is insufficient\n"
        "10. If you don't know the answer, just say that you don't know, and refer users to the 'Ask A Librarian' URL: https://libchat.rcsi-mub.com/\n"
        "11. Do not provide book recommendations; refer users to try their search on a library database\n"
        "12. Please end your response with a reference URL from the source of the response content.\n"
        f"13. Today is {today}. Use this information to answer time-sensitive questions about library hours or events.\n"
        "14. When users ask about research or subject-specific topics, first recommend Primo: https://rcsibahrain.primo.exlibrisgroup.com/discovery/search?vid=973RCSIB_INST:RCSIB&lang=en then suggest specialized databases from https://library.rcsi-mub.com/az/databases.\n"
        f"{context}"
    )

    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=memory,
        llm=llm,
        system_prompt=system_prompt,
        verbose=False,    
    )
    return chat_engine

def queryBot(user_query, bot, chip=''):
    current = datetime.datetime.now()
    st.session_state.moment = current.isoformat()
    session_id = st.session_state.session_id
    
    st.chat_message("user", avatar=AVATARS["user"]).write(user_query)
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):  
        with st.spinner(text="In progress..."):
            try:
                response = bot.chat(user_query)
                answer = getattr(response, "response", None)
                if not answer:
                    answer = "⚠️ Sorry, I couldn't find an answer. Please try rephrasing your question or check the [Library FAQs](https://libchat.rcsi-mub.com/)."
                st.write(answer)
                st.write(response.source_nodes)  # Debug: Show source evidence
            except Exception as e:
                st.error(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":

    st.set_page_config(page_title="Laira - RCSI Bahrain Library", page_icon="🤖", initial_sidebar_state="expanded")
    st.markdown(HIDEMENU, unsafe_allow_html=True)

    st.sidebar.markdown(cbconfig['side']['title'])
    st.sidebar.markdown(cbconfig['side']['intro'])
    st.sidebar.markdown("\n\n")
    st.sidebar.link_button(cbconfig['side']['policylabel'], cbconfig['side']['policylink'])

    col1, col2, col3 = st.columns([0.25, 0.1, 0.65], vertical_alignment="bottom")
    with col2:
        st.markdown(cbconfig['main']['logo'])
    with col3:
        st.title(cbconfig['main']['title'])
    st.markdown("\n\n\n\n")

    col21, col22, col23 = st.columns(3)
    with col21:
        button1 = st.button(cbconfig['button1']['label'])
    with col22:
        button2 = st.button(cbconfig['button2']['label'])
    with col23:
        button3 = st.button(cbconfig['button3']['label'])

    if 'memory' not in st.session_state:
        memory = ChatMemoryBuffer.from_defaults(token_limit=5000)
        st.session_state.memory = memory
    memory = st.session_state.memory

    if 'mybot' not in st.session_state:
        st.session_state.mybot = getBot(memory)
    bot = st.session_state.mybot

    if 'session_id' not in st.session_state:
        session_id = get_script_run_ctx().session_id
        st.session_state.session_id = session_id

    if 'reference' not in st.session_state:
        st.session_state.reference = ''

    max_messages: int = 10
    allmsgs = memory.get()
    msgs = allmsgs[-max_messages:]

    for msg in msgs:
        st.chat_message(ROLES[msg.role], avatar=AVATARS[msg.role]).write(msg.content)

    if button1:
        queryBot(cbconfig['button1']['content'], bot, cbconfig['button1']['chip'])
    if button2:
        queryBot(cbconfig['button2']['content'], bot, cbconfig['button2']['chip'])
    if button3:
        queryBot(cbconfig['button3']['content'], bot, cbconfig['button3']['chip'])

    if user_query := st.chat_input(placeholder="Ask me about the RCSI Library!"):
        queryBot(user_query, bot)

    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "Optional. Please provide extra information",
    }

    if 'moment' in st.session_state:
        currents = st.session_state.moment
        streamlit_feedback(**feedback_kwargs, args=(currents,), key=currents)
