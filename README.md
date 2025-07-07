# Laira  
[Laira](https://www.rcsi.com/bahrain/library) is the official AI-powered chatbot developed by the Library of RCSI Medical University of Bahrain. Laira assists users by answering questions about the library's services, tools, and access points. It uses a retrieval-augmented generation (RAG) architecture and responds based on library-curated FAQs and verified website content.

## Architecture

In production, Laira includes the following components:
- **User Interface:** Streamlit  
- **Chatbot Control:** LlamaIndex  
- **Vector Database:** ChromaDB  
- **Web Scraper:** Scrapy *(optional extension)*  
- **Usage Data:** MySQL *(optional extension)*  
- **LLM:** OpenAI's GPT API  

## Limitations of this distribution

This repository is configured to run immediately on [Streamlit Community Cloud](https://streamlit.io/cloud) or compatible Streamlit environments. For that reason, the code includes only the chatbot UI, the control logic, and integration with the OpenAI API. 

Other components such as:
- live data scraping,
- usage analytics,
- or a database ingestion pipeline

are excluded here but can be integrated for extended use. For a fully self-contained RAG example with vector generation included.

## Quick Start

To deploy your own version of Laira:

### You’ll Need:
- A GitHub account  
- A [Streamlit Community Cloud](https://streamlit.io/cloud) account  
- An OpenAI API key  

### Setup Steps:

1. **Fork this repository** to your own GitHub account.  
2. **Deploy on Streamlit Cloud**  
   - Set the main file path to `"laira.py"`  
3. **Configure Secrets**
   - Go to the app settings in Streamlit Cloud.
   - Add your OpenAI key using the interface.  
   - The app expects this key as `openai.key`.  
   - ⚠️ *Do not commit a `secrets.toml` file to your GitHub repo.*

You're now ready! Customize `laira.py` and `cbconfig.toml` to fine-tune your bot’s tone, button labels, or response rules.

## RCSI Library Links

- 🔎 [Primo Search](https://rcsibahrain.primo.exlibrisgroup.com/discovery/search?vid=973RCSIB_INST:RCSIB&lang=en)  
- 🏛 [Library Homepage](https://www.rcsi.com/bahrain/library)  
- 📚 [LibGuides](https://library.rcsi-mub.com/library/library-guides)  
- 📂 [Database A-Z List](https://library.rcsi-mub.com/az/databases)  
- 📅 [Study Room Booking](https://lrcroombookings.rcsi-mub.com/)  
- 👩‍🏫 [Librarian Appointments](https://lrcroombookings.rcsi-mub.com/appointments/)  
- ❓ [Library FAQs](https://libchat.rcsi-mub.com/)  

## More Information

For questions or collaboration, please contact the library team.