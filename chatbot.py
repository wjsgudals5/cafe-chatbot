# Cafe FAQ Chatbot (Streamlit) - Demo
# Requirements:
#   pip install streamlit openai
#
# How to run:
#   1) export OPENAI_API_KEY="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"
#      (Windows PowerShell: $env:OPENAI_API_KEY = "your_api_key")
#   2) streamlit run Cafe_FAQ_Chatbot_Streamlit.py
#
# This single-file demo provides a lightweight chat UI and uses OpenAI's chat completion
# API to answer questions about a cafe. If OPENAI_API_KEY is not set it will fall back
# to a simple rule-based responder using the embedded cafe_data.

import os
import json
import streamlit as st
try:
    import openai
except Exception:
    openai = None

# -----------------------------
# Sample cafe data (editable)
# -----------------------------
cafe_data = {
    "name": "Sunny Bean Cafe",
    "address": "123 Seoul-ro, Gangnam-gu",
    "hours": "Mon-Sat 08:00-21:00, Sun 09:00-18:00",
    "menu": {
        "Americano": "3,500원",
        "Caffe Latte": "4,500원",
        "Iced Americano": "4,000원",
        "Croissant": "3,000원"
    },
    "delivery": "배달은 쿠팡이츠/배민을 통해 가능, 기본 배달비 2,500원",
    "reservations": "예약은 전화(010-1234-5678) 또는 카톡으로 가능",
    "refund_policy": "상품 수령 후 7일 이내 변심 환불 불가, 제품 하자 시 교환/환불 가능",
    "notes": "반려동물 동반 불가, 룸 없음, 매장 내 좌석 20석"
}

# -----------------------------
# Helper functions
# -----------------------------

def rule_based_answer(user_text: str) -> str:
    # very small rule-based fallback that searches cafe_data
    txt = user_text.lower()
    if any(k in txt for k in ["메뉴", "가격", "얼마", "아메리카노", "라떼"]):
        items = "\n".join([f"{k} - {v}" for k, v in cafe_data["menu"].items()])
        return f"메뉴와 가격입니다:\n{items}"
    if any(k in txt for k in ["영업", "시간", "오픈", "닫"]):
        return f"영업시간은 {cafe_data['hours']} 입니다."
    if any(k in txt for k in ["위치", "주소", "어디"]):
        return f"주소: {cafe_data['address']}"
    if any(k in txt for k in ["배달", "배달비"]):
        return f"배달 안내: {cafe_data['delivery']}"
    if any(k in txt for k in ["예약", "예약방법"]):
        return f"예약 안내: {cafe_data['reservations']}"
    if any(k in txt for k in ["환불", "교환", "환불정책"]):
        return f"환불/교환 정책: {cafe_data['refund_policy']}"
    # default
    return "죄송합니다, 해당 내용은 정확히 모르겠지만 도와드릴 수 있는 다른 질문이 있나요?"


def call_openai_chat(messages: list, model: str = "gpt-4o-mini") -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or openai is None:
        return None
    openai.api_key = api_key
    try:
        # Using ChatCompletion for compatibility; adjust model name if needed
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"(OpenAI API error) {e}"

# -----------------------------
# System prompt guiding the assistant
# -----------------------------
system_prompt = f"You are a friendly, concise customer support assistant for a small cafe. Use the data provided to answer customer questions precisely. If the user asks something not in the data, offer a polite suggestion (e.g., '전화로 문의해주세요' or '매장 방문을 권장합니다'). Data: {json.dumps(cafe_data, ensure_ascii=False)}"

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Cafe FAQ Chatbot - Demo", layout="centered")
st.title("☕ Sunny Bean Cafe — 고객응대 AI 데모")
st.markdown("간단한 질문을 입력하면 카페 전용 AI가 답변합니다. (OpenAI API 키가 설정되어 있으면 고급 응답 사용) ")

# Sidebar: editable cafe info & API key
with st.sidebar.expander("가게 정보 (수정 가능)"):
    cafe_name = st.text_input("가게 이름", value=cafe_data["name"]) or cafe_data["name"]
    cafe_address = st.text_input("주소", value=cafe_data["address"]) or cafe_data["address"]
    cafe_hours = st.text_input("영업시간", value=cafe_data["hours"]) or cafe_data["hours"]
    menu_text = st.text_area("메뉴 (한 줄에: 이름 - 가격)", value="\n".join([f"{k} - {v}" for k, v in cafe_data["menu"].items()]))
    if st.button("가게 정보 적용"):
        # update the in-memory data
        cafe_data["name"] = cafe_name
        cafe_data["address"] = cafe_address
        cafe_data["hours"] = cafe_hours
        # parse menu_text
        new_menu = {}
        for line in menu_text.splitlines():
            if "-" in line:
                name, price = line.split("-", 1)
                new_menu[name.strip()] = price.strip()
        if new_menu:
            cafe_data["menu"] = new_menu
        st.success("가게 정보가 업데이트되었습니다.")

api_key_hint = st.sidebar.text_input("(선택) OPENAI API Key (앱용 테스트)", value="", type="password")
if api_key_hint:
    os.environ["OPENAI_API_KEY"] = api_key_hint

# Chat area
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([4,1])
with col1:
    user_input = st.text_input("질문을 입력하세요...", key="input_box")
with col2:
    send = st.button("보내기")

if send and user_input:
    st.session_state.history.append({"role":"user","content":user_input})
    # Try OpenAI first
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    openai_reply = call_openai_chat(messages)
    if openai_reply and not openai_reply.startswith("(OpenAI API error)"):
        assistant_text = openai_reply
    else:
        # fallback
        assistant_text = rule_based_answer(user_input)
    st.session_state.history.append({"role":"assistant","content":assistant_text})

# Display chat history
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**CafeBot:** {msg['content']}")

# Quick action buttons
st.markdown("---")
st.markdown("### 데모 빠른 예시")
colA, colB, colC = st.columns(3)
if colA.button("메뉴 알려줘"):
    st.session_state.history.append({"role":"user","content":"메뉴 알려줘"})
    st.session_state.history.append({"role":"assistant","content": rule_based_answer("메뉴 알려줘")})
if colB.button("영업시간"):
    st.session_state.history.append({"role":"user","content":"영업시간이 어떻게 되나요?"})
    st.session_state.history.append({"role":"assistant","content": rule_based_answer("영업시간")})
if colC.button("배달 가능한가요?"):
    st.session_state.history.append({"role":"user","content":"배달 가능한가요?"})
    st.session_state.history.append({"role":"assistant","content": rule_based_answer("배달 가능한가요?")})

st.caption("이 데모는 상용 챗봇의 간단한 프로토타입입니다. 배포용으로 사용하기 전에 보안, 인증, 카카오/네이버톡톡 연동, 로깅 등을 추가하세요.")
