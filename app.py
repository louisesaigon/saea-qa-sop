import streamlit as st
import os
import base64
from pypdf import PdfReader

# 모바일 환경을 고려해 사이드바 기본 상태를 auto/collapsed로 지정
st.set_page_config(
    page_title="SOP Standard Operation Manual System", 
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 1. 보안 및 로그인 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.error("⚠️ [NOTICE] Intellectual Property & Confidentiality Warning")
    st.warning("본 시스템 내 매뉴얼 및 정보는 회사의 지적재산(IP)입니다. 무단 유출 및 복제를 엄격히 금합니다.")
    
    with st.form("login_form"):
        password = st.text_input("접속 비밀번호를 입력하세요:", type="password")
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            if password == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

assets_dir = "assets"

# --- 2. 언어 선택 및 다국어 UI ---
st.sidebar.title("🌐 Language / 언어")
lang_choice = st.sidebar.radio("Select Language / 언어 선택", ["한국어 (KOR)", "English (ENG)"])
is_kor = "한국어" in lang_choice
lang_code = "KOR" if is_kor else "ENG"

# --- 3. 목차 매핑 ---
toc_mapping_kor = [
    ("📌 INTRODUCTION (머리말)", 1),
    ("QA/QC 정의", 2),
    ("AQL (Acceptable Quality Limit)", 3),
    ("Sae-A DCL (Defect Classification List)", 4),
    ("원단 검사/4point System", 5),
    ("원단 방단", 6),
    ("부자재 검사", 7),
    ("패턴 조정 절차 및 관리", 18),
    ("PPM Workflow Chart", 19),
    ("PP Sample 제작", 20),
    ("Internal PPM", 21),
    ("PPM", 22),
    ("연단 및 마커 검사", 23),
    ("재단물 검사", 24),
    ("자수/프린트 검사", 25),
    ("Pilot Run 검사", 26),
    ("Wear & Wash Test", 27),
    ("1st Output 검사", 28),
    ("In-Process 검사", 29),
    ("Seam allowance 모니터링", 30),
    ("In-line 검사", 31),
    ("End-line 검사", 32),
    ("Finishing 검사", 33),
    ("Dupro 검사", 34),
    ("Pre-Final 검사", 35),
    ("Final 검사", 36),
    ("바늘과 금속 오염 관리", 37),
    ("검침기 사용 설명", 38),
    ("검침기 청소 관리", 39),
    ("핸드 검침기 사용법", 40),
    ("9 point Calibration", 41),
    ("부적격 자재 관리 CNCM", 42),
    ("CAPA (Corrective & Preventive Action)", 43),
    ("열전사 라벨/심지 부착관리", 44),
    ("Snap/Button 관리", 45),
    ("Attachment Strength Test 방법", 46),
    ("어린이 제품 안전", 47),
    ("Carton/Garment 습도 관리", 48),
    ("곰팡이 발생 방지를 위한 현장 관리", 49),
    ("Aqua Boy 수분 측정기 사용법", 50),
    ("잔사 불량 예방 및 관리", 51),
    ("Virtual Inspection", 52),
    ("Virtual FE", 53),
    ("Risk Assessment Process Meeting", 54),
    ("부록1. Inspection Procedure", 55),
    ("부록2. FE Quick check list", 60),
    ("부록3. Sewing Factory Self Assessment", 65),
    ("부록4. Mold Prevention Checklist", 70),
    ("부록5. Wear & Wash Test Report", 75)
]

toc_mapping_eng = [
    ("📌 INTRODUCTION", 1),
    ("QA/QC Definition", 2),
    ("AQL (Acceptable Quality Limit)", 3),
    ("Sae-A DCL (Defect Classification List)", 4),
    ("Fabric Inspection / 4point System", 5),
    ("Fabric Relaxation & Shading", 6),
    ("Trims & Accessories Inspection", 7),
    ("Pattern Adjustment & Control", 18),
    ("PPM Workflow Chart", 19),
    ("PP Sample Production", 20),
    ("Internal PPM", 21),
    ("PPM", 22),
    ("Spreading & Marker Inspection", 23),
    ("Cut Panel Inspection", 24),
    ("Embroidery / Print Inspection", 25),
    ("Pilot Run Inspection", 26),
    ("Wear & Wash Test", 27),
    ("1st Output Inspection", 28),
    ("In-Process Inspection", 29),
    ("Seam Allowance Monitoring", 30),
    ("In-line Inspection", 31),
    ("End-line Inspection", 32),
    ("Finishing Inspection", 33),
    ("Dupro Inspection", 34),
    ("Pre-Final Inspection", 35),
    ("Final Inspection", 36),
    ("Needle & Metal Contamination Control", 37),
    ("Needle Detector Operation Guide", 38),
    ("Needle Detector Cleaning & Maintenance", 39),
    ("Handheld Needle Detector Guide", 40),
    ("9-point Calibration", 41),
    ("CNCM (Non-conforming Material Control)", 42),
    ("CAPA (Corrective & Preventive Action)", 43),
    ("Heat Transfer Label & Interlining Control", 44),
    ("Snap & Button Management", 45),
    ("Attachment Strength Test Method", 46),
    ("Children's Product Safety", 47),
    ("Carton / Garment Humidity Control", 48),
    ("Mold Prevention Field Control", 49),
    ("Aqua Boy Moisture Meter Operation", 50),
    ("Thread Ends Defect Prevention", 51),
    ("Virtual Inspection", 52),
    ("Virtual FE", 53),
    ("Risk Assessment Process Meeting", 54),
    ("Appendix 1. Inspection Procedure", 55),
    ("Appendix 2. FE Quick Checklist", 60),
    ("Appendix 3. Sewing Factory Self Assessment", 65),
    ("Appendix 4. Mold Prevention Checklist", 70),
    ("Appendix 5. Wear & Wash Test Report", 75)
]

current_toc_mapping = toc_mapping_kor if is_kor else toc_mapping_eng
toc_titles = [item[0] for item in current_toc_mapping]
page_dict = dict(current_toc_mapping)

# --- 4. 사이드바 UI ---
st.sidebar.markdown("---")
st.sidebar.header("📋 CONTENTS" if not is_kor else "📋 CONTENTS (목차)")
selected_topic = st.sidebar.radio("Select Topic" if not is_kor else "소제목 선택", toc_titles)

st.sidebar.markdown("---")
st.sidebar.caption("📌 **Revised / Separate SOPs**" if not is_kor else "📌 **개정/별도 지침 문서**")
other_doc = st.sidebar.radio(
    "Select Document" if not is_kor else "별도 문서 열람",
    ["SOP Handbook", "Wear & Wash Test SOP", "Fleece & Brushed Fabric QC"]
)

# --- 5. 메인 화면 ---
st.title("📱 SOP Manual System")

search_label = "🔍 Search Keyword" if not is_kor else "🔍 매뉴얼 본문 통합 검색"
search_placeholder = "Enter keyword..." if not is_kor else "검색어 입력 후 Enter..."

search_term = st.text_input(search_label, placeholder=search_placeholder)

if search_term and os.path.exists(assets_dir):
    pdf_files = [f for f in os.listdir(assets_dir) if f.endswith('.pdf') and lang_code in f]
    found_any = False
    
    st.info(f"🔎 Results for **'{search_term}'**:")
    for pdf_file in pdf_files:
        pdf_path = os.path.join(assets_dir, pdf_file)
        try:
            reader = PdfReader(pdf_path)
            matches = []
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if search_term.lower() in text.lower():
                    start_i = max(0, text.lower().find(search_term.lower()) - 20)
                    snippet = text[start_i:start_i+80].replace("\n", " ")
                    matches.append((idx + 1, snippet))
            
            if matches:
                found_any = True
                with st.expander(f"📄 **{pdf_file}** ({len(matches)} matches)", expanded=True):
                    for p_num, snip in matches[:5]:
                        st.markdown(f"• **Pg {p_num}:** `... {snip} ...`")
        except Exception as e:
            st.error(f"Search Error: {e}")

st.markdown("---")

# --- 6. 모바일 맞춤 보안 PDF 뷰어 ---
def show_mobile_pdf_viewer(file_path, page_num=1):
    if not os.path.exists(file_path):
        st.error(f"File not found: `{file_path}`")
        return
        
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    
    b64_data = base64.b64encode(pdf_data).decode('utf-8')
    
    # 모바일 터치 스크롤에 맞춘 최적 높이 적용 (750px)
    html_code = f'''
    <div style="width:100%; height:750px; border:1px solid #ccc; border-radius:8px; overflow:hidden;">
        <embed src="data:application/pdf;base64,{b64_data}#page={page_num}&toolbar=0&navpanes=0" 
               type="application/pdf" width="100%" height="100%" />
    </div>
    '''
    st.components.v1.html(html_code, height=760)

# --- 7. 메인 콘텐츠 ---
if "Wear & Wash" in other_doc:
    target_file = f"SOP_WearWash_{lang_code}_20260630.pdf"
    target_page = 1
elif "Fleece" in other_doc:
    target_file = f"SOP_Fleece_{lang_code}_20260630.pdf"
    target_page = 1
else:
    target_file = f"SOP_Handbook_{lang_code}_20250901.pdf"
    target_page = page_dict.get(selected_topic, 1)

target_path = os.path.join(assets_dir, target_file)

clean_title = selected_topic.replace("📌 ", "")
st.markdown(f"#### 📖 `{clean_title}`")

show_mobile_pdf_viewer(target_path, page_num=target_page)