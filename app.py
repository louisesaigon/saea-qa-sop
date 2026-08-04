import glob
import os
import pypdf
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="SOP Smart Handbook - SAE-A", page_icon="🔒", layout="wide"
)

# 2. 세션 상태 초기화 (비밀번호 인증)
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

# 3. 사이드바 설정
st.sidebar.title("SAE-A QA SOP System")
lang = st.sidebar.radio(
    "Language / 언어 선택", ["한국어 (Korean)", "English"], index=0
)

# 4. 보안 인증 화면 (비밀번호: 0101, 엔터 키 지원)
if not st.session_state.authenticated:
  st.title("🔒 SAE-A QA SOP 보안 인증")
  st.write("매뉴얼을 열람하려면 시스템 비밀번호(숫자 4자리)를 입력하십시오.")

  with st.form("auth_form"):
    password = st.text_input(
        "비밀번호 입력",
        type="password",
        max_chars=4,
        value="",
        placeholder="비밀번호 4자리 입력",
    )
    submitted = st.form_submit_button("인증 확인")
    if submitted:
      if password == "0101":
        st.session_state.authenticated = True
        st.rerun()
      else:
        st.error("비밀번호가 틀렸습니다. (힌트: 0101)")
  st.stop()

# --- 인증 완료 후 메인 로직 ---

# 5. 폴더 내 PDF 파일 자동 감지 로직 (파일명 무관하게 인식)
@st.cache_resource
def get_pdf_reader(selected_lang):
  pdf_files = glob.glob("*.pdf")
  if not pdf_files:
    return None, "현재 폴더에 PDF 파일이 없습니다. (GitHub에 PDF 업로드 필요)"

  kr_file, en_file = None, None
  for f in pdf_files:
    f_lower = f.lower()
    if (
        "국문" in f
        or "kor" in f_lower
        or "korean" in f_lower
        or "국문본" in f
    ):
      kr_file = f
    elif "eng" in f_lower or "english" in f_lower or "ver" in f_lower:
      # 영문 파일 매칭
      if not en_file:
        en_file = f

  # 만약 키워드로 못 찾았을 경우 순서대로 배정
  if not kr_file and len(pdf_files) > 0:
    kr_file = pdf_files[0]
  if not en_file and len(pdf_files) > 1:
    en_file = pdf_files[1]
  elif not en_file:
    en_file = pdf_files[0]

  target = kr_file if selected_lang == "kr" else en_file
  if not target:
    return None, f"매칭되는 PDF 없음 (파일 목록: {pdf_files})"

  try:
    return pypdf.PdfReader(target), target
  except Exception as e:
    return None, str(e)


lang_key = "kr" if lang == "한국어 (Korean)" else "en"
reader, file_info = get_pdf_reader(lang_key)

if lang == "한국어 (Korean)":
  st.sidebar.markdown("---")
  st.sidebar.subheader("SOP 목차")
else:
  st.sidebar.markdown("---")
  st.sidebar.subheader("SOP Table of Contents")

# 6. 목차 및 페이지 매칭 데이터 정의
toc_data_kr = [
    ("1. 개요 (Overview)", 3),
    ("2. QA/QC 정의", 4),
    ("3. AQL (Acceptable Quality Limit)", 6),
    ("4. Sae-A DCL (Defect Classification List)", 8),
    ("5. 원단 검사 (4-Point System)", 9),
    ("6. 원단 방단", 12),
    ("7. 부자재 검사", 15),
    ("8. 패턴 조정 절차 및 관리", 18),
    ("9. PPM Workflow Chart", 20),
    ("10. PP Sample 제작", 21),
    ("11. Internal PPM", 23),
    ("12. PPM", 25),
    ("13. 연단 및 마커 검사", 27),
    ("14. 재단물 검사", 31),
    ("15. 자수/프린트 검사", 33),
    ("16. Pilot Run 검사", 35),
    ("17. Wear & Wash Test", 37),
    ("18. 1st Output 검사", 39),
    ("19. In-Process 검사", 41),
    ("20. Seam Allowance 모니터링", 43),
    ("21. In-Line 검사", 45),
    ("22. End-Line 검사", 47),
    ("23. Finishing 검사", 49),
    ("24. Dupro 검사", 51),
    ("25. Pre-Final 검사", 53),
    ("26. Final 검사", 55),
    ("27. 바늘 및 금속 오염 관리", 58),
    ("28. 검침기 사용 설명", 60),
    ("29. 검침기 청소 관리", 63),
    ("30. 핸드 검침기 사용법", 67),
    ("31. 9 point Calibration", 69),
    ("32. 부적격 자재 관리 (CNCM)", 72),
    ("33. CAPA (Corrective & Preventive Action)", 75),
    ("34. HTL, Fusing 관리", 78),
    ("35. 스냅, 버튼 관리", 81),
    ("36. Pulling Test", 83),
    ("37. 어린이 제품 안전 (Children's Safety)", 85),
    ("38. Carton 및 제품 습도 관리", 88),
    ("39. 곰팡이 발생 방지 관리", 91),
    ("40. Aqua Boy 사용법", 94),
    ("41. 잔사 불량 관리", 96),
    ("42. Virtual Inspection", 99),
    ("43. Virtual FE", 101),
    ("44. RAP Meeting", 103),
    ("45. 검사 절차 (Inspection Procedure)", 105),
]

