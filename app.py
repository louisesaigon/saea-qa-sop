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
        "toc_header": "📚 SOP 목차 (Contents)",
        "manual_header": "📖 SAE-A QA 표준 운영 절차 (SOP)",
        "select_item": "원하시는 항목을 선택하세요:",
        "page_info": "📍 현재 위치: Page",
        "total_pages": "전체",
        "no_file": "⚠️ SOP 매뉴얼 PDF 파일을 찾을 수 없습니다.",
        "no_text": "해당 페이지에 표시할 텍스트가 없습니다.",
        "translating": "🔄 베트남어로 자동 번역 중입니다..."
    },
    "EN": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 SOP Contents",
        "manual_header": "📖 SAE-A QA Standard Operating Procedure (SOP)",
        "select_item": "Select an item to view:",
        "page_info": "📍 Current Location: Page",
        "total_pages": "Total",
        "no_file": "⚠️ Cannot find SOP manual PDF file.",
        "no_text": "No text content available on this page.",
        "translating": "🔄 Translating to Vietnamese..."
    },
    "VI": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 Mục lục SOP (Contents)",
        "manual_header": "📖 Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "select_item": "Chọn mục bạn muốn xem:",
        "page_info": "📍 Vị trí hiện tại: Trang",
        "total_pages": "Tổng số",
        "no_file": "⚠️ Không tìm thấy tệp PDF SOP.",
        "no_text": "Không có nội dung văn bản trên trang này.",
        "translating": "🔄 Đang tự động dịch sang tiếng Việt..."
    }
}

def find_sop_pdf(lang_code):
    """assets 폴더에서 한국어/영어 PDF 탐색 (베트남어 선택 시 기본 원문 사용)"""
    if not os.path.exists(assets_dir):
        return None
    files = os.listdir(assets_dir)
    # 먼저 해당 언어 파일 검색
    for file in files:
        if file.lower().endswith(".pdf") and lang_code.lower() in file.lower():
            return file
    # 베트남어 파일이 없을 경우 기본적으로 EN 또는 KO 파일 사용
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
            cleaned = re.sub(r'\.{3,}', ' ', text)
            pages_text.append(cleaned)
        return pages_text
    except Exception:
        return []

@st.cache_data
def translate_to_vietnamese(text):
    """실시간 베트남어 자동 번역 (캐싱 처리로 속도 최적화)"""
    if not text.strip():
        return ""
    try:
        # 긴 문단 분할 번역 처리
        translator = GoogleTranslator(source='auto', target='vi')
        # deep-translator 5000자 제한 방지용 슬라이싱
        chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n".join(translated_chunks)
    except Exception as e:
        return text + f"\n\n(⚠️ 번역 중 오류가 발생했습니다: {e})"

def parse_contents_from_pages(pages_data):
    toc_dict = {}
    if len(pages_data) < 2:
        return toc_dict
    contents_text = pages_data[0] + "\n" + pages_data[1]
    lines = contents_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.search(r'^(.*?)\s*(\d+)$', line)
        if match:
            title = match.group(1).strip()
            page_num = int(match.group(2))
            if len(title) > 2 and page_num <= len(pages_data):
                toc_dict[f"📌 {title}"] = page_num
    return toc_dict

# --- 1. 사이드바 ---
with st.sidebar:
    lang_choice = st.radio("🌐 언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang_choice, "KO")
    labels = UI_LABELS[lang_code]
    
    st.title(labels["title"])
    st.markdown("---")
    
    target_pdf = find_sop_pdf(lang_code)
    pages_data = load_pdf_data(target_pdf) if target_pdf else []
    toc_menu = parse_contents_from_pages(pages_data) if pages_data else {}
    
    st.subheader(labels["toc_header"])
    
    if toc_menu:
        selected_title = st.radio(labels["select_item"], list(toc_menu.keys()))
        target_page_num = toc_menu[selected_title]
    else:
        page_list = [f"Page {i+1}" for i in range(len(pages_data))]
        selected_page_str = st.selectbox("Page:", page_list) if page_list else "Page 1"
        target_page_num = int(selected_page_str.replace("Page ", "")) if page_list else 1
        selected_title = f"Page {target_page_num}"

# --- 2. 메인 화면 ---
st.header(f"{labels['manual_header']} ({lang_choice})")

if target_pdf and pages_data:
    page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
    page_content = pages_data[page_idx]
    
    # 베트남어 선택 시 실시간 번역 적용
    if lang_code == "VI":
        with st.spinner(labels["translating"]):
            display_title = translate_to_vietnamese(selected_title)
            display_content = translate_to_vietnamese(page_content)
    else:
        display_title = selected_title
        display_content = page_content

    st.subheader(display_title)
    
    with st.container(border=True):
        if display_content.strip():
            st.markdown(display_content)
        else:
            st.warning(labels["no_text"])
            
    st.caption(f"{labels['page_info']} {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")
else:
    st.error(labels["no_file"])