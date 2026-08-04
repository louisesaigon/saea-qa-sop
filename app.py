import streamlit as st
import os
import re
from pypdf import PdfReader
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="SAE-A QA SOP",
    layout="wide",
    initial_sidebar_state="expanded"
)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")

UI_LABELS = {
    "KO": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP 목차",
        "manual_header": "SAE-A QA 표준 운영 절차 (SOP)",
        "select_item": "열람할 목차 항목을 선택하십시오:",
        "page_info": "페이지 위치",
        "total_pages": "전체",
        "no_file": "해당 언어의 SOP 매뉴얼 PDF 파일을 찾을 수 없습니다.",
        "no_text": "해당 페이지에 표시할 텍스트 내용이 없습니다.",
        "translating": "베트남어 자동 번역을 진행 중입니다..."
    },
    "EN": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP Table of Contents",
        "manual_header": "SAE-A QA Standard Operating Procedure (SOP)",
        "select_item": "Select a section from Table of Contents:",
        "page_info": "Reference Page",
        "total_pages": "Total",
        "no_file": "Cannot find SOP manual PDF file.",
        "no_text": "No text content available on this page.",
        "translating": "Translating to Vietnamese..."
    },
    "VI": {
        "title": "Hệ thống SAE-A QA SOP",
        "toc_header": "Mục lục SOP",
        "manual_header": "Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "select_item": "Chọn mục bạn muốn xem:",
        "page_info": "Trang tham khảo",
        "total_pages": "Tổng số",
        "no_file": "Không tìm thấy tệp PDF SOP.",
        "no_text": "Không có nội dung văn bản trên trang này.",
        "translating": "Đang tự động dịch sang tiếng Việt..."
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
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return pages_text
    except Exception:
        return []

@st.cache_data
def parse_pdf_dynamic_toc(pages_data):
    toc_list = []
    if not pages_data:
        return toc_list

    total_pages = len(pages_data)
    contents_text = "\n".join(pages_data[:min(3, total_pages)])
    lines = contents_text.split('\n')
    
    for line in lines:
        line_clean = re.sub(r'[\.·_]{2,}', ' ', line.strip())
        match = re.search(r'^(.*?)\s+(\d+)$', line_clean)
        if match:
            title = match.group(1).strip()
            page_num = int(match.group(2))
            if len(title) > 2 and 1 <= page_num <= total_pages:
                toc_list.append({"title": title, "page": page_num})

    if not toc_list:
        for idx, page_text in enumerate(pages_data):
            p_num = idx + 1
            first_line = page_text.strip().split('\n')[0] if page_text.strip() else f"Page {p_num}"
            first_line = re.sub(r'[\.·_]{2,}', '', first_line)[:40]
            toc_list.append({"title": f"P.{p_num} {first_line}", "page": p_num})

    return toc_list

def clean_and_format_text(raw_text):
    if not raw_text.strip():
        return ""
    
    cleaned = re.sub(r'[\.·_]{2,}', '', raw_text)
    lines = cleaned.split('\n')
    formatted_paragraphs = []
    current_para = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            if current_para:
                formatted_paragraphs.append(" ".join(current_para))
                current_para = []
            continue
        
        if any(line_str.startswith(kw) for kw in ["Doc. No.", "Version", "Date", "Prepared", "Approved", "Department", "Note", "Objective"]):
            if current_para:
                formatted_paragraphs.append(" ".join(current_para))
                current_para = []
            formatted_paragraphs.append(f"**{line_str}**")
        else:
            current_para.append(line_str)
            
    if current_para:
        formatted_paragraphs.append(" ".join(current_para))
        
    return "\n\n".join(formatted_paragraphs)

@st.cache_data
def translate_to_vietnamese(text):
    if not text.strip():
        return ""
    try:
        translator = GoogleTranslator(source='auto', target='vi')
        chunks = [text[i:i+2500] for i in range(0, len(text), 2500)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n\n".join(translated_chunks)
    except Exception:
        return text

# --- 1. 사이드바 (설정 및 메뉴) ---
with st.sidebar:
    lang_choice = st.radio("언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang_choice, "KO")
    labels = UI_LABELS[lang_code]
    
    st.markdown(f"### {labels['title']}")
    st.markdown("---")
    
    target_pdf = find_sop_pdf(lang_code)
    pages_data = load_pdf_data(target_pdf) if target_pdf else []
    
    dynamic_toc = parse_pdf_dynamic_toc(pages_data)
    
    st.markdown(f"**{labels['toc_header']}**")
    
    if dynamic_toc:
        toc_titles = [item["title"] for item in dynamic_toc]
        selected_title = st.selectbox(labels["select_item"], toc_titles, index=0)
        selected_index = toc_titles.index(selected_title)
        target_page_num = dynamic_toc[selected_index]["page"]
    else:
        target_page_num = 1
        selected_title = "SOP Manual"

# --- 2. 메인 화면 ---
# 타이틀 크기를 모바일에 맞추어 작은 서식(st.caption / st.markdown)으로 정제
st.caption(f"{labels['manual_header']} ({lang_choice})")

if target_pdf and pages_data:
    page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
    raw_content = pages_data[page_idx]
    
    formatted_content = clean_and_format_text(raw_content)
    
    if lang_code == "VI":
        with st.spinner(labels["translating"]):
            display_title = translate_to_vietnamese(selected_title)
            display_content = translate_to_vietnamese(formatted_content)
    else:
        display_title = selected_title
        display_content = formatted_content

    # 섹션 제목 출력
    st.markdown(f"#### {display_title}")
    
    with st.container(border=True):
        if display_content.strip():
            st.markdown(display_content)
        else:
            st.warning(labels["no_text"])
            
    st.caption(f"{labels['page_info']}: {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")

else:
    st.error(labels["no_file"])