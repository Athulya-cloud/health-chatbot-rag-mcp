import streamlit as st
import mysql.connector
import json
import numpy as np
from google import genai
from google.genai import types # Import types for config
from my_secrets import DB_CONFIG, GOOGLE_KEY

st.set_page_config(page_title="Dr. AI Assistant", layout="wide")
st.title("🏥 EMR Copilot (Final Demo Version)")

try:
    client = genai.Client(api_key=GOOGLE_KEY)
except Exception as e:
    st.error(f"❌ Setup Error: {e}")

# Sidebar
with st.sidebar:
    st.header("System Status")
    mode_display = st.empty() # Placeholder for mode status
    if st.button("Reconnect DB"):
        conn = mysql.connector.connect(**DB_CONFIG)
        st.success("✅ Connected")
        conn.close()

query = st.text_input("Ask a question:")

if query:
    with st.spinner("🧠 Analyzing..."):
        try:
            # 1. Vectorize
            vec_resp = client.models.embed_content(
                model="models/text-embedding-004",
                contents=query
            )
            q_vec = np.array(vec_resp.embeddings[0].values)

            # 2. Search DB
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id, story_text, vector_json FROM patient_vectors")
            rows = cursor.fetchall()
            conn.close()

            # 3. Rank Results
            results = []
            for pid, story, v_json in rows:
                p_vec = np.array(json.loads(v_json))
                sim = np.dot(q_vec, p_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(p_vec))
                results.append((sim, pid, story))
            results.sort(key=lambda x: x[0], reverse=True)

            # 4. DECISION ENGINE (RAG vs MCP)
            # If asking to "list" or match score is high (>0.45) -> Use Patient Data
            is_list_cmd = any(w in query.lower() for w in ["list", "show", "all"])
            top_score = results[0][0] if results else 0
            
            if is_list_cmd or top_score > 0.45:
                mode_display.success("🟢 Mode: Hospital Database")
                context = ""
                count = 0
                for score, pid, story in results:
                    # Lower threshold for "list" commands
                    thresh = 0.35 if is_list_cmd else 0.45
                    if score > thresh:
                        context += f"\n--- PATIENT {pid} ---\n{story}\n"
                        with st.expander(f"View Record: {pid} (Match: {score:.2f})"):
                            st.write(story)
                        count += 1
                        if count >= 5: break
                
                if context:
                    prompt = f"You are a hospital admin. Answer based ONLY on these records:\n{context}\nUser: {query}"
                else:
                    prompt = f"User asked: {query}. Say no matching patients found in database."

            else:
                mode_display.warning("🟠 Mode: General Medical Knowledge")
                st.info("No specific patient found. Answering with general medical knowledge.")
                prompt = f"You are a helpful doctor. Explain this medical concept generally:\n{query}"

            # 5. Generate with LOW TEMPERATURE
            safe_config = types.GenerateContentConfig(
                temperature=0.0, # Strict
                top_p=0.8,
                top_k=40
            )
            
            resp = client.models.generate_content(
                model="models/gemini-flash-latest",
                contents=prompt,
                config=safe_config
            )
            st.markdown("### 🤖 Dr. AI Answer:")
            st.write(resp.text)

        except Exception as e:
            st.error(f"Error: {e}")