import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="자동 제안서 생성기", layout="wide")

st.title("📊 맞춤형 경영컨설팅 제안서 자동 생성기")
st.write("좌측에 기업별 맞춤 정보를 입력하시면, 우측에 고정 템플릿이 결합된 제안서가 실시간으로 완성됩니다.")

# 화면 분할 (입력폼 1 : 미리보기 2)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 1. 기본 정보 입력")
    
    # 제안사 및 고객사 정보
    my_company_name = st.text_input("제안사 이름 (우측 하단 표기)", "주식회사 제이원")
    client_name = st.text_input("고객사 이름 (타이틀 표기)", "(주)영광산업기계")
    
    # 현재 상시 근로자 수 (지원금 조건 판별용)
    current_employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3, step=1, help="5인 미만일 경우 청년도약장려금 등 일부 지원금 신청이 제한됩니다.")
    
    st.info("💡 제안 일자는 파일을 열 때마다 오늘 날짜로 자동 변경되도록 스크립트가 적용되었습니다.")

    st.subheader("📝 2. 맞춤 컨설팅 정보")
    
    # 업종 코드
    industry_code = st.text_input("업종 코드 및 상태 (예: [21812] 뿌리기업 해당)", "[21812] 뿌리기업 해당")
    
    # 제안 내용 (여러 줄 입력)
    proposal_input = st.text_area(
        "핵심 컨설팅 제안 내용 (줄바꿈으로 구분)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장 진입에 따른 행정/노무 정비 및 지원금 수령"
    )
    # 입력받은 텍스트를 HTML 리스트(<li>) 형태로 변환
    proposal_items = "".join([f"<li class='mb-2 flex items-start'><span class='text-blue-500 mr-2'>✔</span><span class='break-keep'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    # 스케쥴표 시작 월 설정
    start_month = st.number_input("스케쥴 시작 월 (숫자만 입력)", min_value=1, max_value=12, value=4)
    
    # 스케쥴 달 계산 (인증 기간을 3개월로 연장, 12월이 넘어가면 1월로 순환)
    m1 = start_month
    m2 = (start_month % 12) + 1                 # 인사/노무: 1개월 소요
    m3 = (start_month + 3) % 12 + 1             # 인증 획득: 3개월 소요
    m4 = (start_month + 4) % 12 + 1             # 재무/세무: 1개월 소요

    st.subheader("📝 3. 고용지원금 자동 계산기 (6대 핵심 지원금)")
    st.write(f"현재 근로자 수({current_employees}명)를 기준으로 수령 가능 여부와 금액이 계산됩니다.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        youth_count = st.number_input("① 청년도약 (만15~34세)", min_value=0, value=1, step=1)
        continuous_count = st.number_input("④ 고령자 계속고용 (정년)", min_value=0, value=0, step=1)
    with col_b:
        senior_count = st.number_input("② 시니어인턴 (만60세)", min_value=0, value=1, step=1)
        disabled_count = st.number_input("⑤ 장애인 신규고용", min_value=0, value=0, step=1)
    with col_c:
        women_count = st.number_input("③ 새일여성 (경단녀)", min_value=0, value=1, step=1)
        parental_count = st.number_input("⑥ 육아휴직 대체인력", min_value=0, value=0, step=1)

    # ==========================================
    # 지원금 요건 판단 및 로직 처리 (최신 규정)
    # ==========================================
    
    # 1. 청년일자리도약장려금 (원칙: 5인 이상)
    youth_eligible = current_employees >= 5
    youth_subsidy_per_person = 1200 if youth_eligible else 0
    youth_total = youth_count * youth_subsidy_per_person
    
    # 2. 시니어인턴십 (보통 1인 이상 가능)
    senior_eligible = current_employees >= 1
    senior_subsidy_per_person = 240 if senior_eligible else 0
    senior_total = senior_count * senior_subsidy_per_person
    
    # 3. 새일여성인턴지원금 (1인 이상 가능 기본 세팅)
    women_eligible = current_employees >= 1
    women_subsidy_per_person = 380 if women_eligible else 0
    women_total = women_count * women_subsidy_per_person

    # 4. 고령자 계속고용장려금 (정년제도 운영 기업, 월 30만 * 24개월 = 720만)
    continuous_eligible = current_employees >= 1
    continuous_subsidy_per_person = 720 if continuous_eligible else 0
    continuous_total = continuous_count * continuous_subsidy_per_person

    # 5. 장애인 신규고용장려금 (경/중증, 성별 따라 상이하나 평균적 720만 산정)
    disabled_eligible = current_employees >= 1
    disabled_subsidy_per_person = 720 if disabled_eligible else 0
    disabled_total = disabled_count * disabled_subsidy_per_person

    # 6. 육아휴직 대체인력 지원금 (최대 월 80만 * 12개월 = 960만)
    parental_eligible = current_employees >= 1
    parental_subsidy_per_person = 960 if parental_eligible else 0
    parental_total = parental_count * parental_subsidy_per_person

    # 총액 계산
    total_subsidy = youth_total + senior_total + women_total + continuous_total + disabled_total + parental_total

    # HTML 카드 생성 함수 (조건부 렌더링)
    def generate_subsidy_card(title, target, eligible, max_amount_str, scheduled_count, total_amount):
        if eligible:
            return f"""
            <div class="bg-amber-50 p-5 rounded-xl border border-amber-100 shadow-sm relative overflow-hidden transition-all print-break-inside-avoid">
                <div class="absolute right-0 top-0 bg-amber-200 text-amber-800 text-xs font-bold px-3 py-1 rounded-bl-lg">예정: {scheduled_count}명</div>
                <div class="inline-block bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded mb-2">신청 가능</div>
                <h3 class="font-bold text-amber-800 mb-1 tracking-tight">{title}</h3>
                <p class="text-xs text-amber-700 mb-3">대상: {target}</p>
                <p class="font-bold text-amber-900 text-2xl">{total_amount:,}<span class="text-base font-normal"> 만원</span></p>
                <p class="text-[11px] text-amber-700 mt-1 break-keep">※ {max_amount_str}</p>
            </div>
            """
        else:
            return f"""
            <div class="bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden opacity-70 grayscale print-break-inside-avoid">
                <div class="absolute right-0 top-0 bg-slate-200 text-slate-600 text-xs font-bold px-3 py-1 rounded-bl-lg">예정: {scheduled_count}명</div>
                <div class="inline-block bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded mb-2">신청 불가 (요건 미달)</div>
                <h3 class="font-bold text-slate-600 mb-1 tracking-tight">{title}</h3>
                <p class="text-xs text-slate-500 mb-3">대상: {target}</p>
                <p class="font-bold text-slate-400 text-2xl line-through">0<span class="text-base font-normal"> 만원</span></p>
                <p class="text-[11px] text-red-500 mt-1 break-keep">※ 현재 5인 미만 사업장으로 원칙적 신청 불가</p>
            </div>
            """

    # 카드 생성
    card_youth = generate_subsidy_card("청년일자리도약장려금", "만 15~34세 청년", youth_eligible, "1인 최대 1,200만 원 (2년)", youth_count, youth_total)
    card_senior = generate_subsidy_card("시니어인턴십", "만 60세 이상 신규채용", senior_eligible, "1인 최대 약 240만 원", senior_count, senior_total)
    card_women = generate_subsidy_card("새일여성인턴지원금", "경력단절여성 등", women_eligible, "1인 최대 380만 원", women_count, women_total)
    card_continuous = generate_subsidy_card("고령자계속고용장려금", "정년 도달자 재고용 등", continuous_eligible, "1인 최대 720만 원 (2년)", continuous_count, continuous_total)
    card_disabled = generate_subsidy_card("장애인 신규고용장려금", "장애인 근로자 (경증/중증)", disabled_eligible, "1인 최대 720만 원 (추산)", disabled_count, disabled_total)
    card_parental = generate_subsidy_card("육아휴직 대체인력지원", "육아휴직자 발생 시 대체", parental_eligible, "1인 최대 960만 원 (1년)", parental_count, parental_total)

    st.subheader("📝 4. 노무 기준 설정 (최저임금)")
    st.write("해당 연도의 최저시급을 입력하면 월 환산액(209시간 기준)이 자동 계산되어 반영됩니다.")
    min_wage = st.number_input("현재 최저시급 (원)", min_value=0, value=10030, step=10)
    
    # 209시간 기준 월 최저임금 자동 계산
    monthly_wage = min_wage * 209

# HTML 템플릿에 변수 및 고정 데이터 결합
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{client_name} 경영컨설팅 제안서</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(5px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .text-gradient {{
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-image: linear-gradient(to right, #2563eb, #059669);
        }}
        ::-webkit-scrollbar {{ display: none; }} /* 스크롤바 숨김 */
        
        .check-list li::before {{
            content: '✔';
            color: #0ea5e9;
            margin-right: 8px;
            font-weight: bold;
        }}
        .danger-list li::before {{
            content: '⚠️';
            margin-right: 8px;
        }}

        /* ========================================= */
        /* 🖨️ 강제 인쇄 모드 제어 CSS (JS 연동) */
        /* ========================================= */
        body.force-print-mode .tab-content {{ 
            display: block !important; 
            opacity: 1 !important;
            margin-bottom: 2rem !important;
        }}
        body.force-print-mode .tab-btn {{ display: none !important; }}
        body.force-print-mode #print_btn {{ display: none !important; }}
        
        @media print {{
            body {{ background-color: #ffffff !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            
            /* 강제 인쇄 모드 활성화 시 각 탭 영역 설정 */
            body.force-print-mode #tab_proposal, 
            body.force-print-mode #tab_labor, 
            body.force-print-mode #tab_fixed, 
            body.force-print-mode #tab_schedule {{
                display: block !important;
                page-break-before: always;
                break-before: page;
            }}
            /* 첫 번째 탭은 새 페이지 안 넘김 */
            body.force-print-mode #tab_proposal {{ page-break-before: avoid; break-before: auto; }}
            
            /* 박스가 중간에 잘리는 현상 방지 */
            .print-break-inside-avoid, .bg-white, .bg-amber-50, .bg-emerald-50, .bg-red-50 {{
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #e2e8f0 !important; }}
        }}
    </style>
</head>
<body class="antialiased">

    <!-- Header -->
    <header class="bg-slate-900 text-white pt-12 pb-12 px-8 relative">
        <div class="absolute inset-0 opacity-20" style="background: radial-gradient(circle at top right, #3b82f6, transparent);"></div>
        <div class="max-w-5xl mx-auto relative z-10 flex flex-col md:flex-row justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-sm mb-2">MASTER CONSULTING PLAN</p>
                <h1 class="text-4xl font-bold mb-3 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 font-light">업종코드: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="mt-4 md:mt-0 text-right flex flex-col items-end">
                <!-- 🖨️ 전용 인쇄 버튼 추가 -->
                <button id="print_btn" onclick="executePrint()" class="mb-4 bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold py-2 px-4 rounded shadow transition-colors flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
                    전체 내용 인쇄하기
                </button>
                <p class="text-slate-400 text-sm">제안일자: <span id="auto_date"></span></p>
                <p class="text-xl font-bold mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <!-- Navigation -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div class="max-w-5xl mx-auto px-6 flex space-x-8 overflow-x-auto">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-4 font-bold text-blue-600 border-b-2 border-blue-600 whitespace-nowrap">핵심 제안 내용</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-4 font-medium text-slate-500 border-b-2 border-transparent whitespace-nowrap">노무 및 비과세 설계</button>
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-4 font-medium text-slate-500 border-b-2 border-transparent whitespace-nowrap">인증/자금/지원금 분석</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-medium text-slate-500 border-b-2 border-transparent whitespace-nowrap">마스터 스케쥴</button>
        </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-6 py-8">
        
        <!-- [가변] TAB 1: 핵심 제안 내용 -->
        <div id="tab_proposal" class="tab-content active">
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
                <h2 class="text-2xl font-bold text-slate-800 mb-6 pb-4 border-b border-slate-100">💡 {client_name} 전용 솔루션 구조 검토</h2>
                <ul class="text-lg text-slate-700 leading-relaxed space-y-2">
                    {proposal_items}
                </ul>
            </div>
        </div>

        <!-- [노무] TAB 2: 노무 및 비과세 설계 -->
        <div id="tab_labor" class="tab-content">
            
            <!-- 최저임금 & 근로계약서 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 print-break-inside-avoid">
                <!-- 최저임금 현황 (자동 연동) -->
                <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 relative overflow-hidden">
                    <div class="absolute -right-4 -top-4 w-24 h-24 bg-blue-50 rounded-full z-0"></div>
                    <div class="relative z-10">
                        <h2 class="text-lg font-bold text-blue-800 mb-4 border-b pb-2">⏱️ 현재 최저임금 현황 ({min_wage:,}원 기준)</h2>
                        <div class="flex justify-between items-end mb-4">
                            <p class="text-slate-600 font-medium">최저 시급</p>
                            <p class="text-2xl font-bold text-blue-900">{min_wage:,}<span class="text-base font-normal text-slate-500"> 원</span></p>
                        </div>
                        <div class="flex justify-between items-end bg-blue-50 p-3 rounded-lg">
                            <p class="text-blue-800 font-bold">월 환산액 <span class="text-xs font-normal">(주 40시간/209시간 기준)</span></p>
                            <p class="text-2xl font-bold text-blue-600">{monthly_wage:,}<span class="text-base font-normal"> 원</span></p>
                        </div>
                        <p class="text-xs text-slate-400 mt-3 break-keep">※ 주휴수당을 포함한 월 기본급 세팅 시 반드시 위 금액 이상으로 설계해야 노동부 점검 시 법 위반을 피할 수 있습니다.</p>
                    </div>
                </div>

                <!-- 근로계약서 미작성 리스크 -->
                <div class="bg-red-50 rounded-2xl shadow-sm border border-red-100 p-6">
                    <h2 class="text-lg font-bold text-red-800 mb-4 border-b border-red-200 pb-2">🚨 근로계약서의 중요성 및 미작성 리스크</h2>
                    <p class="text-sm text-red-900 mb-3 break-keep">근로계약서는 사업주를 보호하는 <b>'최소한의 방어막'</b>입니다. 미작성 및 미교부 시 즉각적인 처벌 대상이 됩니다.</p>
                    <ul class="text-sm text-red-800 space-y-2 danger-list font-medium">
                        <li>정규직 근로자 미작성 시: <span class="bg-red-200 px-1 rounded">벌금 최대 500만 원 (형사처벌)</span></li>
                        <li>기간제/단시간 근로자 미작성 시: <span class="bg-red-200 px-1 rounded">과태료 최대 500만 원 (즉시 부과)</span></li>
                        <li>임금체불 및 부당해고 등 분쟁 발생 시, 계약서 부재는 100% 사업주에게 불리하게 작용합니다.</li>
                    </ul>
                </div>
            </div>

            <!-- 5인 미만 vs 5인 이상 -->
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-8 print-break-inside-avoid">
                <h2 class="text-lg font-bold text-slate-800 mb-4 pl-2 border-l-4 border-slate-800">🏢 상시근로자 5인 미만 vs 5인 이상 노무관리 핵심 차이</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left">
                        <thead class="bg-slate-100 text-slate-700">
                            <tr>
                                <th class="px-4 py-3 rounded-tl-lg font-bold">구분 (핵심 노동법)</th>
                                <th class="px-4 py-3 font-bold text-emerald-700">5인 미만 사업장</th>
                                <th class="px-4 py-3 rounded-tr-lg font-bold text-red-700">5인 이상 사업장 (리스크 증가)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 text-slate-600">
                            <tr>
                                <td class="px-4 py-3 font-medium text-slate-800">연장/야간/휴일 가산수당</td>
                                <td class="px-4 py-3">지급 의무 없음 (1.0배만 지급)</td>
                                <td class="px-4 py-3 font-bold text-red-600">통상임금의 50% 가산 지급 (1.5배)</td>
                            </tr>
                            <tr>
                                <td class="px-4 py-3 font-medium text-slate-800">연차유급휴가</td>
                                <td class="px-4 py-3">부여 의무 없음</td>
                                <td class="px-4 py-3 font-bold text-red-600">법정 연차휴가 발생 (미사용 시 수당 지급)</td>
                            </tr>
                            <tr>
                                <td class="px-4 py-3 font-medium text-slate-800">부당해고 구제신청</td>
                                <td class="px-4 py-3">적용 제외 (해고 비교적 자유로움)</td>
                                <td class="px-4 py-3 font-bold text-red-600">노동위원회 구제신청 가능 (정당한 사유 必)</td>
                            </tr>
                            <tr>
                                <td class="px-4 py-3 font-medium text-slate-800">휴업수당</td>
                                <td class="px-4 py-3">지급 의무 없음</td>
                                <td class="px-4 py-3 font-bold text-red-600">회사 귀책사유 휴업 시 평균임금 70% 지급</td>
                            </tr>
                            <tr>
                                <td class="px-4 py-3 font-medium text-slate-800">대체공휴일 (유급휴일)</td>
                                <td class="px-4 py-3">적용 제외</td>
                                <td class="px-4 py-3 font-bold text-red-600">빨간날 유급휴일 보장 의무 적용</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 print-break-inside-avoid">
                <!-- 주요 법정 수당 -->
                <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-4 pl-2 border-l-4 border-amber-500">⏰ 주요 법정 가산수당 (5인 이상)</h2>
                    <p class="text-sm text-slate-600 mb-4">포괄임금제를 세팅하더라도 아래 가산수당의 구조를 명확히 근로계약서에 명시해야 임금체불 리스크를 벗어납니다.</p>
                    <ul class="text-sm space-y-3 check-list text-slate-700">
                        <li><b>연장근로수당:</b> 법정근로시간(1일 8시간, 주 40시간) 초과 근로 시 <b>[통상임금의 50% 가산]</b></li>
                        <li><b>야간근로수당:</b> 밤 10시 ~ 다음 날 아침 6시 사이 근로 시 <b>[통상임금의 50% 가산]</b></li>
                        <li><b>휴일근로수당:</b> 법정휴일 및 약정휴일 근로 시 8시간 이내 <b>[50% 가산]</b>, 8시간 초과분 <b>[100% 가산]</b></li>
                    </ul>
                </div>

                <!-- 4대보험 비과세 -->
                <div class="bg-emerald-50 rounded-2xl shadow-sm border border-emerald-200 p-6">
                    <h2 class="text-lg font-bold text-emerald-800 mb-4 border-b border-emerald-200 pb-2">💎 4대보험 및 소득세 절감을 위한 '비과세 항목'</h2>
                    <p class="text-sm text-emerald-900 mb-4 break-keep">세금과 4대보험료(노사 합산 약 19%) 산정 기준에서 제외되는 합법적인 비과세 수당을 세팅하여 <b>매월 고정비를 즉각적으로 절감</b>합니다.</p>
                    <ul class="text-sm space-y-2 text-emerald-800 font-medium bg-white p-4 rounded-lg">
                        <li class="flex justify-between items-center border-b border-slate-100 pb-2">
                            <span>🍚 식대 (중식대)</span> <span class="bg-emerald-100 text-emerald-700 px-2 rounded">월 최대 20만 원</span>
                        </li>
                        <li class="flex justify-between items-center border-b border-slate-100 py-2">
                            <span>🚗 자가운전보조금 (본인 명의 차량)</span> <span class="bg-emerald-100 text-emerald-700 px-2 rounded">월 최대 20만 원</span>
                        </li>
                        <li class="flex justify-between items-center border-b border-slate-100 py-2">
                            <span>👶 출산·보육수당 (만 6세 이하 자녀)</span> <span class="bg-emerald-100 text-emerald-700 px-2 rounded">월 최대 20만 원</span>
                        </li>
                        <li class="flex justify-between items-center pt-2">
                            <span>🔬 연구보조비 (연구부서 설립 인가 시)</span> <span class="bg-emerald-100 text-emerald-700 px-2 rounded">월 최대 20만 원</span>
                        </li>
                    </ul>
                    <p class="text-[11px] text-emerald-600 mt-3 text-right">※ 1인당 월 40~60만 원 비과세 세팅 시, 연간 상당한 고정비 절감 효과 발생</p>
                </div>
            </div>
            
        </div>

        <!-- [복합] TAB 3: 인증 / 자금 / 노무지원금 -->
        <div id="tab_fixed" class="tab-content">
            
            <!-- 1. 6대 지원금 동적 계산 항목 -->
            <div class="mb-10 print-break-inside-avoid">
                <h2 class="text-xl font-bold text-slate-800 mb-2 pl-2 border-l-4 border-amber-500">
                    💰 맞춤형 고용지원금 시뮬레이션
                </h2>
                <p class="text-sm text-slate-500 mb-4 pl-3">현재 상시근로자 {current_employees}명 기준, 총 <span class="font-bold text-blue-600">{total_subsidy:,}만 원</span>의 지원금 수령이 가능합니다.</p>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {card_youth}
                    {card_senior}
                    {card_women}
                    {card_continuous}
                    {card_disabled}
                    {card_parental}
                </div>
            </div>

            <!-- 2. 고정 인증 항목 (추가 인증 포함) -->
            <div class="mb-10 print-break-inside-avoid">
                <h2 class="text-xl font-bold text-slate-800 mb-4 pl-2 border-l-4 border-blue-500">🏆 기업 핵심 인증별 혜택</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- 기존 4개 -->
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="font-bold text-blue-700 mb-2">기업부설연구소 / 전담부서</h3>
                        <ul class="text-sm text-slate-600 space-y-1">
                            <li>• 연구원 인당 급여의 25% 법인세 세액공제</li>
                            <li>• 연구원 인당 급여 중 월 20만원 비과세 처리</li>
                        </ul>
                    </div>
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="font-bold text-blue-700 mb-2">벤처기업 인증</h3>
                        <ul class="text-sm text-slate-600 space-y-1">
                            <li>• 창업 3년 미만 시 5년간 법인세 50% 감면</li>
                            <li>• 부동산(공장 등) 취등록세 75% 감면 혜택</li>
                        </ul>
                    </div>
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="font-bold text-blue-700 mb-2">소재·부품·장비 (소부장) 인증</h3>
                        <ul class="text-sm text-slate-600 space-y-1">
                            <li>• 한국은행 금융중개지원 대출 및 지원금 우대</li>
                            <li>• 병역특례 및 외국인 고용 가점 부여</li>
                        </ul>
                    </div>
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="font-bold text-blue-700 mb-2">뿌리기업 인증</h3>
                        <ul class="text-sm text-slate-600 space-y-1">
                            <li>• 정책자금 대출 실행 시 이자율 인하 및 한도 상향</li>
                            <li>• 외국인 채용 제한 완화 및 전용 지원금 신청 가능</li>
                        </ul>
                    </div>
                    <!-- 신규 추가 3개 -->
                    <div class="bg-blue-50 p-5 rounded-xl border border-blue-100 shadow-sm">
                        <h3 class="font-bold text-blue-800 mb-2">여성기업 인증</h3>
                        <ul class="text-sm text-blue-900 space-y-1">
                            <li>• 공공기관 수의계약 한도 5천만 원으로 확대</li>
                            <li>• 공공기관 의무구매 대상 및 입찰 가점 부여 혜택</li>
                        </ul>
                    </div>
                    <div class="bg-blue-50 p-5 rounded-xl border border-blue-100 shadow-sm">
                        <h3 class="font-bold text-blue-800 mb-2">직접생산확인서</h3>
                        <ul class="text-sm text-blue-900 space-y-1">
                            <li>• 조달청(나라장터) 및 공공기관 입찰 참여 필수 요건</li>
                            <li>• 중소기업간 경쟁제품 지정 시 공공 조달시장 진입 가능</li>
                        </ul>
                    </div>
                    <div class="bg-blue-50 p-5 rounded-xl border border-blue-100 shadow-sm md:col-span-2 lg:col-span-1">
                        <h3 class="font-bold text-blue-800 mb-2">공장등록</h3>
                        <ul class="text-sm text-blue-900 space-y-1">
                            <li>• 정부 주요 지원사업 및 융자 신청 시 필수 기본 요건</li>
                            <li>• 제조업 기반 각종 세제 혜택 및 전력 요금 감면 적용</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- 3. 고정 자금 종류 및 금리 현황 -->
            <div class="print-break-inside-avoid">
                <h2 class="text-xl font-bold text-slate-800 mb-4 pl-2 border-l-4 border-emerald-500">🏦 기관별 정책/보증 자금 및 예상 금리 구조</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    
                    <div class="bg-emerald-50 p-5 rounded-xl border border-emerald-100">
                        <h3 class="font-bold text-emerald-800 mb-2">1. 중소벤처기업진흥공단</h3>
                        <p class="text-sm text-emerald-700 font-bold mb-2 pb-2 border-b border-emerald-200">예상: 연 2.5% ~ 3.5% 내외</p>
                        <ul class="text-xs text-emerald-700 space-y-1 break-keep">
                            <li>• <b>성격:</b> 직접 대출 (정책자금 기준금리 적용)</li>
                            <li>• <b>특징:</b> 시중보다 저렴한 고정/변동 금리, 창업기반 및 신성장 자금 등 시설/운전자금 지원</li>
                        </ul>
                    </div>

                    <div class="bg-emerald-50 p-5 rounded-xl border border-emerald-100">
                        <h3 class="font-bold text-emerald-800 mb-2">2. 신용/기술보증기금 (신보/기보)</h3>
                        <p class="text-sm text-emerald-700 font-bold mb-2 pb-2 border-b border-emerald-200">예상: 연 4.0% ~ 5.5% + 보증료</p>
                        <ul class="text-xs text-emerald-700 space-y-1 break-keep">
                            <li>• <b>성격:</b> 보증서 발급 대출 (보증료율 0.5~1.5% 별도)</li>
                            <li>• <b>특징:</b> 담보력이 부족해도 신용도 및 기술 등급 평가를 통해 1금융권 대출 가능</li>
                        </ul>
                    </div>

                    <div class="bg-emerald-50 p-5 rounded-xl border border-emerald-100">
                        <h3 class="font-bold text-emerald-800 mb-2">3. 일반 시중 은행</h3>
                        <p class="text-sm text-emerald-700 font-bold mb-2 pb-2 border-b border-emerald-200">예상: 연 4.5% ~ 6.5% 내외</p>
                        <ul class="text-xs text-emerald-700 space-y-1 break-keep">
                            <li>• <b>성격:</b> 자체 신용 및 담보 대출</li>
                            <li>• <b>특징:</b> 금리는 다소 높을 수 있으나, 재무제표가 양호할 경우 자체 한도 산출이 빠름</li>
                        </ul>
                    </div>

                    <div class="bg-emerald-50 p-5 rounded-xl border border-emerald-100 lg:col-span-3">
                        <h3 class="font-bold text-emerald-800 mb-2">4. 지자체 정책자금 (도 자금 / 시 자금 이차보전)</h3>
                        <p class="text-sm text-emerald-700 font-bold mb-2 pb-2 border-b border-emerald-200">실질 체감 금리: 연 1.5% ~ 3.5% 수준</p>
                        <div class="flex flex-col md:flex-row gap-4 mt-2">
                            <ul class="text-xs text-emerald-700 space-y-1 break-keep flex-1">
                                <li>• <b>성격:</b> 시중 은행 대출 시 발생되는 이자의 일부를 지자체에서 지원(이차보전)</li>
                                <li>• <b>지원율:</b> 통상 은행 대출 금리에서 1.0% ~ 3.0%를 도/시에서 대신 납부</li>
                            </ul>
                            <ul class="text-xs text-emerald-700 space-y-1 break-keep flex-1">
                                <li>• <b>경기도 자금:</b> 경기도 중소기업 육성자금 (시설/운전 자금 지원)</li>
                                <li>• <b>시 자금:</b> 시흥시 등 관내 중소기업 육성자금 (지자체 예산 소진 전 조기 신청 필수)</li>
                            </ul>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <!-- [가변] TAB 4: 마스터 스케쥴 -->
        <div id="tab_schedule" class="tab-content print-break-inside-avoid">
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
                <h2 class="text-2xl font-bold text-slate-800 mb-6 pb-4 border-b border-slate-100">📅 단기 집중 스케쥴 (기준: {m1:02d}월 시작)</h2>
                
                <div class="relative border-l-2 border-slate-200 ml-3 space-y-8 py-2">
                    <!-- Phase 1 -->
                    <div class="relative pl-8">
                        <div class="absolute left-[-9px] top-1 w-4 h-4 rounded-full bg-slate-400 ring-4 ring-white"></div>
                        <span class="inline-block px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm font-bold mb-2">{m1:02d}월 ~ {m2:02d}월</span>
                        <h3 class="text-lg font-bold text-slate-800">인사/노무 기반 정비</h3>
                        <p class="text-slate-600 text-sm mt-1">근로계약서 및 필수합의서 작성, 법정의무교육, 취업규칙(10인 이상) 신고, 4대보험 절세 세팅</p>
                    </div>
                    <!-- Phase 2 -->
                    <div class="relative pl-8">
                        <div class="absolute left-[-9px] top-1 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-white"></div>
                        <span class="inline-block px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-sm font-bold mb-2">{m2:02d}월 ~ {m3:02d}월</span>
                        <h3 class="text-lg font-bold text-slate-800">인증 획득 프로세스 가동</h3>
                        <p class="text-slate-600 text-sm mt-1">연구전담부서 설립 신청, 뿌리기업/소부장 사전 점검 및 신청, 여성/벤처기업 신청 및 현장 준비</p>
                    </div>
                    <!-- Phase 3 -->
                    <div class="relative pl-8">
                        <div class="absolute left-[-9px] top-1 w-4 h-4 rounded-full bg-emerald-500 ring-4 ring-white"></div>
                        <span class="inline-block px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-sm font-bold mb-2">{m3:02d}월 ~ {m4:02d}월</span>
                        <h3 class="text-lg font-bold text-slate-800">재무/세무 결산 및 법무 정비</h3>
                        <p class="text-slate-600 text-sm mt-1">가결산 정리, 임원 보수 적정성 판단, 상법 개정에 맞춘 정관 검토, 세액감면 적용 시뮬레이션</p>
                    </div>
                    <!-- Phase 4 -->
                    <div class="relative pl-8">
                        <div class="absolute left-[-9px] top-1 w-4 h-4 rounded-full bg-purple-500 ring-4 ring-white"></div>
                        <span class="inline-block px-3 py-1 bg-purple-50 text-purple-600 rounded-full text-sm font-bold mb-2">{m4:02d}월 이후 지속</span>
                        <h3 class="text-lg font-bold text-slate-800">자금 매칭 및 사후 관리</h3>
                        <p class="text-slate-600 text-sm mt-1">완성된 인증 및 재무제표를 바탕으로 중진공 및 은행 자금 검토, 고용지원금 지속 관리 및 직접생산/공장등록 사후점검</p>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <script>
        // 1. 날짜 자동 출력 스크립트 (엑셀 TODAY 함수 기능)
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        document.getElementById('auto_date').innerText = year + '년 ' + month + '월 ' + day + '일';

        // 2. 탭 전환 스크립트
        function switchTab(tabId, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('text-blue-600', 'border-blue-600', 'font-bold');
                btn.classList.add('text-slate-500', 'border-transparent', 'font-medium');
            }});
            element.classList.remove('text-slate-500', 'border-transparent', 'font-medium');
            element.classList.add('text-blue-600', 'border-blue-600', 'font-bold');

            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.getElementById(tabId).classList.add('active');
        }}

        // 3. 강제 인쇄 실행 스크립트 (모든 탭을 강제로 열고 인쇄)
        function executePrint() {{
            // body에 강제 인쇄용 클래스 추가
            document.body.classList.add('force-print-mode');
            
            // 약간의 딜레이를 주어 화면 렌더링 후 인쇄 다이얼로그 호출
            setTimeout(() => {{
                window.print();
                
                // 인쇄 다이얼로그가 닫히면 강제 인쇄용 클래스 제거
                setTimeout(() => {{
                    document.body.classList.remove('force-print-mode');
                }}, 500);
            }}, 200);
        }}
    </script>
</body>
</html>
"""

with col2:
    st.subheader(f"💻 {client_name} 제안서 미리보기")
    
    # 생성된 HTML을 브라우저에 렌더링 (스크롤 적용)
    components.html(html_content, height=800, scrolling=True)

    # 완성된 HTML 파일 다운로드 버튼 생성
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    download_link = f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 15px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px; font-size: 16px;">📥 [ {client_name} ] 맞춤 제안서 파일로 다운로드 (다운로드 후 우측 상단 🖨️ 인쇄 버튼 클릭)</a>'
    
    st.markdown(download_link, unsafe_allow_html=True)
