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

# 다국어 목차 데이터셋 (총 50개 항목)
TOC_DATA = {
    "KO": [
        {"title": "1. 머리말", "page": 1},
        {"title": "2. QA/QC 정의", "page": 2},
        {"title": "3. AQL (Acceptable Quality Limit)", "page": 3},
        {"title": "4. Sae-A DCL (Defect Classification List)", "page": 5},
        {"title": "5. 원단 검사/4point System", "page": 7},
        {"title": "6. 원단 방단", "page": 8},
        {"title": "7. 부자재 검사", "page": 11},
        {"title": "8. 패턴 조정 절차 및 관리", "page": 14},
        {"title": "9. PPM Workflow Chart", "page": 17},
        {"title": "10. PP Sample 제작", "page": 19},
        {"title": "11. Internal PPM", "page": 20},
        {"title": "12. PPM", "page": 22},
        {"title": "13. 연단 및 마커 검사", "page": 24},
        {"title": "14. 재단물 검사", "page": 26},
        {"title": "15. 자수/프린트 검사", "page": 28},
        {"title": "16. Pilot Run 검사", "page": 30},
        {"title": "17. Wear & Wash Test", "page": 32},
        {"title": "18. 1st Output 검사", "page": 34},
        {"title": "19. In-Process 검사", "page": 36},
        {"title": "20. Seam allowance 모니터링", "page": 38},
        {"title": "21. In-line 검사", "page": 40},
        {"title": "22. End-line 검사", "page": 42},
        {"title": "23. Finishing 검사", "page": 44},
        {"title": "24. Dupro 검사", "page": 46},
        {"title": "25. Pre-Final 검사", "page": 48},
        {"title": "26. Final 검사", "page": 50},
        {"title": "27. 바늘과 금속 오염 관리", "page": 52},
        {"title": "28. 검침기 사용 설명", "page": 54},
        {"title": "29. 검침기 청소 관리", "page": 56},
        {"title": "30. 9 point Calibration", "page": 58},
        {"title": "31. 핸드 검침기 사용법", "page": 60},
        {"title": "32. 9 point Calibration", "page": 62},
        {"title": "33. 부적격 자재 관리 CNCM", "page": 64},
        {"title": "34. CAPA", "page": 66},
        {"title": "35. 열전사 라벨/심지 부착관리", "page": 68},
        {"title": "36. Snap/Button 관리", "page": 70},
        {"title": "37. Attachment Strength Test 방법", "page": 72},
        {"title": "38. 어린이 제품 안전", "page": 74},
        {"title": "39. Carton/Garment 습도 관리", "page": 76},
        {"title": "40. 곰팡이 발생 방지 현장 관리", "page": 78},
        {"title": "41. Aqua Boy 수분 측정기 사용법", "page": 80},
        {"title": "42. 잔사 불량 예방 및 관리", "page": 82},
        {"title": "43. Virtual Inspection", "page": 84},
        {"title": "44. Virtual FE", "page": 86},
        {"title": "45. Risk Assessment Process Meeting", "page": 88},
        {"title": "부록 1. Inspection Procedure", "page": 91},
        {"title": "부록 2. FE Quick check list", "page": 96},
        {"title": "부록 3. Sewing Factory Self Assessment", "page": 101},
        {"title": "부록 4. Mold Prevention Checklist", "page": 106},
        {"title": "부록 5. Wear & Wash Test Report", "page": 111}
    ],
    "EN": [
        {"title": "1. Introduction", "page": 1},
        {"title": "2. QA/QC Definition", "page": 2},
        {"title": "3. AQL (Acceptable Quality Limit)", "page": 3},
        {"title": "4. Sae-A DCL (Defect Classification List)", "page": 5},
        {"title": "5. Fabric Inspection / 4point System", "page": 7},
        {"title": "6. Fabric Relaxation Management", "page": 8},
        {"title": "7. Trims & Accessories Inspection", "page": 11},
        {"title": "8. Pattern Adjustment & Management", "page": 14},
        {"title": "9. PPM Workflow Chart", "page": 17},
        {"title": "10. PP Sample Making", "page": 19},
        {"title": "11. Internal PPM", "page": 20},
        {"title": "12. PPM Process", "page": 22},
        {"title": "13. Spreading & Marker Inspection", "page": 24},
        {"title": "14. Cut Panel Inspection", "page": 26},
        {"title": "15. Embroidery/Print Inspection", "page": 28},
        {"title": "16. Pilot Run Inspection", "page": 30},
        {"title": "17. Wear & Wash Test", "page": 32},
        {"title": "18. 1st Output Inspection", "page": 34},
        {"title": "19. In-Process Inspection", "page": 36},
        {"title": "20. Seam Allowance Monitoring", "page": 38},
        {"title": "21. In-line Inspection", "page": 40},
        {"title": "22. End-line Inspection", "page": 42},
        {"title": "23. Finishing Inspection", "page": 44},
        {"title": "24. Dupro Inspection", "page": 46},
        {"title": "25. Pre-Final Inspection", "page": 48},
        {"title": "26. Final Inspection", "page": 50},
        {"title": "27. Needle & Metal Contamination Control", "page": 52},
        {"title": "28. Needle Detector Operation", "page": 54},
        {"title": "29. Needle Detector Cleaning & Maintenance", "page": 56},
        {"title": "30. 9 point Calibration", "page": 58},
        {"title": "31. Hand-held Metal Detector Usage", "page": 60},
        {"title": "32. 9 point Calibration (Hand Detector)", "page": 62},
        {"title": "33. Control of Non-conforming Material (CNCM)", "page": 64},
        {"title": "34. CAPA", "page": 66},
        {"title": "35. Heat Transfer Label / Interlining Control", "page": 68},
        {"title": "36. Snap / Button Control", "page": 70},
        {"title": "37. Attachment Strength Test (Pulling Test)", "page": 72},
        {"title": "38. Children's Product Safety", "page": 74},
        {"title": "39. Carton / Garment Humidity Control", "page": 76},
        {"title": "40. Mold Prevention Site Management", "page": 78},
        {"title": "41. Aqua Boy Moisture Meter Usage", "page": 80},
        {"title": "42. Loose Fiber / Residue Prevention", "page": 82},
        {"title": "43. Virtual Inspection", "page": 84},
        {"title": "44. Virtual FE", "page": 86},
        {"title": "45. Risk Assessment Process Meeting", "page": 88},
        {"title": "Appendix 1. Inspection Procedure", "page": 91},
        {"title": "Appendix 2. FE Quick check list", "page": 96},
        {"title": "Appendix 3. Sewing Factory Self Assessment", "page": 101},
        {"title": "Appendix 4. Mold Prevention Checklist", "page": 106},
        {"title": "Appendix 5. Wear & Wash Test Report", "page": 111}
    ],
    "VI": [
        {"title": "1. Giới thiệu (Introduction)", "page": 1},
        {"title": "2. Định nghĩa QA/QC", "page": 2},
        {"title": "3. AQL (Giới hạn chất lượng chấp nhận được)", "page": 3},
        {"title": "4. Danh mục phân loại lỗi Sae-A (DCL)", "page": 5},
        {"title": "5. Kiểm tra vải / Hệ thống 4 điểm", "page": 7},
        {"title": "6. Quản lý thả lỏng vải", "page": 8},
        {"title": "7. Kiểm tra nguyên phụ liệu", "page": 11},
        {"title": "8. Quy trình điều chỉnh và quản lý rập", "page": 14},
        {"title": "9. Biểu đồ quy trình PPM", "page": 17},
        {"title": "10. Làm mẫu PP", "page": 19},
        {"title": "11. PPM nội bộ", "page": 20},
        {"title": "12. Quy trình PPM", "page": 22},
        {"title": "13. Kiểm tra trải vải và sơ đồ", "page": 24},
        {"title": "14. Kiểm tra bán thành phẩm cắt", "page": 26},
        {"title": "15. Kiểm tra thêu/in", "page": 28},
        {"title": "16. Kiểm tra chạy thử (Pilot Run)", "page": 30},
        {"title": "17. Kiểm tra độ bền giặt (Wear & Wash)", "page": 32},
        {"title": "18. Kiểm tra sản phẩm đầu ra đầu tiên", "page": 34},
        {"title": "19. Kiểm tra trong quá trình sản xuất", "page": 36},
        {"title": "20. Theo dõi độ rộng đường may", "page": 38},
        {"title": "21. Kiểm tra chuyền (In-line)", "page": 40},
        {"title": "22. Kiểm tra cuối chuyền (End-line)", "page": 42},
        {"title": "23. Kiểm tra hoàn thiện (Finishing)", "page": 44},
        {"title": "24. Kiểm tra Dupro", "page": 46},
        {"title": "25. Kiểm tra tiền xuất hàng (Pre-Final)", "page": 48},
        {"title": "26. Kiểm tra cuối cùng (Final)", "page": 50},
        {"title": "27. Quản lý kim và nhiễm bẩn kim loại", "page": 52},
        {"title": "28. Vận hành máy dò kim", "page": 54},
        {"title": "29. Vệ sinh và bảo dưỡng máy dò kim", "page": 56},
        {"title": "30. Hiệu chuẩn 9 điểm", "page": 58},
        {"title": "31. Sử dụng máy dò kim cầm tay", "page": 60},
        {"title": "32. Hiệu chuẩn 9 điểm (Máy cầm tay)", "page": 62},
        {"title": "33. Quản lý nguyên vật liệu không phù hợp (CNCM)", "page": 64},
        {"title": "34. Kế hoạch hành động khắc phục & phòng ngừa (CAPA)", "page": 66},
        {"title": "35. Quản lý nhãn ép nhiệt / keo mận", "page": 68},
        {"title": "36. Quản lý nút / Snap", "page": 70},
        {"title": "37. Kiểm tra độ bền đính kết (Pulling Test)", "page": 72},
        {"title": "38. An toàn sản phẩm trẻ em", "page": 74},
        {"title": "39. Quản lý độ ẩm thùng carton / hàng hóa", "page": 76},
        {"title": "40. Quản lý hiện trường phòng chống ẩm mốc", "page": 78},
        {"title": "41. Sử dụng máy đo độ ẩm Aqua Boy", "page": 80},
        {"title": "42. Phòng ngừa và quản lý lỗi xơ sợi thừa", "page": 82},
        {"title": "43. Kiểm tra ảo (Virtual Inspection)", "page": 84},
        {"title": "44. FE ảo (Virtual FE)", "page": 86},
        {"title": "45. Họp quy trình đánh giá rủi ro", "page": 88},
        {"title": "Phụ lục 1. Quy trình kiểm tra", "page": 91},
        {"title": "Phụ lục 2. Danh sách kiểm tra nhanh FE", "page": 96},
        {"title": "Phụ lục 3. Báo cáo tự đánh giá nhà máy may", "page": 101},
        {"title": "Phụ lục 4. Bảng kiểm tra phòng ngừa ẩm mốc", "page": 106},
        {"title": "Phụ lục 5. Báo cáo kiểm tra giặt", "page": 111}
    ]
}

