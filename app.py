import streamlit as st
import os
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="SAE-A QA SOP System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 및 모바일 가독성 최적화 CSS
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

# 다국어 목차 데이터셋 (한국어 / 영어 / 베트남어)
TOC_DATA = {
    "KO": [
        {"title": "1. 머리말", "page": 3},
        {"title": "2. QA/QC 정의", "page": 4},
        {"title": "3. AQL (Acceptable Quality Limit)", "page": 5},
        {"title": "4. Sae-A DCL (Defect Classification List)", "page": 7},
        {"title": "5. 원단 검사/4point System", "page": 9},
        {"title": "6. 원단 방단", "page": 10},
        {"title": "7. 부자재 검사", "page": 13},
        {"title": "8. 패턴 조정 절차 및 관리", "page": 16},
        {"title": "9. PPM Workflow Chart", "page": 19},
        {"title": "10. PP Sample 제작", "page": 21},
        {"title": "11. Internal PPM", "page": 22},
        {"title": "12. PPM", "page": 24},
        {"title": "13. 연단 및 마커 검사", "page": 26},
        {"title": "14. 재단물 검사", "page": 28},
        {"title": "15. 자수/프린트 검사", "page": 30},
        {"title": "16. Pilot Run 검사", "page": 32},
        {"title": "17. Wear & Wash Test", "page": 34},
        {"title": "18. 1st Output 검사", "page": 36},
        {"title": "19. In-Process 검사", "page": 38},
        {"title": "20. Seam allowance 모니터링", "page": 40},
        {"title": "21. In-line 검사", "page": 42},
        {"title": "22. End-line 검사", "page": 44},
        {"title": "23. Finishing 검사", "page": 46},
        {"title": "24. Dupro 검사", "page": 48},
        {"title": "25. Pre-Final 검사", "page": 50},
        {"title": "26. Final 검사", "page": 52},
        {"title": "27. 바늘과 금속 오염 관리", "page": 54},
        {"title": "28. 검침기 사용 설명", "page": 56},
        {"title": "29. 검침기 청소 관리", "page": 58},
        {"title": "30. 9 point Calibration", "page": 60},
        {"title": "31. 핸드 검침기 사용법", "page": 62},
        {"title": "32. 9 point Calibration", "page": 64},
        {"title": "33. 부적격 자재 관리 CNCM", "page": 66},
        {"title": "34. CAPA", "page": 68},
        {"title": "35. 열전사 라벨/심지 부착관리", "page": 70},
        {"title": "36. Snap/Button 관리", "page": 72},
        {"title": "37. Attachment Strength Test 방법", "page": 74},
        {"title": "38. 어린이 제품 안전", "page": 76},
        {"title": "39. Carton/Garment 습도 관리", "page": 78},
        {"title": "40. 곰팡이 발생 방지 현장 관리", "page": 80},
        {"title": "41. Aqua Boy 수분 측정기 사용법", "page": 82},
        {"title": "42. 잔사 불량 예방 및 관리", "page": 84},
        {"title": "43. Virtual Inspection", "page": 86},
        {"title": "44. Virtual FE", "page": 88},
        {"title": "45. Risk Assessment Process Meeting", "page": 90},
        {"title": "부록 1. Inspection Procedure", "page": 93},
        {"title": "부록 2. FE Quick check list", "page": 98},
        {"title": "부록 3. Sewing Factory Self Assessment", "page": 103},
        {"title": "부록 4. Mold Prevention Checklist", "page": 108},
        {"title": "부록 5. Wear & Wash Test Report", "page": 113}
    ],
    "EN": [
        {"title": "1. Introduction", "page": 3},
        {"title": "2. QA/QC Definition", "page": 4},
        {"title": "3. AQL (Acceptable Quality Limit)", "page": 5},
        {"title": "4. Sae-A DCL (Defect Classification List)", "page": 7},
        {"title": "5. Fabric Inspection / 4point System", "page": 9},
        {"title": "6. Fabric Relaxation Management", "page": 10},
        {"title": "7. Trims & Accessories Inspection", "page": 13},
        {"title": "8. Pattern Adjustment & Management", "page": 16},
        {"title": "9. PPM Workflow Chart", "page": 19},
        {"title": "10. PP Sample Making", "page": 21},
        {"title": "11. Internal PPM", "page": 22},
        {"title": "12. PPM Process", "page": 24},
        {"title": "13. Spreading & Marker Inspection", "page": 26},
        {"title": "14. Cut Panel Inspection", "page": 28},
        {"title": "15. Embroidery/Print Inspection", "page": 30},
        {"title": "16. Pilot Run Inspection", "page": 32},
        {"title": "17. Wear & Wash Test", "page": 34},
        {"title": "18. 1st Output Inspection", "page": 36},
        {"title": "19. In-Process Inspection", "page": 38},
        {"title": "20. Seam Allowance Monitoring", "page": 40},
        {"title": "21. In-line Inspection", "page": 42},
        {"title": "22. End-line Inspection", "page": 44},
        {"title": "23. Finishing Inspection", "page": 46},
        {"title": "24. Dupro Inspection", "page": 48},
        {"title": "25. Pre-Final Inspection", "page": 50},
        {"title": "26. Final Inspection", "page": 52},
        {"title": "27. Needle & Metal Contamination Control", "page": 54},
        {"title": "28. Needle Detector Operation", "page": 56},
        {"title": "29. Needle Detector Cleaning & Maintenance", "page": 58},
        {"title": "30. 9 point Calibration", "page": 60},
        {"title": "31. Hand-held Metal Detector Usage", "page": 62},
        {"title": "32. 9 point Calibration (Hand Detector)", "page": 64},
        {"title": "33. Control of Non-conforming Material (CNCM)", "page": 66},
        {"title": "34. CAPA", "page": 68},
        {"title": "35. Heat Transfer Label / Interlining Control", "page": 70},
        {"title": "36. Snap / Button Control", "page": 72},
        {"title": "37. Attachment Strength Test (Pulling Test)", "page": 74},
        {"title": "38. Children's Product Safety", "page": 76},
        {"title": "39. Carton / Garment Humidity Control", "page": 78},
        {"title": "40. Mold Prevention Site Management", "page": 80},
        {"title": "41. Aqua Boy Moisture Meter Usage", "page": 82},
        {"title": "42. Loose Fiber / Residue Prevention", "page": 84},
        {"title": "43. Virtual Inspection", "page": 86},
        {"title": "44. Virtual FE", "page": 88},
        {"title": "45. Risk Assessment Process Meeting", "page": 90},
        {"title": "Appendix 1. Inspection Procedure", "page": 93},
        {"title": "Appendix 2. FE Quick check list", "page": 98},
        {"title": "Appendix 3. Sewing Factory Self Assessment", "page": 103},
        {"title": "Appendix 4. Mold Prevention Checklist", "page": 108},
        {"title": "Appendix 5. Wear & Wash Test Report", "page": 113}
    ],
    "VI": [
        {"title": "1. Giới thiệu (Introduction)", "page": 3},
        {"title": "2. Định nghĩa QA/QC", "page": 4},
        {"title": "3. AQL (Giới hạn chất lượng chấp nhận được)", "page": 5},
        {"title": "4. Danh mục phân loại lỗi Sae-A (DCL)", "page": 7},
        {"title": "5. Kiểm tra vải / Hệ thống 4 điểm", "page": 9},
        {"title": "6. Quản lý thả lỏng vải", "page": 10},
        {"title": "7. Kiểm tra nguyên phụ liệu", "page": 13},
        {"title": "8. Quy trình điều chỉnh và quản lý rập", "page": 16},
        {"title": "9. Biểu đồ quy trình PPM", "page": 19},
        {"title": "10. Làm mẫu PP", "page": 21},
        {"title": "11. PPM nội bộ", "page": 22},
        {"title": "12. Quy trình PPM", "page": 24},
        {"title": "13. Kiểm tra trải vải và sơ đồ", "page": 26},
        {"title": "14. Kiểm tra bán thành phẩm cắt", "page": 28},
        {"title": "15. Kiểm tra thêu/in", "page": 30},
        {"title": "16. Kiểm tra chạy thử (Pilot Run)", "page": 32},
        {"title": "17. Kiểm tra độ bền giặt (Wear & Wash)", "page": 34},
        {"title": "18. Kiểm tra sản phẩm đầu ra đầu tiên", "page": 36},
        {"title": "19. Kiểm tra trong quá trình sản xuất", "page": 38},
        {"title": "20. Theo dõi độ rộng đường may", "page": 40},
        {"title": "21. Kiểm tra chuyền (In-line)", "page": 42},
        {"title": "22. Kiểm tra cuối chuyền (End-line)", "page": 44},
        {"title": "23. Kiểm tra hoàn thiện (Finishing)", "page": 46},
        {"title": "24. Kiểm tra Dupro", "page": 48},
        {"title": "25. Kiểm tra tiền xuất hàng (Pre-Final)", "page": 50},
        {"title": "26. Kiểm tra cuối cùng (Final)", "page": 52},
        {"title": "27. Quản lý kim và nhiễm bẩn kim loại", "page": 54},
        {"title": "28. Vận hành máy dò kim", "page": 56},
        {"title": "29. Vệ sinh và bảo dưỡng máy dò kim", "page": 58},
        {"title": "30. Hiệu chuẩn 9 điểm", "page": 60},
        {"title": "31. Sử dụng máy dò kim cầm tay", "page": 62},
        {"title": "32. Hiệu chuẩn 9 điểm (Máy cầm tay)", "page": 64},
        {"title": "33. Quản lý nguyên vật liệu không phù hợp (CNCM)", "page": 66},
        {"title": "34. Kế hoạch hành động khắc phục & phòng ngừa (CAPA)", "page": 68},
        {"title": "35. Quản lý nhãn ép nhiệt / keo mận", "page": 70},
        {"title": "36. Quản lý nút / Snap", "page": 72},
        {"title": "37. Kiểm tra độ bền đính kết (Pulling Test)", "page": 74},
        {"title": "38. An toàn sản phẩm trẻ em", "page": 76},
        {"title": "39. Quản lý độ ẩm thùng carton / hàng hóa", "page": 78},
        {"title": "40. Quản lý hiện trường phòng chống ẩm mốc", "page": 80},
        {"title": "41. Sử dụng máy đo độ ẩm Aqua Boy", "page": 82},
        {"title": "42. Phòng ngừa và quản lý lỗi xơ sợi thừa", "page": 84},
        {"title": "43. Kiểm tra ảo (Virtual Inspection)", "page": 86},
        {"title": "44. FE ảo (Virtual FE)", "page": 88},
        {"title": "45. Họp quy trình đánh giá rủi ro", "page": 90},
        {"title": "Phụ lục 1. Quy trình kiểm tra", "page": 93},
        {"title": "Phụ lục 2. Danh sách kiểm tra nhanh FE", "page": 98},
        {"title": "Phụ lục 3. Báo cáo tự đánh giá nhà máy may", "page": 103},
        {"title": "Phụ lục 4. Bảng kiểm tra phòng ngừa ẩm mốc", "page": 108},
        {"title": "Phụ lục 5. Báo cáo kiểm tra giặt", "page": 113}
    ]
}

