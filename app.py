import streamlit as st
import os
import re
from pypdf import PdfReader
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="SAE-A QA SOP System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 라디오 버튼 텍스트 줄바꿈 및 간격 최적화 CSS
st.markdown("""
    <style>
    .stRadio > div {
        gap: 6px;
    }
    .stRadio label {
        white-space: normal !important;
        word-break: break-word !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    </style>
""", unsafe_allow_html=True)

assets_dir = os.path.join(os.path.dirname(__file__), "assets")

# --- 이미지 소스 기반 100% 일치 목차 목록 (1~45번 + 부록 1~5번) ---
SOP_TOC = [
    # 1~14번
    {"num": "1", "title": "1. 머리말", "page": 1},
    {"num": "2", "title": "2. QA/QC 정의", "page": 1},
    {"num": "3", "title": "3. AQL (Acceptable Quality Limit)", "page": 2},
    {"num": "4", "title": "4. Sae-A DCL (Defect Classification List)", "page": 4},
    {"num": "5", "title": "5. 원단 검사/4point System", "page": 6},
    {"num": "6", "title": "6. 원단 방단", "page": 7},
    {"num": "7", "title": "7. 부자재 검사", "page": 10},
    {"num": "8", "title": "8. 패턴 조정 절차 및 관리", "page": 13},
    {"num": "9", "title": "9. PPM Workflow Chart", "page": 16},
    {"num": "10", "title": "10. PP Sample 제작", "page": 18},
    {"num": "11", "title": "11. Internal PPM", "page": 19},
    {"num": "12", "title": "12. PPM", "page": 21},
    {"num": "13", "title": "13. 연단 및 마커 검사", "page": 23},
    {"num": "14", "title": "14. 재단물 검사", "page": 25},
    # 15~29번 (이미지 기준 정확 수정)
    {"num": "15", "title": "15. 자수/프린트 검사", "page": 27},
    {"num": "16", "title": "16. Pilot Run 검사", "page": 29},
    {"num": "17", "title": "17. Wear & Wash Test", "page": 31},
    {"num": "18", "title": "18. 1st Output 검사", "page": 33},
    {"num": "19", "title": "19. In-Process 검사", "page": 35},
    {"num": "20", "title": "20. Seam allowance 모니터링", "page": 37},
    {"num": "21", "title": "21. In-line 검사", "page": 39},
    {"num": "22", "title": "22. End-line 검사", "page": 41},
    {"num": "23", "title": "23. Finishing 검사", "page": 43},
    {"num": "24", "title": "24. Dupro 검사", "page": 45},
    {"num": "25", "title": "25. Pre-Final 검사", "page": 47},
    {"num": "26", "title": "26. Final 검사", "page": 49},
    {"num": "27", "title": "27. 바늘과 금속 오염 관리", "page": 51},
    {"num": "28", "title": "28. 검침기 사용 설명", "page": 53},
    {"num": "29", "title": "29. 검침기 청소 관리", "page": 55},
    {"num": "30", "title": "30. 9 point Calibration", "page": 57},
    # 31~45번 (이미지 기준 정확 수정)
    {"num": "31", "title": "31. 핸드 검침기 사용법", "page": 59},
    {"num": "32", "title": "32. 9 point Calibration", "page": 61},
    {"num": "33", "title": "33. 부적격 자재 관리 CNCM(Control of Non-conforming Material)", "page": 63},
    {"num": "34", "title": "34. CAPA(Corrective & Preventive Action Plan)", "page": 65},
    {"num": "35", "title": "35. 열전사 라벨/심지 부착관리", "page": 67},
    {"num": "36", "title": "36. Snap/Button 관리", "page": 69},
    {"num": "37", "title": "37. Attachment Strength Test 방법 (Pulling Test)", "page": 71},
    {"num": "38", "title": "38. 어린이 제품 안전", "page": 73},
    {"num": "39", "title": "39. Carton/Garment 습도 관리", "page": 75},
    {"num": "40", "title": "40. 곰팡이 발생 방지를 위한 현장 관리", "page": 77},
    {"num": "41", "title": "41. Aqua Boy 수분 측정기 사용법", "page": 79},
    {"num": "42", "title": "42. 잔사 불량 예방 및 관리", "page": 81},
    {"num": "43", "title": "43. Virtual Inspection", "page": 83},
    {"num": "44", "title": "44. Virtual FE", "page": 85},
    {"num": "45", "title": "45. Risk Assessment Process Meeting", "page": 87},
    # 부록 1~5번 (이미지 기준 정확 수정)
    {"num": "App 1", "title": "부록1 Inspection Procedure (Production Test Plan)", "page": 90},
    {"num": "App 2", "title": "부록2 FE Quick check list", "page": 95},
    {"num": "App 3", "title": "부록3 Sewing Factory Self Assessment Report", "page": 100},
    {"num": "App 4", "title": "부록4 Mold Prevention Checklist", "page": 105},
    {"num": "App 5", "title": "부록5 Wear & Wash Test Report", "page": 110}
]

