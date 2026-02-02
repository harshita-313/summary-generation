import os
import uuid
import streamlit as st
from streamlit_javascript import st_javascript
from openai import OpenAI
from dotenv import load_dotenv
from mysql_database import insert_conversation, fetch_summary, delete_summary

load_dotenv()
openai_api = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")
client = OpenAI(api_key=openai_api)

transcription_text = None

st.title("Audio Summarization")

st.markdown(
    """
    <style>
    .st-emotion-cache-k30353 {
        background: transparent;
        font-family: "Source Sans", sans-serif !important;
        padding-left: 0px;
        font-size: 16px
    }
    .st-emotion-cache-rv01uy p, .st-emotion-cache-rv01uy ol, .st-emotion-cache-rv01uy ul, .st-emotion-cache-rv01uy dl, .st-emotion-cache-rv01uy li {
        font-size: 13px !important; 
    }

    button.st-emotion-cache-1cl4umz.e1haskxa1 {
        border-radius: 20px;
        padding-left: 20px;
        padding-right: 20px;
    }

    button.st-emotion-cache-5qfegl.e1haskxa2 {
        background-color: #f0f2f6 !important;
        border-radius: 20px !important;
        border: none !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }

    .st-emotion-cache-9114l4 {
        display: block;
        overflow: hidden;
        text-align: left;
        background-color: transparent;
        border: none;
        padding: 0px;
        }

    .st-emotion-cache-9114l4 p{
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .st-emotion-cache-6ms01g p{
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .st-emotion-cache-6ms01g {
    display: block;
    overflow: hidden;
    text-align: left;
    background-color: transparent;
    border: none;
    padding: 0px;
}

    [data-testid="stSidebar"] .st-emotion-cache-tn0cau {
        gap: 0px;
    }

    [data-testid="stSidebar"] .st-emotion-cache-zh2fnc {
        width: 100%;
    }

    [data-testid="stSidebar"] .st-emotion-cache-px2xcf h1{
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] .st-emotion-cache-rv01uy h1 {
        padding-bottom: 2rem;
    }

    .st-emotion-cache-fojvt9 {
        display: block;
        border: none !important;
        background: none !important;
        width: auto;
    }

    .st-emotion-cache-6ms01g {
        border: none;
    }

    </style>

    """, unsafe_allow_html=True
)

# STEP 1: TRY TO READ LOCALSTORAGE
user_id = st_javascript("localStorage.getItem('ajs_anonymous_id');")
st.session_state.user_id = user_id

with st.sidebar:
    st.title("Recent Summaries")

    if user_id:
        history_rows = fetch_summary(user_id, 10)
        if history_rows:
            for row in history_rows:
                id = row[0]
                transcript = row[2]
                summary = row[3]

                snippet = summary[:80] + "..." if len(summary) > 80 else summary

                if st.button(snippet, key=f"hist_{id}"):
                    st.session_state.selected_id = id
                    st.session_state.selected_transcript = transcript
                    st.session_state.selected_summary = summary
                    st.session_state.viewing_history = True
        else:
            st.write("*No history yet*")
    else:
        st.write("*No history yet*")

# Initialize history
if 'history' not in st.session_state:
    st.session_state.history = []

if not st.session_state.get("viewing_history", False) and not st.session_state.get("summary_generated", False):

    if "recorded" not in st.session_state:
        st.session_state.recorded = False

    if not st.session_state.recorded:
        audio_value = st.audio_input("Record a voice message")

        if audio_value is not None:
            st.session_state.recorded = True
            st.session_state.audio = audio_value
            st.rerun()

    if "audio" in st.session_state and st.session_state.recorded:
        audio_value = st.session_state.audio
        if audio_value:
            st.audio(audio_value)
            transcription = client.audio.transcriptions.create (
                model = "whisper-1",
                file = audio_value,
                )
            st.header("Transcript")
            st.write(transcription.text)
            transcription_text = transcription.text

            if 'run_button' in st.session_state and st.session_state.run_button == True:
                st.session_state.running = True
            else:
                st.session_state.running = False

            if st.button('Generate Summary', disabled=st.session_state.get("run_button", False), key='run_button'):
                    if transcription_text != None:   
                        response = client.responses.create(
                            model = openai_model,
                            input = f'Summarize the following transcript clearly and concisely in easy manner and try to use new/synonym words for the summary. Also the language of the transcript and the summary should be same\n\nTranscript:\n{transcription_text}\n ',
                            reasoning={"effort": "medium"},
                        )

                        st.header("Summary")
                        st.code(response.output_text, wrap_lines=True, language='text')

                        st.session_state.history.append(response.output_text)

                        # DATA INSERTION INTO MYSQL DB 
                        insert_conversation(
                            user_id = user_id,
                            transcript = transcription_text,
                            summary = response.output_text
                        )
                    else:
                        st.write ("Transcription not Found!")
            
            if st.button("New Input"):
                for key in ["transcription_text", "summary", "run_button"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    else:
        st.write('Say Something')

# --- SHOW HISTORY SESSION IF SELECTED ---
if st.session_state.get("viewing_history", False):
    st.subheader("Transcript")
    st.write(st.session_state.selected_transcript)

    st.subheader("Summary")
    st.code(st.session_state.selected_summary, wrap_lines=True)

    if st.button("Delete", type="primary"):
        delete_summary(st.session_state.selected_id)
        st.session_state.clear()
        st.rerun()

    if st.button("New Input", type="secondary"):
        st.session_state.clear()
        st.rerun()





