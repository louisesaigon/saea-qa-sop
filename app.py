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
        "translating": "🔄 베트남어로 번역 중입니다..."
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

@st.cache_data
def parse_full_toc(pages_data):
    """Page 1~3 목차 영역에서 55개 본문 항목 + 6개 부록 항목 및 페이지 번호 정밀 파싱"""
    toc_list = []
    if len(pages_data) < 2:
        return toc_list

    # 목차가 들어있는 앞 1~3페이지 텍스트 결합
    toc_text = "\n".join(pages_data[:3])
    lines = toc_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 점선, 밑줄, 특수문자 제거 정제
        cleaned_line = re.sub(r'[\.·_]{2,}', ' ', line)
        
        # 1) 일반 항목 파싱 (예: "1. 머리말 1" 또는 "55. 교육 및 훈련 135")
        match = re.search(r'^(?:📌\s*)?(\d+[\.\)]?\s*.*?\b)\s+(\d+)$', cleaned_line)
        if match:
            title = match.group(1).strip()
            page_num = int(match.group(2))
            if page_num <= len(pages_data) and len(title) > 1:
                toc_list.append({"title": f"📌 {title}", "page": page_num})
            continue

        # 2) 부록(Appendix) 파싱 (예: "Appendix 1. ~ 140" 또는 "부록 1. ~ 140")
        app_match = re.search(r'^(Appendix|부록|App)\s*(\d+[\.\)]?\s*.*?\b)\s+(\d+)$', cleaned_line, re.IGNORECASE)
        if app_match:
            app_label = app_match.group(1)
            app_title = app_match.group(2).strip()
            page_num = int(app_match.group(3))
            if page_num <= len(pages_data):
                toc_list.append({"title": f"📑 {app_label} {app_title}", "page": page_num})

    # 파싱 결과가 적을 경우 기본 예비 추출 로직 적용
    if not toc_list:
        for i in range(min(55, len(pages_data))):
            toc_list.append({"title": f"📌 Item {i+1}", "page": i+1})

    return toc_list

@st.cache_data
def translate_to_vietnamese(text):
    if not text.strip():
        return ""
    try:
        translator = GoogleTranslator(source='auto', target='vi')
        chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n".join(translated_chunks)
    except Exception:
        return text

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
    
    # 55개 항목 + 6개 부록 파싱
    parsed_toc = parse_full_toc(pages_data) if pages_data else []
    
    st.subheader(labels["toc_header"])
    
    if parsed_toc:
        toc_titles = [item["title"] for item in parsed_toc]
        selected_title = st.radio(labels["select_item"], toc_titles)
        
        # 선택된 목차의 실제 페이지 번호 가져오기
        selected_index = toc_titles.index(selected_title)
        target_page_num = parsed_toc[selected_index]["page"]
    else:
        page_list = [f"Page {i+1}" for i in range(len(pages_data))]
        selected_page_str = st.selectbox("Page:", page_list) if page_list else "Page 1"
        target_page_num = int(selected_page_str.replace("Page ", "")) if page_list else 1
        selected_title = f"Page {target_page_num}"

# --- 2. 메인 화면 ---
st.header(f"{labels['manual_header']} ({lang_choice})")

if target_pdf and pages_data:
    page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
    
    # 지저분한 연속 점선 및 특수문자 정돈
    raw_content = pages_data[page_idx]
    cleaned_content = re.sub(r'[\.·_]{3,}', '', raw_content)
    
    # 베트남어 모드 처리
    if lang_code == "VI":
        with st.spinner(labels["translating"]):
            display_title = translate_to_vietnamese(selected_title)
            display_content = translate_to_vietnamese(cleaned_content)
    else:
        display_title = selected_title
        display_content = cleaned_content

    st.subheader(f"{display_title}")
    
    with st.container(border=True):
        if display_content.strip():
            st.markdown(display_content)
        else:
            st.warning(labels["no_text"])
            
    st.caption(f"{labels['page_info']} {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")

else:
    st.error(labels["no_file"])