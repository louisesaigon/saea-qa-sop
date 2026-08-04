import streamlit as st
import os
import re
from pypdf import PdfReader
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="SAE-A QA SOP Manual",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")

UI_LABELS = {
    "KO": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 SOP 목차 & 페이지 이동",
        "manual_header": "📖 SAE-A QA 표준 운영 절차 (SOP)",
        "select_item": "원하시는 항목 또는 페이지를 선택하세요:",
        "page_info": "📍 현재 위치: Page",
        "total_pages": "전체",
        "no_file": "⚠️ SOP 매뉴얼 PDF 파일을 찾을 수 없습니다.",
        "no_text": "해당 페이지에 표시할 텍스트가 없습니다.",
        "translating": "🔄 베트남어로 번역 중입니다..."
    },
    "EN": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 SOP Navigation",
        "manual_header": "📖 SAE-A QA Standard Operating Procedure (SOP)",
        "select_item": "Select item or page to view:",
        "page_info": "📍 Current Location: Page",
        "total_pages": "Total",
        "no_file": "⚠️ Cannot find SOP manual PDF file.",
        "no_text": "No text content available on this page.",
        "translating": "🔄 Translating to Vietnamese..."
    },
    "VI": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 Điều hướng SOP",
        "manual_header": "📖 Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "select_item": "Chọn mục hoặc trang bạn muốn xem:",
        "page_info": "📍 Vị trí hiện tại: Trang",
        "total_pages": "Tổng số",
        "no_file": "⚠️ Không tìm thấy tệp PDF SOP.",
        "no_text": "Không có nội dung văn bản trên trang này.",
        "translating": "🔄 Đang tự động dịch sang tiếng Việt..."
    }
}

def find_sop_pdf(lang_code):
    if not os.path.exists(assets_dir):
        return None
    files = os.listdir(assets_dir)
    for file in files:
        if file.lower().endswith(".pdf") and lang_code.lower() in file.lower():
            return file
    pdf_files = [f for f in files if f.lower().endswith(".pdf")]
    return pdf_files[0] if pdf_files else None

@st.cache_data
def load_pdf_data(pdf_filename):
    pdf_path = os.path.join(assets_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        return []
    try:
        reader = PdfReader(pdf_path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
        return pages_text
    except Exception:
        return []

def format_sop_text(text):
    """지저분하게 뭉친 텍스트를 단락별로 시각화하여 가독성을 극대화하는 함수"""
    if not text:
        return ""
    
    # 1. 특수 점선/특수문자 정리
    cleaned = re.sub(r'[\.·_]{3,}', '', text)
    
    # 2. 핵심 키워드 기준 줄바꿈 및 강조 처리
    keywords = [
        "Doc. No.", "Version #", "Date Created", "Date Revised", 
        "Prepared by", "Approved by", "Department", "Note :", "Objective",
        "Description of Activities", "Section/", "Responsible Activities", 
        "Documentation", "Date Validation", "Minimum Requirement"
    ]
    
    for kw in keywords:
        cleaned = cleaned.replace(kw, f"\n\n**{kw}**")
    
    # 3. 문장 끝 마침표 후 줄바꿈 삽입 (단락 형성)
    cleaned = re.sub(r'(\. )', '.\n\n', cleaned)
    
    # 4. 불필요한 연속 다중 공백 및 줄바꿈 정리
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()

@st.cache_data
def translate_to_vietnamese(text):
    if not text.strip():
        return ""
    try:
        translator = GoogleTranslator(source='auto', target='vi')
        chunks = [text[i:i+2500] for i in range(0, len(text), 2500)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n".join(translated_chunks)
    except Exception:
        return text

# --- 1. 사이드바 (메뉴 및 페이지 이동) ---
with st.sidebar:
    lang_choice = st.radio("🌐 언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang_choice, "KO")
    labels = UI_LABELS[lang_code]
    
    st.title(labels["title"])
    st.markdown("---")
    
    target_pdf = find_sop_pdf(lang_code)
    pages_data = load_pdf_data(target_pdf) if target_pdf else []
    
    st.subheader(labels["toc_header"])
    
    if pages_data:
        # 직관적인 페이지 이동 셀렉트박스 (1장~145장)
        total_p = len(pages_data)
        page_options = [f"📌 Page {i+1}" for i in range(total_p)]
        
        selected_page_str = st.selectbox(
            labels["select_item"], 
            page_options,
            index=0
        )
        target_page_num = int(selected_page_str.replace("📌 Page ", ""))
    else:
        target_page_num = 1

# --- 2. 메인 화면 (가독성 높은 텍스트 뷰) ---
st.header(f"{labels['manual_header']} ({lang_choice})")

if target_pdf and pages_data:
    page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
    raw_content = pages_data[page_idx]
    
    # 단락 구분 및 서식 가독성 개선
    formatted_content = format_sop_text(raw_content)
    
    # 베트남어 선택 시 실시간 번역
    if lang_code == "VI":
        with st.spinner(labels["translating"]):
            display_content = translate_to_vietnamese(formatted_content)
    else:
        display_content = formatted_content

    st.subheader(f"📄 Page {page_idx + 1}")
    
    # 모바일 카드 뷰 서식
    with st.container(border=True):
        if display_content.strip():
            st.markdown(display_content)
        else:
            st.warning(labels["no_text"])
            
    st.caption(f"{labels['page_info']} {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")

else:
    st.error(labels["no_file"])