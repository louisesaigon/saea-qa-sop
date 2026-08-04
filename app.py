import streamlit as st
import os
from pypdf import PdfReader

st.set_page_config(
    page_title="SAE-A QA SOP Manual",
    page_icon="📋",
    layout="centered"
)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")

# assets 폴더에서 조건에 맞는 PDF 파일 찾아내기
def find_matching_pdf(manual_key, lang_code):
    if not os.path.exists(assets_dir):
        return None
    
    files = os.listdir(assets_dir)
    for file in files:
        if file.lower().endswith(".pdf"):
            # 매뉴얼 키워드 및 언어 코드 일치 여부 확인
            if manual_key.lower() in file.lower() and lang_code.lower() in file.lower():
                return file
    return None

@st.cache_data
def extract_text_from_pdf(pdf_filename):
    pdf_path = os.path.join(assets_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        return None
    
    try:
        reader = PdfReader(pdf_path)
        extracted_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(f"### 📄 Page {i+1}\n\n" + text)
        return "\n\n---\n\n".join(extracted_text)
    except Exception as e:
        return f"파일을 읽는 중 오류가 발생했습니다: {e}"

# --- 헤더 ---
st.title("📋 SAE-A QA SOP")
st.caption("모바일 최적화 텍스트 매뉴얼")

# --- 언어 선택 ---
lang = st.radio("🌐 언어 선택 / Select Language", ["한국어", "English", "Tiếng Việt"], horizontal=True)
lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
lang_code = lang_map.get(lang, "KO")

# --- 매뉴얼 선택 ---
manual_type = st.selectbox(
    "📚 매뉴얼 종류 선택",
    ["SOP Handbook", "Wear & Wash SOP", "Fleece SOP"]
)

# 매뉴얼 키워드 매핑
key_map = {
    "SOP Handbook": "Handbook",
    "Wear & Wash SOP": "Wear",
    "Fleece SOP": "Fleece"
}
target_key = key_map.get(manual_type, "Handbook")

st.markdown("---")

# --- 파일 검색 및 출력 ---
st.subheader(f"📖 {manual_type} ({lang})")

matched_file = find_matching_pdf(target_key, lang_code)

if matched_file:
    with st.spinner("매뉴얼 텍스트를 불러오는 중입니다..."):
        pdf_text = extract_text_from_pdf(matched_file)
    
    if pdf_text:
        st.markdown(pdf_text)
    else:
        st.warning("PDF 파일에서 텍스트를 추출하지 못했습니다.")
else:
    st.error(f"⚠️ `{target_key}` 관련 `{lang_code}` 매뉴얼 PDF 파일을 `assets` 폴더에서 찾을 수 없습니다.")