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

# 1. 완벽 고정된 55개 본문 항목 + 6개 부록(Appendix) 목차 데이터
SOP_TOC = [
    # --- 본문 55개 항목 ---
    {"num": "1", "ko": "머리말", "en": "Introduction", "page": 1},
    {"num": "2", "ko": "QA/QC 정의", "en": "QA/QC Definition", "page": 1},
    {"num": "3", "ko": "AQL (Acceptable Quality Limit)", "en": "AQL (Acceptable Quality Limit)", "page": 2},
    {"num": "4", "ko": "Sae-A DCL (Defect Classification List)", "en": "Sae-A DCL (Defect Classification List)", "page": 4},
    {"num": "5", "ko": "원단 검사/4point System", "en": "Fabric Inspection / 4point System", "page": 6},
    {"num": "6", "ko": "원단 방단", "en": "Fabric Relaxation Management", "page": 7},
    {"num": "7", "ko": "부자재 검사", "en": "Trims & Accessories Inspection", "page": 10},
    {"num": "8", "ko": "패턴 조정 절차 및 관리", "en": "Pattern Adjustment & Management", "page": 13},
    {"num": "9", "ko": "PPM Workflow Chart", "en": "PPM Workflow Chart", "page": 16},
    {"num": "10", "ko": "PP Sample 제작", "en": "PP Sample Making", "page": 18},
    {"num": "11", "ko": "Internal PPM", "en": "Internal PPM", "page": 19},
    {"num": "12", "ko": "PPM", "en": "PPM Process", "page": 21},
    {"num": "13", "ko": "연단 및 마커 검사", "en": "Spreading & Marker Inspection", "page": 23},
    {"num": "14", "ko": "재단물 검사", "en": "Cut Panel Inspection", "page": 25},
    {"num": "15", "ko": "재완성 검사", "en": "Sub-Assembly Inspection", "page": 27},
    {"num": "16", "ko": "봉제 라인 검사", "en": "Sewing In-line Inspection", "page": 29},
    {"num": "17", "ko": "완사 검사", "en": "End-line Inspection", "page": 31},
    {"num": "18", "ko": "완성 포장 검사", "en": "Finishing & Packing Inspection", "page": 33},
    {"num": "19", "ko": "Shipment Inspection", "en": "Shipment Inspection", "page": 35},
    {"num": "20", "ko": "검사장비 및 측정도구 관리", "en": "Inspection Tools & Equipment Management", "page": 37},
    {"num": "21", "ko": "봉제기계/설비 표준 운영", "en": "Sewing Machine Operation Standard", "page": 39},
    {"num": "22", "ko": "바늘 관리 수칙", "en": "Needle Control Procedure", "page": 41},
    {"num": "23", "ko": "칼/이물질 관리 수칙", "en": "Sharps & Foreign Matter Control", "page": 43},
    {"num": "24", "ko": "금속검출기 운영", "en": "Needle Detector Operation", "page": 45},
    {"num": "25", "ko": "습도 및 곰팡이 관리", "en": "Humidity & Mold Control", "page": 47},
    {"num": "26", "ko": "교육 및 훈련", "en": "Training & Qualification", "page": 49},
    {"num": "27", "ko": "공정 품질 감사 (Auditing)", "en": "Process Quality Audit", "page": 51},
    {"num": "28", "ko": "부적합품 관리 및 CAPA", "en": "Non-conforming Product & CAPA", "page": 53},
    {"num": "29", "ko": "고객 클레임 대응 절차", "en": "Customer Claim Handling", "page": 55},
    {"num": "30", "ko": "실험실 및 테스트 표준", "en": "Lab & Testing Standards", "page": 57},
    {"num": "31", "ko": "세탁 및 수축률 관리", "en": "Washing & Shrinkage Control", "page": 59},
    {"num": "32", "ko": "색상 및 이염 관리", "en": "Color & Bleeding Management", "page": 61},
    {"num": "33", "ko": "원단 수축 시험 가이드", "en": "Fabric Shrinkage Test Guide", "page": 63},
    {"num": "34", "ko": "봉제 조시 및 땀수 관리", "en": "Tension & SPI Management", "page": 65},
    {"num": "35", "ko": "샘플링 검사 규정", "en": "Sampling Inspection Rules", "page": 67},
    {"num": "36", "ko": "품질 기록 및 보관", "en": "Quality Record Management", "page": 69},
    {"num": "37", "ko": "협력업체 품질 관리", "en": "Subcontractor Quality Control", "page": 71},
    {"num": "38", "ko": "최종 검사 승인 절차", "en": "Final Inspection Approval", "page": 73},
    {"num": "39", "ko": "출하 전 서류 확인", "en": "Pre-shipment Doc Verification", "page": 75},
    {"num": "40", "ko": "창고 입출고 검사", "en": "Warehouse In/Out Inspection", "page": 77},
    {"num": "41", "ko": "컨테이너 적재 검사", "en": "Container Loading Inspection", "page": 79},
    {"num": "42", "ko": "안전 및 환경 품질", "en": "Safety & Environmental Quality", "page": 81},
    {"num": "43", "ko": "유해물질 관리 (RSL)", "en": "Restricted Substances List (RSL)", "page": 83},
    {"num": "44", "ko": "작업장 5S 및 환경", "en": "Workplace 5S & Environment", "page": 85},
    {"num": "45", "ko": "조명 및 감수 환경", "en": "Lighting & Inspection Environment", "page": 87},
    {"num": "46", "ko": "통계적 품질 관리 (SQC)", "en": "Statistical Quality Control", "page": 89},
    {"num": "47", "ko": "주요 품질 지표 (KPI)", "en": "Key Quality Metrics (KPI)", "page": 91},
    {"num": "48", "ko": "자체 평가 및 내부 감사", "en": "Self-Assessment & Internal Audit", "page": 93},
    {"num": "49", "ko": "경영진 품질 검토", "en": "Management Quality Review", "page": 95},
    {"num": "50", "ko": "연간 품질 계획 수립", "en": "Annual Quality Plan", "page": 97},
    {"num": "51", "ko": "품질 매뉴얼 개정 절차", "en": "SOP Revision Procedure", "page": 99},
    {"num": "52", "ko": "QA 팀 역할 및 책임", "en": "QA Team Roles & Responsibilities", "page": 101},
    {"num": "53", "ko": "바이어별 특별 요구사항", "en": "Buyer Special Requirements", "page": 103},
    {"num": "54", "ko": "품질 비상 대응 체계", "en": "Quality Emergency Response", "page": 105},
    {"num": "55", "ko": "SOP 총칙 및 적용 범위", "en": "General Provisions & Scope", "page": 107},
    # --- 부록 6개 (Appendix) ---
    {"num": "App 1", "ko": "부록 1. 결함 분류 기준표 (DCL Detail)", "en": "Appendix 1. Defect Classification Detail", "page": 110},
    {"num": "App 2", "ko": "부록 2. AQL 샘플링 검사표", "en": "Appendix 2. AQL Sampling Table", "page": 115},
    {"num": "App 3", "ko": "부록 3. PPM 점검 체크리스트", "en": "Appendix 3. PPM Inspection Checklist", "page": 120},
    {"num": "App 4", "ko": "부록 4. 표준 품질 보고서 양식", "en": "Appendix 4. Standard Quality Report Form", "page": 125},
    {"num": "App 5", "ko": "부록 5. 봉제 불량 유형 및 조치 가이드", "en": "Appendix 5. Sewing Defect Guide", "page": 130},
    {"num": "App 6", "ko": "부록 6. QA 용어 및 약어 정의집", "en": "Appendix 6. QA Glossary & Abbreviations", "page": 135}
]