UI_LABELS = {
    "KO": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP 목차 목록 (전체 50개)",
        "manual_header": "SAE-A QA 표준 운영 절차 (SOP)",
        "search_label": "SOP 키워드 검색",
        "search_placeholder": "검색어를 입력하세요 (예: 핸드 검침기, 어린이, Calibration)",
        "page_info": "페이지 위치",
        "total_pages": "전체",
        "no_file": "SOP Handbook 메인 PDF 파일을 찾을 수 없습니다.",
        "no_text": "해당 페이지에 표시할 텍스트 내용이 없습니다.",
        "translating": "베트남어 자동 번역 진행 중..."
    },
    "EN": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP Contents (50 Items)",
        "manual_header": "SAE-A QA Standard Operating Procedure (SOP)",
        "search_label": "Search SOP Keywords",
        "search_placeholder": "Enter search keyword (e.g. Needle, Calibration)",
        "page_info": "Reference Page",
        "total_pages": "Total",
        "no_file": "Cannot find main SOP Handbook PDF file.",
        "no_text": "No text content available on this page.",
        "translating": "Translating to Vietnamese..."
    },
    "VI": {
        "title": "Hệ thống SAE-A QA SOP",
        "toc_header": "Danh mục SOP (Tổng số 50 mục)",
        "manual_header": "Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "search_label": "Tìm kiếm từ khóa SOP",
        "search_placeholder": "Nhập từ khóa (Ví dụ: Kiểm tra, Needle)",
        "page_info": "Trang tham khảo",
        "total_pages": "Tổng số",
        "no_file": "Không tìm thấy tệp PDF SOP chính.",
        "no_text": "Không có nội dung văn bản trên trang này.",
        "translating": "Đang tự động dịch sang tiếng Việt..."
    }
}

def find_main_sop_pdf(lang_code):
    """3페이지 소형 PDF 제외, 145페이지 분량의 메인 SOP Handbook PDF 찾기"""
    if not os.path.exists(assets_dir):
        return None
    files = [f for f in os.listdir(assets_dir) if f.lower().endswith('.pdf')]
    if not files:
        return None
    for f in files:
        if "handbook" in f.lower():
            return f
    files_with_size = [(f, os.path.getsize(os.path.join(assets_dir, f))) for f in files]
    files_with_size.sort(key=lambda x: x[1], reverse=True)
    return files_with_size[0][0]

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

def clean_and_format_text(raw_text):
    """줄바꿈 문단 정돈 및 가독성 최적화"""
    if not raw_text.strip():
        return ""
    cleaned = re.sub(r'[\.·_]{2,}', '', raw_text)
    lines = cleaned.split('\n')
    formatted = []
    
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if any(l.startswith(kw) for kw in ["Doc. No.", "Version", "Date", "Prepared", "Approved", "Department", "Note", "Objective"]):
            formatted.append(f"\n**{l}**\n")
        else:
            formatted.append(l)
            
    return "\n".join(formatted)

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

# --- 1. 사이드바 ---
with st.sidebar:
    lang_choice = st.radio("언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang_choice, "KO")
    labels = UI_LABELS[lang_code]
    
    st.markdown(f"### {labels['title']}")
    st.markdown("---")
    
    target_pdf = find_main_sop_pdf(lang_code)
    pages_data = load_pdf_data(target_pdf) if target_pdf else []
    
    st.markdown(f"**{labels['toc_header']}**")
    
    # 1~45번 항목 + 부록 1~5번 항목 라디오 버튼으로 표시
    toc_titles = [f"{item['title']} (P.{item['page']})" for item in SOP_TOC]
    selected_label = st.radio("목차를 선택하세요:", toc_titles, index=0)
    
    selected_index = toc_titles.index(selected_label)
    selected_item = SOP_TOC[selected_index]
    target_page_num = selected_item["page"]

# --- 2. 메인 화면 ---
st.caption(f"{labels['manual_header']} ({lang_choice})")

search_query = st.text_input(labels["search_label"], placeholder=labels["search_placeholder"])

if target_pdf and pages_data:
    if search_query.strip():
        st.markdown(f"#### 검색 결과: '{search_query}'")
        found_count = 0
        for i, p_text in enumerate(pages_data):
            if search_query.lower() in p_text.lower():
                found_count += 1
                with st.expander(f"Page {i+1} 검색 결과"):
                    st.markdown(clean_and_format_text(p_text))
        if found_count == 0:
            st.warning("일치하는 매뉴얼 내용을 찾을 수 없습니다.")
    else:
        page_idx = max(0, min(target_page_num - 1, len(pages_data) - 1))
        raw_content = pages_data[page_idx]
        formatted_content = clean_and_format_text(raw_content)
        
        display_title = selected_item["title"]
        
        if lang_code == "VI":
            with st.spinner(labels["translating"]):
                display_title = translate_to_vietnamese(display_title)
                display_content = translate_to_vietnamese(formatted_content)
        else:
            display_content = formatted_content

        st.markdown(f"#### {display_title}")
        
        with st.container(border=True):
            if display_content.strip():
                st.markdown(display_content)
            else:
                st.warning(labels["no_text"])
                
        st.caption(f"{labels['page_info']}: {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")

else:
    st.error(labels["no_file"])