toc_data_en = [
    ("1. Overview", 3),
    ("2. QA/QC Definition", 4),
    ("3. AQL (Acceptable Quality Limit)", 6),
    ("4. Sae-A DCL (Defect Classification List)", 8),
    ("5. Fabric Inspection (4-Point System)", 9),
    ("6. Fabric Relaxation", 12),
    ("7. Accessory Inspection", 15),
    ("8. Pattern Adjustment", 18),
    ("9. PPM Workflow Chart", 20),
    ("10. PP Sample", 21),
    ("11. Internal PPM", 23),
    ("12. PPM", 25),
    ("13. Spreading & Marker", 27),
    ("14. Cut Panel Inspection", 31),
    ("15. Embroidery & Print Inspection", 33),
    ("16. Pilot Run", 35),
    ("17. Wear & Wash Test", 37),
    ("18. 1st Output Inspection", 39),
    ("19. In-Process Inspection", 41),
    ("20. Seam Allowance Monitoring", 43),
    ("21. In-Line Inspection", 45),
    ("22. End-Line Inspection", 47),
    ("23. Finishing Inspection", 49),
    ("24. Dupro Inspection", 51),
    ("25. Pre-Final Inspection", 53),
    ("26. Final Inspection", 55),
    ("27. Needle & Metal Contamination", 58),
    ("28. Metal Detector How to Use", 60),
    ("29. Metal Detector Cleaning", 63),
    ("30. How to Use Handheld Metal Detector", 67),
    ("31. 9 point Calibration", 69),
    ("32. CNCM", 72),
    ("33. CAPA", 75),
    ("34. HTL, Fusing", 78),
    ("35. Snap, Button", 81),
    ("36. Pulling Test", 83),
    ("37. Children's Safety", 85),
    ("38. Carton & Garment Humidity Control", 88),
    ("39. Mold Prevention", 91),
    ("40. Aqua Boy", 94),
    ("41. Managing Thread Defect", 96),
    ("42. Virtual Inspection", 99),
    ("43. Virtual FE", 101),
    ("44. RAP Meeting", 103),
    ("45. Inspection Procedure", 105),
]

toc_data = toc_data_kr if lang == "한국어 (Korean)" else toc_data_en

# 7. 목차 선택
toc_titles = [item[0] for item in toc_data]
selected_title = st.sidebar.radio("목차를 선택하세요:", toc_titles)

selected_page_num = 3
for title, p_num in toc_data:
  if title == selected_title:
    selected_page_num = p_num
    break

# 8. 메인 화면 렌더링
if lang == "한국어 (Korean)":
  st.markdown(
      """
    > **⚠️ 보안 경고 (Security Notice)**
    > 이 SOP는 **SAE-A의 자산**으로 전부 또는 일부 내용의 허가되지 않은 외부 유출, 제3자 배포, 복사는 엄격히 금지된다.
    """
  )
  st.subheader(f"📖 {selected_title}")
else:
  st.markdown(
      """
    > **⚠️ Security Notice**
    > This SOP is the property of **SAE-A**. Unauthorized external leakage, third-party distribution, or copying of all or part of the contents is strictly prohibited.
    """
  )
  st.subheader(f"📖 {selected_title}")

if reader and isinstance(reader, pypdf.PdfReader):
  target_idx = max(0, selected_page_num - 1)
  if target_idx < len(reader.pages):
    page_text = reader.pages[target_idx].extract_text()
    st.text_area(
        "SOP Manual Content / 매뉴얼 내용",
        page_text,
        height=600,
        disabled=True,
    )
    st.info(
        f"현재 표시된 페이지: PDF {selected_page_num}페이지 | 연동 파일:"
        f" {file_info}"
    )
  else:
    st.error("해당 페이지를 찾을 수 없습니다.")
else:
  st.error(
      f"PDF 파일을 불러오지 못했습니다. 원인: {file_info} (※ 참고: GitHub"
      " 저장소에 PDF 파일들이 정상적으로 push 되어 있는지 확인해주세요.)"
  )