UI_LABELS = {
    "KO": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP 목차 (총 50개)",
        "manual_header": "SAE-A QA 표준 운영 절차 (SOP)",
        "page_info": "페이지 위치",
        "total_pages": "전체",
        "no_file": "SOP Handbook 메인 PDF 파일을 찾을 수 없습니다.",
        "auth_title": "🔒 SAE-A QA SOP 보안 인증",
        "auth_desc": "매뉴얼을 열람하려면 시스템 비밀번호를 입력하십시오.",
        "pw_label": "비밀번호 입력",
        "pw_placeholder": "비밀번호를 입력하세요",
        "pw_btn": "인증 확인",
        "pw_error": "비밀번호가 올바르지 않습니다. 다시 입력해 주세요."
    },
    "EN": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP Contents (50 Items)",
        "manual_header": "SAE-A QA Standard Operating Procedure (SOP)",
        "page_info": "Reference Page",
        "total_pages": "Total",
        "no_file": "Cannot find main SOP Handbook PDF file.",
        "auth_title": "🔒 SAE-A QA SOP Security Authentication",
        "auth_desc": "Please enter the system password to access the manual.",
        "pw_label": "Password",
        "pw_placeholder": "Enter password",
        "pw_btn": "Authenticate",
        "pw_error": "Incorrect password. Please try again."
    },
    "VI": {
        "title": "Hệ thống SAE-A QA SOP",
        "toc_header": "Danh mục SOP (Tổng số 50 mục)",
        "manual_header": "Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "page_info": "Trang tham khảo",
        "total_pages": "Tổng số",
        "no_file": "Không tìm thấy tệp PDF SOP chính.",
        "auth_title": "🔒 Xác thực bảo mật SAE-A QA SOP",
        "auth_desc": "Vui lòng nhập mật khẩu hệ thống để xem sổ tay.",
        "pw_label": "Mật khẩu",
        "pw_placeholder": "Nhập mật khẩu",
        "pw_btn": "Xác nhận",
        "pw_error": "Mật khẩu không chính xác. Vui lòng thử lại."
    }
}

