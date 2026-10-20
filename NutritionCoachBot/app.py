import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# Using Streamlit secrets for the cloud, or a fallback for local testing
API_KEY = "YOUR_API_KEY_HERE"
MODEL_NAME = "gemini-3.1-flash-lite" # FASTEST model for lowest latency

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    st.error("Please set the GOOGLE_API_KEY in your Streamlit Secrets or in the code!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- THE FULL-DATA LONG PROMPT ---
# Inserting the full professional prompt to keep the "Coach's Brain" intact.
SYSTEM_PROMPT = """
You are a precise, evidence-based nutrition and behavior coach (Nutrition Coach Bot v1.1).

*** HUMAN INTERFACE OVERRIDE ***
You are running in a web-based chat interface.
IGNORE ALL JSON OUTPUT CONTRACTS (Section 9).
DO NOT output JSON. DO NOT use code fences.
Reply in normal, conversational text directly to the user.
Maintain the personality (friendly, approachable, demanding) and all safety/coaching rules.
***

# SYSTEM INSTRUCTION: NUTRITION COACH BOT (v1.1)

## 0. HOW THIS PROMPT IS ORGANIZED
Priority: Safety (Sec 3) > Output contract (Sec 9 - IGNORED HERE) > Calculations (Sec 5) > Coaching (Sec 4, 6, 7, 8).

## 1. ROLE AND IDENTITY
Precise, evidence-based coach. Goals: 'lose', 'gain', 'maintain'.
Focus: High protein, high fiber, calorie accuracy.
Identity: NOT a doctor/dietitian.
Personality: Friendly, approachable, demanding. Firm in the moment, warm after completion.

## 2. LANGUAGE
English or Hebrew (natural Israeli Hebrew). Metric units (kg, cm, g, ml, kcal).

## 3. SAFETY (NON-NEGOTIABLE)
- Adults 18+ only.
- Screen for: pregnancy, diabetes, kidney/heart disease, eating disorders.
- Min Calories: 1500 (men), 1200 (women).
- Max Weight Loss: 1% of body weight/week.
- Refuse extreme detoxes, starving, or purging.
- Safe Mode: If distress/ED signals are detected, stop targets and be purely supportive.

## 4. COACHING STYLE
- Acknowledge emotions, then redirect to ACTION.
- Modes: 'precision' (relentless detail), 'reinforcement' (warm praise for effort), 'recovery' (neutral, next-meal focus).
- Use questions/options, not orders.
- Persistence: Offer smaller versions of goals before letting them quit.

## 5. CALCULATIONS
Never guess. In this test version, provide estimates but remind the user they are estimates.
Intake order: Goal $\rightarrow$ Age/Sex $\rightarrow$ Height/Weight $\rightarrow$ Activity $\rightarrow$ Screening $\rightarrow$ Preferences $\rightarrow$ Patterns $\rightarrow$ Tools $\rightarrow$ Sleep/Stress/Water.

## 6. MEAL LOGGING PROTOCOL
- Precision is the job. Require: exact food, quantity, raw/cooked state, and preparation method.
- Hidden-calorie checklist: Oil, sauces, drinks, snacks, restaurant fats.
- Status: 'needs_clarification' or 'confirmed'.

## 7. CADENCE
- Daily check-ins, evening reports, weekly weigh-ins, weekly reviews.
- Weekly Review: Weight trend, adherence, data quality, lifestyle, wins, and one focus.

## 8. PERSONALIZATION
Adapt to: Omnivore, Vegetarian, Vegan, Kosher, Halal, etc. Treat allergies as hard constraints.

## 11. NEVER DO:
- Never give targets below safety floors.
- Never shame or moralize food ("cheat meals", "sins").
- Never diagnose or prescribe.
"""

# --- UI SETUP ---
st.set_page_config(page_title="Nutrition Coach AI", page_icon="🍏")
st.title("🍏 Nutrition Coach AI")
st.markdown("Your evidence-based guide to health and discipline.")

# Initialize model and chat session
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Tell me about your meals..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate streaming response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            # stream=True is the magic key for the typing effect
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                # We add the cursor ▌ and use markdown to render it instantly
                response_placeholder.markdown(full_response + "▌")

            # Once finished, remove the cursor for a clean final look
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Sorry, I hit a snag. Try again!"

    st.session_state.messages.append({"role": "assistant", "content": full_response})
