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

# 사이드바 라디오 버튼 스타일 최적화 (텍스트 줄바꿈 및 간격)
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

# 목차 목록 (옆에 P.1 등 페이지 번호 완전 제거)
SOP_TOC = [
    {"num": "1", "title": "1. 머리말", "keyword": "머리말"},
    {"num": "2", "title": "2. QA/QC 정의", "keyword": "QA/QC 정의"},
    {"num": "3", "title": "3. AQL (Acceptable Quality Limit)", "keyword": "AQL"},
    {"num": "4", "title": "4. Sae-A DCL (Defect Classification List)", "keyword": "Defect Classification List"},
    {"num": "5", "title": "5. 원단 검사/4point System", "keyword": "원단 검사"},
    {"num": "6", "title": "6. 원단 방단", "keyword": "원단 방단"},
    {"num": "7", "title": "7. 부자재 검사", "keyword": "부자재 검사"},
    {"num": "8", "title": "8. 패턴 조정 절차 및 관리", "keyword": "패턴 조정"},
    {"num": "9", "title": "9. PPM Workflow Chart", "keyword": "PPM Workflow"},
    {"num": "10", "title": "10. PP Sample 제작", "keyword": "PP Sample"},
    {"num": "11", "title": "11. Internal PPM", "keyword": "Internal PPM"},
    {"num": "12", "title": "12. PPM", "keyword": "PPM"},
    {"num": "13", "title": "13. 연단 및 마커 검사", "keyword": "연단 및 마커"},
    {"num": "14", "title": "14. 재단물 검사", "keyword": "재단물 검사"},
    {"num": "15", "title": "15. 자수/프린트 검사", "keyword": "자수"},
    {"num": "16", "title": "16. Pilot Run 검사", "keyword": "Pilot Run"},
    {"num": "17", "title": "17. Wear & Wash Test", "keyword": "Wear & Wash"},
    {"num": "18", "title": "18. 1st Output 검사", "keyword": "1st Output"},
    {"num": "19", "title": "19. In-Process 검사", "keyword": "In-Process"},
    {"num": "20", "title": "20. Seam allowance 모니터링", "keyword": "Seam allowance"},
    {"num": "21", "title": "21. In-line 검사", "keyword": "In-line 검사"},
    {"num": "22", "title": "22. End-line 검사", "keyword": "End-line 검사"},
    {"num": "23", "title": "23. Finishing 검사", "keyword": "Finishing 검사"},
    {"num": "24", "title": "24. Dupro 검사", "keyword": "Dupro 검사"},
    {"num": "25", "title": "25. Pre-Final 검사", "keyword": "Pre-Final"},
    {"num": "26", "title": "26. Final 검사", "keyword": "Final 검사"},
    {"num": "27", "title": "27. 바늘과 금속 오염 관리", "keyword": "바늘과 금속"},
    {"num": "28", "title": "28. 검침기 사용 설명", "keyword": "검침기 사용"},
    {"num": "29", "title": "29. 검침기 청소 관리", "keyword": "검침기 청소"},
    {"num": "30", "title": "30. 9 point Calibration", "keyword": "9 point Calibration"},
    {"num": "31", "title": "31. 핸드 검침기 사용법", "keyword": "핸드 검침기"},
    {"num": "32", "title": "32. 9 point Calibration", "keyword": "Calibration"},
    {"num": "33", "title": "33. 부적격 자재 관리 CNCM(Control of Non-conforming Material)", "keyword": "부적격 자재"},
    {"num": "34", "title": "34. CAPA(Corrective & Preventive Action Plan)", "keyword": "CAPA"},
    {"num": "35", "title": "35. 열전사 라벨/심지 부착관리", "keyword": "열전사 라벨"},
    {"num": "36", "title": "36. Snap/Button 관리", "keyword": "Snap/Button"},
    {"num": "37", "title": "37. Attachment Strength Test 방법 (Pulling Test)", "keyword": "Attachment Strength"},
    {"num": "38", "title": "38. 어린이 제품 안전", "keyword": "어린이 제품"},
    {"num": "39", "title": "39. Carton/Garment 습도 관리", "keyword": "습도 관리"},
    {"num": "40", "title": "40. 곰팡이 발생 방지를 위한 현장 관리", "keyword": "곰팡이"},
    {"num": "41", "title": "41. Aqua Boy 수분 측정기 사용법", "keyword": "Aqua Boy"},
    {"num": "42", "title": "42. 잔사 불량 예방 및 관리", "keyword": "잔사 불량"},
    {"num": "43", "title": "43. Virtual Inspection", "keyword": "Virtual Inspection"},
    {"num": "44", "title": "44. Virtual FE", "keyword": "Virtual FE"},
    {"num": "45", "title": "45. Risk Assessment Process Meeting", "keyword": "Risk Assessment"},
    {"num": "App1", "title": "부록1 Inspection Procedure (Production Test Plan)", "keyword": "Inspection Procedure"},
    {"num": "App2", "title": "부록2 FE Quick check list", "keyword": "Quick check list"},
    {"num": "App3", "title": "부록3 Sewing Factory Self Assessment Report", "keyword": "Self Assessment"},
    {"num": "App4", "title": "부록4 Mold Prevention Checklist", "keyword": "Mold Prevention"},
    {"num": "App5", "title": "부록5 Wear & Wash Test Report", "keyword": "Test Report"}
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

def find_matching_page_index(pages_data, item_info, default_idx):
    """목차 페이지(Contents)를 건너뛰고 해당 섹션이 실제로 시작하는 본문 페이지 탐색"""
    keyword = item_info.get("keyword", "").lower()
    if not keyword or not pages_data:
        return default_idx

    # 앞 3페이지(목차/표지 영역)를 제외하고 검색
    start_search_page = 2 if len(pages_data) > 3 else 0

    for idx in range(start_search_page, len(pages_data)):
        page_text = pages_data[idx].lower()
        if keyword in page_text:
            return idx
            
    return default_idx

def clean_and_format_text(raw_text):
    """점선 제거 및 단락 구분을 통한 가독성 대폭 향상"""
    if not raw_text.strip():
        return ""
    
    # 1. 점선 및 특수 연속 기호 완전 제거
    cleaned = re.sub(r'[\.·_]{2,}', '', raw_text)
    
    lines = cleaned.split('\n')
    formatted_paragraphs = []
    
    for line in lines:
        l = line.strip()
        if not l:
            continue
            
        # 2. 항목 번호, 주요 헤더 및 섹션 키워드 강하게 분리
        is_header = any(l.startswith(kw) for kw in [
            "Doc. No.", "Version", "Date", "Prepared", "Approved", 
            "Department", "Note", "Objective", "Purpose", "Scope"
        ]) or re.match(r'^\d+[\.\)]\s*', l) or re.match(r'^[가-하A-Z][\.\)]\s*', l)

        if is_header:
            formatted_paragraphs.append(f"\n\n### {l}\n")
        else:
            # 문장 마침표 뒤 단락 구분
            l_formatted = re.sub(r'(\. )', '.\n\n', l)
            formatted_paragraphs.append(l_formatted)
            
    result_text = " ".join(formatted_paragraphs)
    # 불필요한 연속 개행 정리
    result_text = re.sub(r'\n{3,}', '\n\n', result_text)
    
    return result_text.strip()

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
    
    # 페이지 번호(P.1 등) 없이 깔끔한 목차 제목만 노출
    toc_titles = [item['title'] for item in SOP_TOC]
    selected_title = st.radio("목차를 선택하세요:", toc_titles, index=0)
    
    selected_index = toc_titles.index(selected_title)
    selected_item = SOP_TOC[selected_index]
    
    # 본문 해당 페이지 자동 탐색
    estimated_idx = selected_index + 2
    matched_page_idx = find_matching_page_index(pages_data, selected_item, estimated_idx)

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
        page_idx = max(0, min(matched_page_idx, len(pages_data) - 1))
        raw_content = pages_data[page_idx]
        formatted_content = clean_and_format_text(raw_content)
        
        display_title = selected_item["title"]
        
        if lang_code == "VI":
            with st.spinner(labels["translating"]):
                display_title = translate_to_vietnamese(display_title)
                display_content = translate_to_vietnamese(formatted_content)
        else:
            display_content = formatted_content

        st.markdown(f"### 📖 {display_title}")
        
        with st.container(border=True):
            if display_content.strip():
                st.markdown(display_content)
            else:
                st.warning(labels["no_text"])
                
        st.caption(f"{labels['page_info']}: {page_idx + 1} / {labels['total_pages']} {len(pages_data)}")

else:
    st.error(labels["no_file"])