def find_main_sop_pdf():
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
def render_pdf_page_as_image(pdf_filename, page_num):
    pdf_path = os.path.join(assets_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        return None
    try:
        doc = fitz.open(pdf_path)
        page_idx = max(0, min(page_num - 1, len(doc) - 1))
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        doc.close()
        return img_bytes
    except Exception:
        return None

# --- 세션 상태 초기화 (비밀번호 인증용) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- 1. 사이드바 (언어 선택) ---
with st.sidebar:
    lang_choice = st.radio("언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang_choice, "KO")
    labels = UI_LABELS[lang_code]
    
    st.markdown(f"### {labels['title']}")
    st.markdown("---")
    
    target_pdf = find_main_sop_pdf()
    
    # 인증 완료 후에만 사이드바에 목차 표시
    if st.session_state.authenticated:
        st.markdown(f"**{labels['toc_header']}**")
        current_toc = TOC_DATA[lang_code]
        toc_titles = [item['title'] for item in current_toc]
        selected_title = st.radio("목차를 선택하세요:", toc_titles, index=0)
        
        selected_index = toc_titles.index(selected_title)
        selected_item = current_toc[selected_index]
        target_page_num = selected_item["page"]
    else:
        target_page_num = 3  # 기본 Introduction 페이지

# --- 2. 메인 화면 ---
st.caption(f"{labels['manual_header']} ({lang_choice})")

if not target_pdf:
    st.error(labels["no_file"])
else:
    doc_check = fitz.open(os.path.join(assets_dir, target_pdf))
    total_pages = len(doc_check)
    doc_check.close()

    # --- 비밀번호 인증 화면 (미인증 시 첫 페이지는 Introduction을 보여주되 인증 창 표시) ---
    if not st.session_state.authenticated:
        st.markdown(f"### {labels['auth_title']}")
        st.markdown(labels['auth_desc'])
        
        with st.form("auth_form"):
            entered_pw = st.text_input(labels['pw_label'], type="password", placeholder=labels['pw_placeholder'])
            submit_btn = st.form_submit_button(labels['pw_btn'])
            
            if submit_btn:
                # 기본 비밀번호: saea2026 (원하시는 비밀번호로 변경 가능)
                if entered_pw == "saea2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error(labels['pw_error'])
        
        st.markdown("---")
        st.markdown("#### 📖 1. Introduction (머리말)")
        intro_bytes = render_pdf_page_as_image(target_pdf, 3)
        if intro_bytes:
            st.image(intro_bytes, use_container_width=True)
            
    else:
        # --- 인증 완료 후 정상적인 SOP 뷰어 작동 ---
        img_bytes = render_pdf_page_as_image(target_pdf, target_page_num)
        
        st.markdown(f"### 📖 {selected_title}")
        
        if img_bytes:
            st.image(img_bytes, use_container_width=True)
        else:
            st.warning("해당 페이지를 이미지로 불러올 수 없습니다.")
            
        st.caption(f"{labels['page_info']}: {target_page_num} / {labels['total_pages']} {total_pages}")