import requests
import streamlit as st

def generate_avatar(prompt: str) -> str:
    replicate_token = st.secrets["replicate"]["key"]
    
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {replicate_token}",
            "Content-Type": "application/json"
        },
        json={
            "version": "YOUR_MODEL_VERSION_ID",  # e.g. from replicate.com
            "input": {"prompt": prompt}
        }
    )
    return response.json().get("urls", {}).get("get", "")