UI_LABELS = {
    "KO": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 SOP 목차 (Contents)",
        "manual_header": "📖 SAE-A QA 표준 운영 절차 (SOP)",
        "select_item": "목차 항목을 선택하세요 (총 61개):",
        "page_info": "📍 Reference Page",
        "total_pages": "전체",
        "no_file": "⚠️ SOP 매뉴얼 PDF 파일을 찾을 수 없습니다.",
        "no_text": "해당 페이지에 표시할 텍스트가 없습니다.",
        "translating": "🔄 베트남어로 번역 중입니다..."
    },
    "EN": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 SOP Contents",
        "manual_header": "📖 SAE-A QA Standard Operating Procedure (SOP)",
        "select_item": "Select a section (Total 61 Items):",
        "page_info": "📍 Reference Page",
        "total_pages": "Total",
        "no_file": "⚠️ Cannot find SOP manual PDF file.",
        "no_text": "No text content available on this page.",
        "translating": "🔄 Translating to Vietnamese..."
    },
    "VI": {
        "title": "📋 SAE-A QA SOP",
        "toc_header": "📚 Mục lục SOP (Contents)",
        "manual_header": "📖 Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "select_item": "Chọn mục bạn muốn xem (Tổng 61 mục):",
        "page_info": "📍 Trang tham khảo",
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

def clean_and_format_text(raw_text):
    """지저분한 문장 분부 및 불필요한 줄바꿈을 정돈하여 깔끔한 단락으로 만듦"""
    if not raw_text.strip():
        return ""
    
    # 점선, 밑줄 제거
    cleaned = re.sub(r'[\.·_]{2,}', '', raw_text)
    
    # 억지로 잘린 문장 줄바꿈 복원
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
        
        # 주요 섹션 항목은 볼드체 및 줄바꿈 처리
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

# --- 1. 사이드바 (메뉴 선택) ---
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
    
    # 선택 언어별 라벨 목록 구성
    toc_labels = []
    for item in SOP_TOC:
        if lang_code == "KO":
            title_text = item["ko"]
        else:
            title_text = item["en"]
            
        if item["num"].startswith("App"):
            toc_labels.append(f"📑 {title_text}")
        else:
            toc_labels.append(f"📌 {item['num']}. {title_text}")
            
    selected_label = st.selectbox(labels["select_item"], toc_labels, index=0)
    selected_index = toc_labels.index(selected_label)
    selected_item = SOP_TOC[selected_index]
    target_page_num = selected_item["page"]

# --- 2. 메인 화면 ---
st.header(f"{labels['manual_header']} ({lang_choice})")

if target_pdf and pages_data:
    page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
    raw_content = pages_data[page_idx]
    
    # 자연스러운 문단 구조로 본문 정돈
    formatted_content = clean_and_format_text(raw_content)
    
    # 선택된 항목 제목
    if lang_code == "KO":
        item_title_str = selected_item["ko"]
    else:
        item_title_str = selected_item["en"]
        
    # 베트남어 처리
    if lang_code == "VI":
        with st.spinner(labels["translating"]):
            display_title = translate_to_vietnamese(item_title_str)
            display_content = translate_to_vietnamese(formatted_content)
    else:
        display_title = item_title_str
        display_content = formatted_content

    # 매뉴얼 제목 출력 (크게 지저분한 Page 1 표시 제거)
    st.subheader(f"📖 {display_title}")
    
    with st.container(border=True):
        if display_content.strip():
            st.markdown(display_content)
        else:
            st.warning(labels["no_text"])
            
    st.caption(f"{labels['page_info']}: {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")

else:
    st.error(labels["no_file"])