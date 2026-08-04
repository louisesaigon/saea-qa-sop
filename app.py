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

# 1. 고정 목차 데이터셋 (한국어 및 영어 매핑)
SOP_TOC = [
    {"num": 1, "ko": "머리말", "en": "Introduction", "page": 1},
    {"num": 2, "ko": "QA/QC 정의", "en": "QA/QC Definition", "page": 1},
    {"num": 3, "ko": "AQL (Acceptable Quality Limit)", "en": "AQL (Acceptable Quality Limit)", "page": 2},
    {"num": 4, "ko": "Sae-A DCL (Defect Classification List)", "en": "Sae-A DCL (Defect Classification List)", "page": 4},
    {"num": 5, "ko": "원단 검사/4point System", "en": "Fabric Inspection/4point System", "page": 6},
    {"num": 6, "ko": "원단 방단", "en": "Fabric Relaxtion Management", "page": 7},
    {"num": 7, "ko": "부자재 검사", "en": "Trims & Accessories Inspection", "page": 10},
    {"num": 8, "ko": "패턴 조정 절차 및 관리", "en": "Pattern Adjustment & Management", "page": 13},
    {"num": 9, "ko": "PPM Workflow Chart", "en": "PPM Workflow Chart", "page": 16},
    {"num": 10, "ko": "PP Sample 제작", "en": "PP Sample Making", "page": 18},
    {"num": 11, "ko": "Internal PPM", "en": "Internal PPM", "page": 19},
    {"num": 12, "ko": "PPM", "en": "PPM Process", "page": 21},
    {"num": 13, "ko": "연단 및 마커 검사", "en": "Spreading & Marker Inspection", "page": 23},
    {"num": 14, "ko": "재단물 검사", "en": "Cut Panel Inspection", "page": 25},
    {"num": 15, "ko": "재완성 검사", "en": "Sub-Assembly Inspection", "page": 27},
    {"num": 16, "ko": "봉제 라인 검사", "en": "Sewing In-line Inspection", "page": 29},
    {"num": 17, "ko": "완사 검사", "en": "End-line Inspection", "page": 31},
    {"num": 18, "ko": "완성 포장 검사", "en": "Finishing & Packing Inspection", "page": 33},
    {"num": 19, "ko": "Shipment Inspection", "en": "Shipment Inspection", "page": 35},
    {"num": 20, "ko": "검사장비 및 측정도구 관리", "en": "Inspection Tools & Equipment", "page": 37},
    {"num": 21, "ko": "봉제기계/설비 표준 운영", "en": "Sewing Machine Operation Standard", "page": 39},
    {"num": 22, "ko": "바늘 관리 수칙", "en": "Needle Control Procedure", "page": 41},
    {"num": 23, "ko": "칼/이물질 관리 수칙", "en": "Sharps & Foreign Matter Control", "page": 43},
    {"num": 24, "ko": "금속검출기 운영", "en": "Needle Detector Operation", "page": 45},
    {"num": 25, "ko": "습도 및 곰팡이 관리", "en": "Humidity & Mold Control", "page": 47},
    {"num": 26, "ko": "교육 및 훈련", "en": "Training & Qualification", "page": 49}
]

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
            # 연속 점선 및 지저분한 특수문자 완벽 제거
            cleaned = re.sub(r'\.{2,}', '', text)
            cleaned = re.sub(r'·{2,}', '', cleaned)
            cleaned = re.sub(r'_{2,}', '', cleaned)
            pages_text.append(cleaned)
        return pages_text
    except Exception:
        return []

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

# --- 1. 사이드바 (왼쪽 메뉴) ---
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
    
    # 선택된 언어에 맞춰 목차 항목 생성
    toc_options = []
    for item in SOP_TOC:
        if lang_code == "KO":
            label = f"📌 {item['num']}. {item['ko']}"
        elif lang_code == "EN":
            label = f"📌 {item['num']}. {item['en']}"
        else: # 베트남어
            # 기본 영어 항목 사용 후 화면 출력 시 베트남어 번역
            label = f"📌 {item['num']}. {item['en']}"
        toc_options.append(label)
    
    selected_label = st.radio(labels["select_item"], toc_options)
    
    # 선택된 라디오 메뉴의 인덱스에서 페이지 번호 추출
    selected_index = toc_options.index(selected_label)
    selected_item_info = SOP_TOC[selected_index]
    target_page_num = selected_item_info["page"]

# --- 2. 메인 화면 ---
st.header(f"{labels['manual_header']} ({lang_choice})")

if target_pdf and pages_data:
    page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
    page_content = pages_data[page_idx]
    
    # 제목 결정
    if lang_code == "KO":
        item_title = f"{selected_item_info['num']}. {selected_item_info['ko']}"
    else:
        item_title = f"{selected_item_info['num']}. {selected_item_info['en']}"
    
    # 베트남어 모드 시 실시간 번역
    if lang_code == "VI":
        with st.spinner(labels["translating"]):
            display_title = translate_to_vietnamese(item_title)
            display_content = translate_to_vietnamese(page_content)
    else:
        display_title = item_title
        display_content = page_content

    st.subheader(f"📄 {display_title}")
    
    with st.container(border=True):
        if display_content.strip():
            st.markdown(display_content)
        else:
            st.warning(labels["no_text"])
            
    st.caption(f"{labels['page_info']} {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")
else:
    st.error(labels["no_file"])