import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="제이원 통합 경영제안서 시스템", layout="wide")

st.title("📊 주식회사 제이원 - 시니어 가독성 특화 경영제안서")
st.write("대표님들을 위한 큰 글씨와 깔끔한 인쇄 레이아웃이 적용된 마스터 버전입니다.")

# 화면 분할 (입력폼 1 : 미리보기 2)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 1. 기본 및 고객사 정보")
    my_company_name = st.text_input("제안사 이름", "주식회사 제이원")
    client_name = st.text_input("고객사 이름", "(주)영광산업기계")
    current_employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3, step=1)
    industry_code = st.text_input("업종 코드 및 상태", "[21812] 뿌리기업 해당")

    st.subheader("📝 2. 컨설팅 제안 및 스케쥴")
    proposal_input = st.text_area("핵심 제안 내용 (요약 절대 금지)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장 진입에 따른 행정/노무 정비 및 지원금 수령")
    proposal_items = "".join([f"<li class='mb-4 flex items-start'><span class='text-blue-500 mr-3 text-2xl'>✔</span><span class='break-keep text-xl font-medium'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    start_month = st.number_input("스케쥴 시작 월", min_value=1, max_value=12, value=4)
    m1 = start_month
    m2 = (start_month % 12) + 1
    m3 = (start_month + 3) % 12 + 1
    m4 = (start_month + 4) % 12 + 1

    st.subheader("📝 3. 고용지원금 인원 설정")
    ca, cb, cc = st.columns(3)
    with ca: 
        youth_count = st.number_input("① 청년도약", min_value=0, value=1)
        continuous_count = st.number_input("④ 계속고용", min_value=0, value=0)
    with cb: 
        senior_count = st.number_input("② 시니어인턴", min_value=0, value=1)
        disabled_count = st.number_input("⑤ 장애인", min_value=0, value=0)
    with cc: 
        women_count = st.number_input("③ 새일여성", min_value=0, value=1)
        parental_count = st.number_input("⑥ 대체인력", min_value=0, value=0)

    # 지원금 카드 생성 로직 (디자인 강화)
    def generate_subsidy_card(title, target, eligible, max_amount_str, scheduled_count, total_amount):
        if eligible:
            return f"""
            <div class="bg-amber-50 p-6 rounded-2xl border-2 border-amber-200 shadow-sm relative overflow-hidden print-break-inside-avoid mb-4">
                <div class="absolute right-0 top-0 bg-amber-400 text-amber-900 text-xs font-bold px-4 py-1 rounded-bl-xl">예정: {scheduled_count}명</div>
                <h3 class="font-bold text-amber-900 text-xl mb-2">{title}</h3>
                <p class="font-bold text-amber-600 text-3xl">{total_amount:,}<span class="text-lg font-normal text-amber-700"> 만원</span></p>
                <p class="text-sm text-amber-700 mt-2 font-medium">※ {max_amount_str}</p>
            </div>
            """
        else:
            return f"""
            <div class="bg-slate-100 p-6 rounded-2xl border-2 border-slate-200 shadow-sm relative overflow-hidden opacity-60 grayscale print-break-inside-avoid mb-4">
                <h3 class="font-bold text-slate-500 text-xl mb-2">{title}</h3>
                <p class="font-bold text-slate-400 text-3xl">0<span class="text-lg font-normal"> 만원</span></p>
                <p class="text-sm text-red-500 mt-2 font-bold">※ 현재 조건 미달로 신청 불가</p>
            </div>
            """

    youth_eligible = current_employees >= 5
    card_youth = generate_subsidy_card("청년일자리도약장려금", "청년", youth_eligible, "1인 1,200만원(2년)", youth_count, youth_count * (1200 if youth_eligible else 0))
    card_senior = generate_subsidy_card("시니어인턴십", "60세↑", True, "1인 약 240만원", senior_count, senior_count * 240)
    card_women = generate_subsidy_card("새일여성인턴", "경단녀", True, "1인 380만원", women_count, women_count * 380)
    card_continuous = generate_subsidy_card("고령자계속고용", "정년연장", True, "1인 720만원(2년)", continuous_count, continuous_count * 720)
    card_disabled = generate_subsidy_card("장애인신규고용", "장애인", True, "1인 약 720만원", disabled_count, disabled_count * 720)
    card_parental = generate_subsidy_card("육아휴직대체인력", "대체인력", True, "1인 960만원(1년)", parental_count, parental_count * 960)
    
    total_subsidy = (youth_count * (1200 if youth_eligible else 0)) + (senior_count * 240) + (women_count * 380) + (continuous_count * 720) + (disabled_count * 720) + (parental_count * 960)

    st.subheader("⚖️ 4. 법인 전환 검토 설정")
    show_corp_tab = st.toggle("법인 전환 검토 탭 활성화 (개인사업자 전용)", value=True)
    if show_corp_tab:
        net_income = st.number_input("당기순이익 (만원)", min_value=0, value=15000, step=1000)
        rep_salary = st.number_input("대표자 월 급여 (만원)", min_value=0, value=500, step=50)
        yearly_salary = rep_salary * 12
        p_tax = (net_income * 0.35) * 1.1 
        p_health = net_income * 0.0709 
        personal_total_cost = p_tax + p_health
        corp_profit = max(0, net_income - yearly_salary)
        c_tax = (corp_profit * 0.09 if corp_profit <= 20000 else 1800 + (corp_profit-20000)*0.19) * 1.1
        s_tax = (yearly_salary * 0.15) * 1.1
        total_insurance = yearly_salary * 0.1869 
        corp_total_cost = c_tax + s_tax + total_insurance
        tax_diff = personal_total_cost - corp_total_cost
    else:
        personal_total_cost, corp_total_cost, tax_diff, rep_salary = 0, 0, 0, 0

    st.subheader("📝 5. 노무/시급 기준")
    min_wage = st.number_input("2026년 최저시급 (원)", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# ----------------------------------------------------------------------------------
# HTML/CSS 시작 (A4 최적화 및 폰트 크기 대폭 상향)
# ----------------------------------------------------------------------------------
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ 
            font-family: 'Noto Sans KR', sans-serif; 
            background-color: #f1f5f9; 
            color: #0f172a; 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important;
            font-size: 18px; /* 기본 폰트 크기 상향 */
        }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        .text-gradient {{ background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(to right, #1d4ed8, #059669); }}
        
        /* 인쇄 전용 레이아웃 */
        @media print {{
            @page {{ size: A4; margin: 15mm; }}
            body {{ background-color: #ffffff !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            
            /* 모든 활성 탭 내용을 강제로 페이지 단위로 펼침 */
            .tab-content {{ display: none !important; }}
            .tab-content.print-active {{ 
                display: block !important; 
                opacity: 1 !important; 
                page-break-before: always !important; 
                margin-top: 0 !important;
                padding-top: 20px !important;
            }}
            /* 첫 페이지 중복 넘김 방지 */
            #tab_proposal.print-active {{ page-break-before: avoid !important; }}
            
            .print-break-inside-avoid {{ page-break-inside: avoid; break-inside: avoid; }}
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #cbd5e1 !important; }}
            
            h2 {{ font-size: 32px !important; margin-bottom: 30px !important; }}
            p, li, td, th {{ font-size: 20px !important; line-height: 1.6 !important; }}
        }}
        
        /* 화면상 시니어 가독성용 스타일 */
        h2 {{ font-size: 28px; }}
        .card-title {{ font-size: 22px; }}
        .info-text {{ font-size: 19px; line-height: 1.8; }}
        table th, table td {{ padding: 16px; font-size: 18px; }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-16 pb-16 px-10 relative">
        <div class="absolute inset-0 opacity-20" style="background: radial-gradient(circle at top right, #3b82f6, transparent);"></div>
        <div class="max-w-5xl mx-auto relative z-10 flex justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-lg mb-2">MASTER CONSULTING PLAN</p>
                <h1 class="text-5xl font-bold mb-4 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 text-lg font-medium">업종코드: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right flex flex-col items-end">
                <button id="print_btn" onclick="executePrint()" class="mb-6 bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold py-3 px-6 rounded-xl shadow-lg cursor-pointer transition-all">🖨️ 전체 내용 인쇄하기</button>
                <p class="text-slate-400 text-sm">제안일자: <span id="auto_date"></span></p>
                <p class="text-2xl font-bold mt-2">{my_company_name}</p>
            </div>
        </div>
    </header>

    <div class="bg-white border-b sticky top-0 z-20 overflow-x-auto shadow-md">
        <div class="max-w-5xl mx-auto px-6 flex space-x-10">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-5 font-bold text-blue-600 border-b-4 border-blue-600 whitespace-nowrap text-lg">1. 핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap text-lg">2. 노무 및 비과세</button>
            {'<button id="btn_corp" onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap text-lg">3. 법인 전환</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap text-lg">4. 인증/지원금</button>
            <button onclick="switchTab('tab_fund', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap text-lg">5. 기관별 자금</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-bold text-slate-500 whitespace-nowrap text-lg">6. 스케쥴</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-6 py-12">
        <!-- 탭 1: 핵심 제안 -->
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white rounded-3xl shadow-sm border-2 border-slate-100 p-12">
                <h2 class="font-bold text-slate-800 mb-10 pb-6 border-b-4 border-blue-500 inline-block">💡 {client_name} 경영 고도화 솔루션</h2>
                <ul class="info-text space-y-4">{proposal_items}</ul>
            </div>
        </div>

        <!-- 탭 2: 노무 상세 (내용 요약 절대 금지 반영) -->
        <div id="tab_labor" class="tab-content print-active">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 print-break-inside-avoid">
                <div class="bg-white rounded-3xl border-2 border-blue-100 p-8 shadow-sm">
                    <h2 class="text-blue-800 mb-6 font-bold">⏱️ 2026년 최저임금 및 법적 의무</h2>
                    <div class="flex justify-between mb-4 items-center"><span>2026년 최저 시급</span><p class="text-3xl font-bold text-slate-900">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-6 rounded-2xl flex justify-between items-center font-bold text-blue-700">
                        <span class="text-xl">월 환산액 (209시간)</span>
                        <span class="text-3xl">{monthly_wage:,}원</span>
                    </div>
                    <p class="text-base text-slate-500 mt-6 leading-relaxed break-keep">※ 최저임금법 위반 시 시정지시 없이 즉시 <b>3년 이하 징역 또는 2천만원 이하 벌금</b>이 부과될 수 있습니다.</p>
                </div>
                <div class="bg-red-50 rounded-3xl border-2 border-red-200 p-8 text-red-900 shadow-sm">
                    <h2 class="mb-4 font-bold">🚨 근로계약서 미작성 리스크</h2>
                    <p class="text-lg mb-6 leading-relaxed font-medium">근로계약서는 사업주를 보호하는 유일한 방어막이자 입증 서류입니다.</p>
                    <ul class="space-y-4 danger-list text-lg">
                        <li>정규직 미작성: <b>벌금 최대 500만원 (형사처벌/전과기록)</b></li>
                        <li>단시간/기간제 미작성: <b>과태료 500만원 즉시 부과</b></li>
                        <li>노동 분쟁 발생 시 계약서 부재는 사업주에게 절대적으로 불리하게 작용</li>
                    </ul>
                </div>
            </div>

            <div class="bg-white rounded-3xl border-2 border-slate-200 p-10 mb-12 print-break-inside-avoid">
                <h2 class="text-slate-800 mb-8 font-bold pl-4 border-l-8 border-slate-800">🏢 5인 미만 vs 5인 이상 노무관리 핵심 차이표</h2>
                <table class="w-full text-left border-collapse rounded-xl overflow-hidden shadow-sm">
                    <thead class="bg-slate-800 text-white">
                        <tr><th class="p-5 border border-slate-700">구분</th><th class="p-5 border border-slate-700">5인 미만 사업장</th><th class="p-5 border border-slate-700">5인 이상 사업장</th></tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 text-slate-700 font-medium">
                        <tr><td class="p-5 border bg-slate-50 font-bold">가산수당 (연장/야간/휴일)</td><td class="p-5 border">의무 없음 (1배 지급)</td><td class="p-5 border font-bold text-red-600">통상임금의 50% 가산 (1.5배)</td></tr>
                        <tr><td class="p-5 border bg-slate-50 font-bold">연차유급휴가</td><td class="p-5 border">의무 없음</td><td class="p-5 border font-bold text-red-600">법정 연차 발생 (미사용 시 수당 정산)</td></tr>
                        <tr><td class="p-5 border bg-slate-50 font-bold">부당해고 구제신청</td><td class="p-5 border">적용 제외 (비교적 자유)</td><td class="p-5 border font-bold text-red-600">노동위 구제신청 가능 (해고 절차 엄격)</td></tr>
                        <tr><td class="p-5 border bg-slate-50 font-bold">주 52시간 근무제</td><td class="p-5 border">미적용</td><td class="p-5 border font-bold text-red-600">준수 의무 적용 (위반 시 형사처벌)</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="bg-emerald-50 rounded-3xl border-2 border-emerald-200 p-10 print-break-inside-avoid">
                <h2 class="text-emerald-800 mb-8 font-bold border-b-2 border-emerald-200 pb-4 text-3xl">💎 합법적 4대보험 비과세 항목 (매월 고정비 즉각 절감)</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div class="bg-white p-8 rounded-2xl shadow-sm text-center border border-emerald-100">
                        <p class="font-bold text-slate-600 text-xl mb-2">🍚 식대 (중식대)</p>
                        <p class="text-3xl text-emerald-600 font-bold">월 20만원</p>
                    </div>
                    <div class="bg-white p-8 rounded-2xl shadow-sm text-center border border-emerald-100">
                        <p class="font-bold text-slate-600 text-xl mb-2">🚗 자가운전보조</p>
                        <p class="text-3xl text-emerald-600 font-bold">월 20만원</p>
                    </div>
                    <div class="bg-white p-8 rounded-2xl shadow-sm text-center border border-emerald-100">
                        <p class="font-bold text-slate-600 text-xl mb-2">👶 출산보육수당</p>
                        <p class="text-3xl text-emerald-600 font-bold">월 20만원</p>
                    </div>
                    <div class="bg-white p-8 rounded-2xl shadow-sm text-center border border-emerald-100">
                        <p class="font-bold text-slate-600 text-xl mb-2">🔬 연구보조비</p>
                        <p class="text-3xl text-emerald-600 font-bold">월 20만원</p>
                    </div>
                </div>
                <p class="text-lg text-emerald-700 mt-8 text-center font-bold">※ 비과세 세팅 시, 근로자 세후 소득 증가 및 사업주 4대보험료(약 10%) 추가 절감 효과!</p>
            </div>
        </div>

        <!-- 탭 3: 법인 전환 (show_corp_tab 조건 반영) -->
        <div id="tab_corp" class="tab-content {'print-active' if show_corp_tab else ''}">
            <div class="bg-white rounded-3xl border-2 border-slate-200 p-12">
                <h2 class="font-bold text-slate-800 mb-10 pb-6 border-b-4 border-indigo-500 inline-block">⚖️ 개인 vs 법인 통합 세무 비용 비교 분석</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12 items-center">
                    <div class="space-y-6">
                        <div class="bg-red-50 p-8 rounded-3xl border-2 border-red-100">
                            <p class="text-xl font-bold text-red-800 mb-2">개인사업 유지 시 (소득세 + 지역건보료)</p>
                            <p class="text-5xl font-bold text-red-600">{personal_total_cost:,.0f}<span class="text-2xl font-normal"> 만원</span></p>
                        </div>
                        <div class="bg-blue-50 p-8 rounded-3xl border-2 border-blue-100">
                            <p class="text-xl font-bold text-blue-800 mb-2">법인 전환 시 (법인세 + 근로세 + 직장보험)</p>
                            <p class="text-5xl font-bold text-blue-600">{corp_total_cost:,.0f}<span class="text-2xl font-normal"> 만원</span></p>
                        </div>
                        <div class="bg-emerald-100 p-8 rounded-3xl text-center shadow-md">
                            <p class="text-3xl font-bold text-emerald-900">💡 예상 절세 기대액: <span class="text-5xl text-emerald-600">{max(0, tax_diff):,.0f}만 원</span></p>
                            <p class="text-lg text-slate-500 mt-4">※ 월 급여 {rep_salary:,}만원 대표 근로자 전환 시뮬레이션 결과</p>
                        </div>
                    </div>
                    <div class="h-96 flex justify-center bg-slate-50 rounded-3xl p-6 border border-slate-100 shadow-inner"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <!-- 탭 4: 인증 및 지원금 (전체 상세) -->
        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="font-bold mb-8 border-l-8 border-amber-400 pl-6 text-4xl">💰 고용지원금 수령 시뮬레이션</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
                {card_youth}{card_senior}{card_women}{card_continuous}{card_disabled}{card_parental}
            </div>
            
            <h2 class="font-bold mb-8 border-l-8 border-blue-500 pl-6 text-4xl">🏆 기업 핵심 인증 상세 혜택</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-bl-2xl hidden">✔️ 대상</div>
                    <h3 class="font-bold text-2xl mb-4 text-slate-800">여성기업인증</h3>
                    <ul class="text-lg text-slate-600 space-y-2">
                        <li>• 공공기관 수의계약 5,000만원 한도 확대</li>
                        <li>• 공공입찰 가점 및 자금 신청 시 우선권</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-bl-2xl hidden">✔️ 대상</div>
                    <h3 class="font-bold text-2xl mb-4 text-slate-800">직접생산 / 공장등록</h3>
                    <ul class="text-lg text-slate-600 space-y-2">
                        <li>• 나라장터 경쟁입찰 참여 필수 요건</li>
                        <li>• 제조업 전용 세제 혜택 및 전기료 감면 적용</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-bl-2xl hidden">✔️ 대상</div>
                    <h3 class="font-bold text-2xl mb-4 text-slate-800">메인비즈 / 이노비즈</h3>
                    <ul class="text-lg text-slate-600 space-y-2">
                        <li>• 경영 및 기술 혁신형 중소기업 국가 공인</li>
                        <li>• 정기 세무조사 유예 및 정책자금 금리 인하</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-bl-2xl hidden">✔️ 대상</div>
                    <h3 class="font-bold text-2xl mb-4 text-slate-800">ISO 9001 / 45001</h3>
                    <ul class="text-lg text-slate-600 space-y-2">
                        <li>• 품질경영 및 안전보건 통합 국제 표준</li>
                        <li>• 중대재해처벌법 대응 및 대기업 협력 필수</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-bl-2xl hidden">✔️ 대상</div>
                    <h3 class="font-bold text-2xl mb-4 text-slate-800">특허 (비용 400~1000만)</h3>
                    <ul class="text-lg text-slate-600 space-y-2">
                        <li>• 핵심 기술 독점적 권리 확보 및 기술가치 상승</li>
                        <li>• 정책자금 한도 증액을 위한 기술 등급 상향</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-bl-2xl hidden">✔️ 대상</div>
                    <h3 class="font-bold text-2xl mb-4 text-slate-800">기업부설연구소</h3>
                    <ul class="text-lg text-slate-600 space-y-2">
                        <li>• 연구전담인력 인건비의 25% 법인세 공제</li>
                        <li>• 연구원 인당 월 20만원 비과세 절세 효과</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 탭 5: 기관별 자금 (상세 복구) -->
        <div id="tab_fund" class="tab-content print-active">
            <h2 class="font-bold mb-10 border-l-8 border-emerald-500 pl-6 text-4xl">🏦 기관별 정책자금 및 지원사업 상세 현황</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-emerald-50 p-10 rounded-3xl border-2 border-emerald-200 print-break-inside-avoid">
                    <h3 class="font-bold text-emerald-800 text-2xl mb-6 border-b-2 border-emerald-200 pb-4">🟢 1. 중소벤처기업진흥공단 및 바우처</h3>
                    <ul class="text-xl space-y-4 text-emerald-700 font-medium">
                        <li><b>[직접융자]</b> 고정금리 연 2.5~3.5% 수준, 운전 5억/시설 60억 한도</li>
                        <li><b>[혁신바우처]</b> 최대 5,000만원 무상 지원 (컨설팅, 시제품 제작, 마케팅)</li>
                        <li><b>[수출바우처]</b> 해외 진출 비용 최대 3,000만원 ~ 1억원 (90% 국고지원)</li>
                    </ul>
                </div>
                <div class="bg-blue-50 p-10 rounded-3xl border-2 border-blue-200 print-break-inside-avoid">
                    <h3 class="font-bold text-blue-800 text-2xl mb-6 border-b-2 border-blue-200 pb-4">🔵 2. 보증기관 (신보/기보) 및 금융권</h3>
                    <ul class="text-xl space-y-4 text-blue-700 font-medium">
                        <li><b>[보증서 대출]</b> 담보 없이 기술력으로 보증서 발급 (금리 4.0~5.5%)</li>
                        <li><b>[시중은행 연계]</b> 정책자금 기반 이자 감면 및 한도 최적화 매칭</li>
                    </ul>
                </div>
                <div class="bg-red-50 p-10 rounded-3xl border-2 border-red-200 print-break-inside-avoid">
                    <h3 class="font-bold text-red-800 text-2xl mb-6 border-b-2 border-red-200 pb-4">🔴 3. 안전보건공단 지원 (보조금/융자)</h3>
                    <ul class="text-xl space-y-4 text-red-700 font-medium">
                        <li><b>[안전동행지원]</b> 고위험 설비 교체 시 <b>최대 1억 무상지원</b> (50% 자부담)</li>
                        <li><b>[산재예방융자]</b> 안전 설비 도입 시 <b>연 1.5% 고정금리</b> (최대 10억)</li>
                    </ul>
                </div>
                <div class="bg-purple-50 p-10 rounded-3xl border-2 border-purple-200 print-break-inside-avoid">
                    <h3 class="font-bold text-purple-800 text-2xl mb-6 border-b-2 border-purple-200 pb-4">🟣 4. 지자체 정책자금 (도/시 자금)</h3>
                    <ul class="text-xl space-y-4 text-purple-700 font-medium">
                        <li><b>[이차보전]</b> 대출 이자 중 1.0~3.0%를 지자체가 직접 대납하여 실이자 절감</li>
                        <li><b>[시흥시 자금]</b> 관내 기업 전용 예산으로 저리 융자 (적기 신청 관리 필수)</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 탭 6: 스케쥴 -->
        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-white rounded-3xl border-2 border-slate-200 p-12 print-break-inside-avoid">
                <h2 class="font-bold text-slate-800 mb-10 pb-6 border-b-4 border-slate-800 inline-block">📅 컨설팅 마스터 로드맵</h2>
                <div class="space-y-12">
                    <div class="flex gap-10 items-start">
                        <div class="bg-slate-800 text-white px-6 py-2 rounded-2xl font-bold text-2xl">{m1:02d}월</div>
                        <div><p class="text-2xl font-bold mb-2">인사/노무 기반 정비 및 비과세 최적화</p><p class="text-xl text-slate-500 font-medium">근로계약서, 취업규칙 정비 및 즉각적인 고정비(4대보험) 절감 설계</p></div>
                    </div>
                    <div class="flex gap-10 items-start">
                        <div class="bg-blue-600 text-white px-6 py-2 rounded-2xl font-bold text-2xl">{m1:02d}월~{m2:02d}월</div>
                        <div><p class="text-2xl font-bold mb-2">핵심 기업인증 획득 (3개월 집중 가동)</p><p class="text-xl text-slate-500 font-medium">메인/이노비즈, ISO, 특허 신청 등 가점 확보를 위한 인증 프로세스 완비</p></div>
                    </div>
                    <div class="flex gap-10 items-start">
                        <div class="bg-emerald-600 text-white px-6 py-2 rounded-2xl font-bold text-2xl">{m3:02d}월~{m4:02d}월</div>
                        <div><p class="text-2xl font-bold mb-2">법인 전환 및 재무 건전성 관리</p><p class="text-xl text-slate-500 font-medium">절세 시뮬레이션에 따른 전환 여부 확정 및 정책 자금 매칭을 위한 가결산 조정</p></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const now = new Date();
        document.getElementById('auto_date').innerText = now.getFullYear() + '년 ' + (now.getMonth()+1) + '월 ' + now.getDate() + '일';

        function switchTab(tabId, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('text-blue-600', 'border-blue-600', 'font-bold'));
            element.classList.add('text-blue-600', 'border-blue-600', 'font-bold');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        }}

        function toggleCert(el) {{
            el.classList.toggle('border-blue-500'); el.classList.toggle('ring-4'); el.classList.toggle('ring-blue-200');
            el.classList.toggle('bg-blue-50');
            const badge = el.querySelector('.cert-badge'); if (badge) badge.classList.toggle('hidden');
        }}

        function executePrint() {{
            // 인쇄용 클래스 추가 (모든 활성 탭 펼침)
            document.body.classList.add('force-print-mode');
            setTimeout(() => {{ window.print(); setTimeout(() => document.body.classList.remove('force-print-mode'), 500); }}, 200);
        }}

        {f'''
        const ctx = document.getElementById('taxChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['개인사업 유지', '법인 전환 통합'],
                datasets: [{{
                    data: [{personal_total_cost}, {corp_total_cost}],
                    backgroundColor: ['#ef4444', '#3b82f6'],
                    borderRadius: 12
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});
        ''' if show_corp_tab else ""}
    </script>
</body>
</html>
"""

with col2:
    st.subheader(f"💻 {client_name} 제안서 최종 미리보기")
    components.html(html_content, height=1000, scrolling=True)
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 20px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 12px; font-weight: bold; margin-top: 10px; font-size: 18px;">📥 최종 제안서 파일로 저장하기</a>', unsafe_allow_html=True)
