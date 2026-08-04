import streamlit as st
import os
from pypdf import PdfReader

# 페이지 기본 설정 (모바일 모드 최적화)
st.set_page_config(
    page_title="SAE-A QA SOP Manual",
    page_icon="📋",
    layout="centered"
)

# 자산 폴더 경로
assets_dir = os.path.join(os.path.dirname(__file__), "assets")

# PDF 텍스트 추출 함수 (캐싱 처리로 속도 향상)
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

# --- 헤더 영역 ---
st.title("📋 SAE-A QA SOP")
st.caption("모바일 최적화 텍스트 매뉴얼")

# --- 언어 / 매뉴얼 선택 ---
lang = st.radio("🌐 언어 선택 / Select Language", ["한국어", "English", "Tiếng Việt"], horizontal=True)

# 언어 코드 매핑
lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
lang_code = lang_map.get(lang, "KO")

# 매뉴얼 종류 선택 (드롭다운/셀렉트박스로 모바일 터치 편의성 확보)
manual_type = st.selectbox(
    "📚 매뉴얼 종류 선택",
    ["SOP Handbook", "Wear & Wash SOP", "Fleece SOP"]
)

# 매뉴얼 파일명 결정
if manual_type == "Wear & Wash SOP":
    target_file = f"SOP_WearWash_{lang_code}_20260630.pdf"
elif manual_type == "Fleece SOP":
    target_file = f"SOP_Fleece_{lang_code}_20260630.pdf"
else:
    target_file = f"SOP_Handbook_{lang_code}_20250901.pdf"

st.markdown("---")

# --- 텍스트 매뉴얼 출력 영역 ---
st.subheader(f"📖 {manual_type} ({lang})")

with st.spinner("매뉴얼 텍스트를 불러오는 중입니다..."):
    pdf_text = extract_text_from_pdf(target_file)

if pdf_text:
    # 모바일에서 읽기 편하도록 깔끔한 컨테이너 카드 형태로 텍스트 출력
    with st.container():
        st.markdown(pdf_text)
else:
    st.error(f"⚠️ 매뉴얼 파일(`{target_file}`)을 찾을 수 없습니다. `assets` 폴더를 확인해 주세요.")