UI_LABELS = {
    "KO": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP 목차 (총 50개)",
        "manual_header": "SAE-A QA 표준 운영 절차 (SOP)",
        "search_label": "SOP 키워드 검색",
        "search_placeholder": "검색어를 입력하세요 (예: AQL, 핸드 검침기, 어린이)",
        "page_info": "페이지 위치",
        "total_pages": "전체",
        "no_file": "SOP Handbook 메인 PDF 파일을 찾을 수 없습니다.",
        "auth_title": "🔒 SAE-A QA SOP 보안 인증",
        "auth_desc": "매뉴얼을 열람하려면 시스템 비밀번호를 입력하십시오.",
        "pw_label": "비밀번호 입력",
        "pw_placeholder": "비밀번호를 입력하세요",
        "pw_btn": "인증 확인",
        "pw_error": "비밀번호가 올바르지 않습니다. 다시 입력해 주세요.",
        "view_mode": "열람 모드 선택",
        "mode_img": "🖼️ PDF 원본 이미지 보기",
        "mode_txt": "🌐 선택 언어 자동 번역 텍스트 보기"
    },
    "EN": {
        "title": "SAE-A QA SOP System",
        "toc_header": "SOP Contents (50 Items)",
        "manual_header": "SAE-A QA Standard Operating Procedure (SOP)",
        "search_label": "Search SOP Keywords",
        "search_placeholder": "Enter search term (e.g. AQL, Needle, Children)",
        "page_info": "Reference Page",
        "total_pages": "Total",
        "no_file": "Cannot find main SOP Handbook PDF file.",
        "auth_title": "🔒 SAE-A QA SOP Security Authentication",
        "auth_desc": "Please enter the system password to access the manual.",
        "pw_label": "Password",
        "pw_placeholder": "Enter password",
        "pw_btn": "Authenticate",
        "pw_error": "Incorrect password. Please try again.",
        "view_mode": "Select View Mode",
        "mode_img": "🖼️ View Original PDF Image",
        "mode_txt": "🌐 View Translated Text"
    },
    "VI": {
        "title": "Hệ thống SAE-A QA SOP",
        "toc_header": "Danh mục SOP (Tổng số 50 mục)",
        "manual_header": "Quy trình vận hành chuẩn SAE-A QA (SOP)",
        "search_label": "Tìm kiếm từ khóa SOP",
        "search_placeholder": "Nhập từ khóa (Ví dụ: AQL, Kiểm tra, Trẻ em)",
        "page_info": "Trang tham khảo",
        "total_pages": "Tổng số",
        "no_file": "Không tìm thấy tệp PDF SOP chính.",
        "auth_title": "🔒 Xác thực bảo mật SAE-A QA SOP",
        "auth_desc": "Vui lòng nhập mật khẩu hệ thống để xem sổ tay.",
        "pw_label": "Mật khẩu",
        "pw_placeholder": "Nhập mật khẩu",
        "pw_btn": "Xác nhận",
        "pw_error": "Mật khẩu không chính xác. Vui lòng thử lại.",
        "view_mode": "Chọn chế độ xem",
        "mode_img": "🖼️ Xem ảnh PDF gốc",
        "mode_txt": "🌐 Xem văn bản dịch tự động"
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

@st.cache_data
def extract_and_translate_page(pdf_filename, page_num, target_lang):
    pdf_path = os.path.join(assets_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        return ""
    try:
        doc = fitz.open(pdf_path)
        page_idx = max(0, min(page_num - 1, len(doc) - 1))
        text = doc[page_idx].get_text() or ""
        doc.close()
        
        if not text.strip():
            return "No text available on this page."
            
        if target_lang == "KO":
            return text
            
        dest = "en" if target_lang == "EN" else "vi"
        translator = GoogleTranslator(source='auto', target=dest)
        chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n\n".join(translated_chunks)
    except Exception as e:
        return f"Translation error: {e}"

# --- 세션 상태 초기화 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- 1. 사이드바 (언어 선택 및 목차) ---
with st.sidebar:
    lang_choice = st.radio("언어 선택 / Language", ["한국어", "English", "Tiếng Việt"])
    lang_map = {"한국어": "KO", "English": "EN", "Tiếng Việt": "VI"}
    lang_code = lang_map.get(lang_choice, "KO")
    labels = UI_LABELS[lang_code]
    
    st.markdown(f"### {labels['title']}")
    st.markdown("---")
    
    target_pdf = find_main_sop_pdf()
    
    if st.session_state.authenticated:
        st.markdown(f"**{labels['toc_header']}**")
        current_toc = TOC_DATA[lang_code]
        toc_titles = [item['title'] for item in current_toc]
        selected_title = st.radio("목차를 선택하세요:", toc_titles, index=0)
        
        selected_index = toc_titles.index(selected_title)
        selected_item = current_toc[selected_index]
        target_page_num = selected_item["page"]
    else:
        target_page_num = 1

# --- 2. 메인 화면 ---
st.caption(f"{labels['manual_header']} ({lang_choice})")

if not target_pdf:
    st.error(labels["no_file"])
else:
    doc_check = fitz.open(os.path.join(assets_dir, target_pdf))
    total_pages = len(doc_check)
    doc_check.close()

    # --- 비밀번호 인증 화면 ---
    if not st.session_state.authenticated:
        st.markdown(f"### {labels['auth_title']}")
        st.markdown(labels['auth_desc'])
        
        with st.form("auth_form"):
            entered_pw = st.text_input(labels['pw_label'], type="password", placeholder=labels['pw_placeholder'])
            submit_btn = st.form_submit_button(labels['pw_btn'])
            
            if submit_btn:
                if entered_pw == "saea2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error(labels['pw_error'])
        
        st.markdown("---")
        st.markdown(f"#### 📖 {TOC_DATA[lang_code][0]['title']}")
        intro_bytes = render_pdf_page_as_image(target_pdf, 1)
        if intro_bytes:
            st.image(intro_bytes, use_container_width=True)
            
    else:
        # --- 검색창 및 열람 모드 항상 상단 노출 ---
        search_query = st.text_input(labels["search_label"], placeholder=labels["search_placeholder"])
        view_mode = st.radio(labels["view_mode"], [labels["mode_img"], labels["mode_txt"]], horizontal=True)
        st.markdown("---")
        
        if search_query.strip():
            st.markdown(f"#### Search Results / Kết quả tìm kiếm: '{search_query}'")
            doc = fitz.open(os.path.join(assets_dir, target_pdf))
            found = False
            for i, page in enumerate(doc):
                raw_txt = page.get_text() or ""
                # 다국어 검색 지원을 위해 텍스트 번역 대조
                search_target = raw_txt
                if lang_code == "EN":
                    try:
                        search_target = GoogleTranslator(source='auto', target='en').translate(raw_txt[:1500])
                    except:
                        pass
                elif lang_code == "VI":
                    try:
                        search_target = GoogleTranslator(source='auto', target='vi').translate(raw_txt[:1500])
                    except:
                        pass
                
                if search_query.lower() in search_target.lower():
                    found = True
                    with st.expander(f"Page {i+1} Match"):
                        img_b = render_pdf_page_as_image(target_pdf, i+1)
                        if img_b:
                            st.image(img_b, use_container_width=True)
            doc.close()
            if not found:
                st.warning("No matching content found. / Không tìm thấy nội dung phù hợp.")
        else:
            st.markdown(f"### 📖 {selected_title}")
            
            if view_mode == labels["mode_img"]:
                img_bytes = render_pdf_page_as_image(target_pdf, target_page_num)
                if img_bytes:
                    st.image(img_bytes, use_container_width=True)
                else:
                    st.warning("Cannot load page image.")
            else:
                with st.spinner("Translating text... / Đang dịch văn bản..."):
                    translated_text = extract_and_translate_page(target_pdf, target_page_num, lang_code)
                with st.container(border=True):
                    st.markdown(translated_text)
                    
            st.caption(f"{labels['page_info']}: {target_page_num} / {labels['total_pages']} {total_pages}")