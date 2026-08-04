import streamlit as st
import os
import re
from pypdf import PdfReader

st.set_page_config(
    page_title="SAE-A QA SOP Manual",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")

def find_matching_pdf(manual_key, lang_code):
    if not os.path.exists(assets_dir):
        return None
    files = os.listdir(assets_dir)
    for file in files:
        if file.lower().endswith(".pdf"):
            if manual_key.lower() in file.lower() and lang_code.lower() in file.lower():
                return file
    return None

@st.cache_data
def get_pdf_pages(pdf_filename):
    pdf_path = os.path.join(assets_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        return []
    try:
        reader = PdfReader(pdf_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # 점선 등 불필요한 줄바꿈/텍스트 정돈
            cleaned_text = re.sub(r'\.{3,}', '', text)
            pages_text.append((i + 1, cleaned_text))
        return pages_text
    except Exception as e:
        return []

# --- 1. 사이드바 (왼쪽 메뉴) 구성 ---
with st.sidebar:
    st.title("📋 SAE-A QA SOP")
    
    # 언어 선택
    lang = st.radio("🌐 언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang, "KO")
    
    st.markdown("---")
    
    # 매뉴얼 종류 선택
    manual_type = st.selectbox(
        "📚 매뉴얼 선택",
        ["SOP Handbook", "Wear & Wash SOP", "Fleece SOP"]
    )
    key_map = {
        "SOP Handbook": "Handbook",
        "Wear & Wash SOP": "Wear",
        "Fleece SOP": "Fleece"
    }
    target_key = key_map.get(manual_type, "Handbook")
    
    st.markdown("---")
    
    # PDF 파일 읽기
    matched_file = find_matching_pdf(target_key, lang_code)
    pages_data = get_pdf_pages(matched_file) if matched_file else []
    
    # 목차/페이지 선택 라디오 버튼
    if pages_data:
        st.subheader("📌 목차 / 페이지 선택")
        page_options = [f"페이지 {p[0]}" for p in pages_data]
        selected_page_str = st.radio("이동할 항목을 선택하세요:", page_options)
        selected_page_num = int(selected_page_str.replace("페이지 ", ""))
    else:
        selected_page_num = None

# --- 2. 메인 화면 (선택한 매뉴얼 본문 출력) ---
st.header(f"📖 {manual_type} ({lang})")

if matched_file and pages_data:
    if selected_page_num:
        # 선택한 페이지의 내용만 표시
        page_info = pages_data[selected_page_num - 1]
        st.subheader(f"📄 Page {page_info[0]}")
        
        # 보기 깔끔하게 카드형 박스로 출력
        with st.container(border=True):
            st.markdown(page_info[1])
            
        # 전체보기 옵션 제공
        with st.expander("🔍 매뉴얼 전체 내용 한눈에 보기"):
            full_text = "\n\n---\n\n".join([f"### 📄 Page {p[0]}\n{p[1]}" for p in pages_data])
            st.markdown(full_text)
else:
    st.error(f"⚠️ `{target_key}` 관련 `{lang_code}` 매뉴얼 PDF 파일을 찾을 수 없습니다.")