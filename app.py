import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="제이원 가로형 경영제안서 시스템", layout="wide")

st.title("📊 주식회사 제이원 - A4 가로 출력 최적화 제안서")
st.write("본 시스템은 대표님들의 가독성을 위해 큰 글씨와 A4 가로 인쇄 레이아웃이 적용되었습니다.")

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
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장에 따른 행정/노무 정비 및 지원금 수령")
    proposal_items = "".join([f"<li class='mb-6 flex items-start'><span class='text-blue-600 mr-4 text-3xl'>✔</span><span class='break-keep text-2xl font-bold text-slate-700'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
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

    # 지원금 카드 생성 함수 (가로 출력 시 3열 배치를 고려한 디자인)
    def generate_subsidy_card(title, target, eligible, max_amount_str, scheduled_count, total_amount):
        if eligible:
            return f"""
            <div class="bg-amber-50 p-8 rounded-3xl border-2 border-amber-200 shadow-sm relative overflow-hidden print-break-inside-avoid mb-6 h-full flex flex-col justify-between">
                <div class="absolute right-0 top-0 bg-amber-400 text-amber-900 text-sm font-bold px-5 py-2 rounded-bl-2xl">예정: {scheduled_count}명</div>
                <div>
                    <h3 class="font-bold text-amber-900 text-2xl mb-4">{title}</h3>
                    <p class="font-black text-amber-600 text-4xl mb-4">{total_amount:,}<span class="text-xl font-normal text-amber-700"> 만원</span></p>
                </div>
                <p class="text-base text-amber-700 font-bold border-t border-amber-200 pt-4">※ {max_amount_str}</p>
            </div>
            """
        else:
            return f"""
            <div class="bg-slate-100 p-8 rounded-3xl border-2 border-slate-200 shadow-sm relative overflow-hidden opacity-60 grayscale print-break-inside-avoid mb-6 h-full flex flex-col justify-center">
                <h3 class="font-bold text-slate-500 text-2xl mb-2">{title}</h3>
                <p class="font-bold text-slate-400 text-4xl">0<span class="text-xl font-normal"> 만원</span></p>
                <p class="text-sm text-red-500 mt-4 font-black">※ 요건 미달 신청불가</p>
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
    show_corp_tab = st.toggle("법인 전환 검토 탭 활성화 (개인사업자용)", value=True)
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
    min_wage = st.number_input("최저시급 설정", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# ----------------------------------------------------------------------------------
# HTML/CSS 시작 (가로 인쇄 최적화 및 폰트 대폭 확대)
# ----------------------------------------------------------------------------------
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ 
            font-family: 'Noto Sans KR', sans-serif; 
            background-color: #f1f5f9; 
            color: #0f172a; 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important;
            font-size: 20px; 
        }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        .text-gradient {{ background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(to right, #1d4ed8, #059669); }}
        
        /* 🖨️ 가로(Landscape) 인쇄 전용 레이아웃 */
        @media print {{
            @page {{ size: A4 landscape; margin: 10mm; }}
            body {{ background-color: #ffffff !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            
            .tab-content {{ display: none !important; }}
            .tab-content.print-active {{ 
                display: block !important; 
                opacity: 1 !important; 
                page-break-before: always !important; 
                margin-top: 0 !important;
                padding: 10px !important;
            }}
            #tab_proposal.print-active {{ page-break-before: avoid !important; }}
            
            .print-break-inside-avoid {{ page-break-inside: avoid; break-inside: avoid; }}
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #cbd5e1 !important; }}
            
            h2 {{ font-size: 40px !important; margin-bottom: 40px !important; border-bottom-width: 6px !important; }}
            p, li, td, th {{ font-size: 22px !important; line-height: 1.6 !important; }}
        }}
        
        h2 {{ font-size: 34px; font-weight: 900; }}
        .card-title {{ font-size: 26px; }}
        .info-text {{ font-size: 22px; line-height: 1.8; }}
        table th, table td {{ padding: 20px; font-size: 20px; }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-12 pb-12 px-12 relative">
        <div class="absolute inset-0 opacity-20" style="background: radial-gradient(circle at top right, #3b82f6, transparent);"></div>
        <div class="max-w-7xl mx-auto relative z-10 flex justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-xl mb-2">MASTER CONSULTING PLAN</p>
                <h1 class="text-6xl font-black mb-4 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 text-xl font-bold">업종코드: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right flex flex-col items-end">
                <button id="print_btn" onclick="executePrint()" class="mb-6 bg-blue-600 hover:bg-blue-700 text-white text-xl font-bold py-4 px-8 rounded-2xl shadow-2xl cursor-pointer transition-all">🖨️ 전체 내용 인쇄하기 (가로 출력)</button>
                <p class="text-slate-400 text-base">제안일자: <span id="auto_date"></span></p>
                <p class="text-3xl font-black mt-2">{my_company_name}</p>
            </div>
        </div>
    </header>

    <div class="bg-white border-b sticky top-0 z-20 overflow-x-auto shadow-md">
        <div class="max-w-7xl mx-auto px-10 flex space-x-12">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-6 font-black text-blue-600 border-b-4 border-blue-600 whitespace-nowrap text-xl">1. 핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-6 font-black text-slate-500 whitespace-nowrap text-xl">2. 노무 및 비과세</button>
            {'<button id="btn_corp" onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-6 font-black text-slate-500 whitespace-nowrap text-xl">3. 법인 전환</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-6 font-black text-slate-500 whitespace-nowrap text-xl">4. 인증/지원금</button>
            <button onclick="switchTab('tab_fund', this)" class="tab-btn py-6 font-black text-slate-500 whitespace-nowrap text-xl">5. 기관별 자금</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-6 font-black text-slate-500 whitespace-nowrap text-xl">6. 스케쥴</button>
        </div>
    </div>

    <main class="max-w-7xl mx-auto px-10 py-16">
        <!-- 탭 1: 핵심 제안 -->
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white rounded-[40px] shadow-sm border-2 border-slate-100 p-16">
                <h2 class="text-slate-800 mb-12 pb-6 border-b-8 border-blue-500 inline-block">💡 {client_name} 경영 고도화 핵심 전략</h2>
                <ul class="info-text space-y-8">{proposal_items}</ul>
            </div>
        </div>

        <!-- 탭 2: 노무 상세 -->
        <div id="tab_labor" class="tab-content print-active">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-10 mb-16 print-break-inside-avoid">
                <div class="bg-white rounded-[40px] border-4 border-blue-100 p-10 shadow-sm">
                    <h2 class="text-blue-800 mb-8">⏱️ 2026년 최저임금 및 법적 의무</h2>
                    <div class="flex justify-between mb-6 items-center text-2xl font-bold text-slate-600"><span>2026년 최저 시급</span><p class="text-5xl text-slate-900 font-black">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-8 rounded-3xl flex justify-between items-center font-black text-blue-700">
                        <span class="text-2xl">월 환산액 (209시간 기준)</span>
                        <span class="text-5xl">{monthly_wage:,}원</span>
                    </div>
                    <p class="text-lg text-slate-500 mt-8 leading-relaxed font-bold break-keep">※ 최저임금법 위반 시 시정지시 없이 즉시 처벌됩니다 (3년 이하 징역 또는 2천만원 이하 벌금).</p>
                </div>
                <div class="bg-red-50 rounded-[40px] border-4 border-red-200 p-10 text-red-900 shadow-sm">
                    <h2 class="mb-6 font-black">🚨 근로계약서 미작성 리스크</h2>
                    <p class="text-2xl mb-8 leading-relaxed font-black">근로계약서는 사업주를 지키는 유일한 법적 방어막입니다.</p>
                    <ul class="space-y-6 text-xl font-bold">
                        <li class="flex items-start"><span class="mr-3">🚩</span><span>정규직 미작성: 벌금 최대 500만원 (형사처벌/전과기록)</span></li>
                        <li class="flex items-start"><span class="mr-3">🚩</span><span>단시간/기간제 미작성: 과태료 500만원 즉시 부과</span></li>
                        <li class="flex items-start"><span class="mr-3">🚩</span><span>노동 분쟁 시 계약서가 없으면 사업주는 100% 패소합니다.</span></li>
                    </ul>
                </div>
            </div>

            <div class="bg-white rounded-[40px] border-4 border-slate-200 p-12 mb-16 print-break-inside-avoid">
                <h2 class="text-slate-800 mb-10 pl-6 border-l-[12px] border-slate-800">🏢 상시근로자 5인 미만 vs 5인 이상 노무관리 핵심 차이표</h2>
                <table class="w-full text-left border-collapse rounded-3xl overflow-hidden shadow-xl">
                    <thead class="bg-slate-800 text-white">
                        <tr><th class="p-8 border border-slate-700 text-2xl">구분</th><th class="p-8 border border-slate-700 text-2xl">5인 미만 사업장</th><th class="p-8 border border-slate-700 text-2xl">5인 이상 사업장 (리스크 관리)</th></tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 text-slate-700 font-bold">
                        <tr><td class="p-8 border bg-slate-50 text-2xl">가산수당 (연장/야간/휴일)</td><td class="p-8 border text-2xl">의무 없음 (1배 지급)</td><td class="p-8 border font-black text-red-600 text-3xl">통상임금의 50% 가산 (1.5배)</td></tr>
                        <tr><td class="p-8 border bg-slate-50 text-2xl">연차유급휴가</td><td class="p-8 border text-2xl">부여 의무 없음</td><td class="p-8 border font-black text-red-600 text-3xl">법정 연차 발생 (미사용 시 수당)</td></tr>
                        <tr><td class="p-8 border bg-slate-50 text-2xl">부당해고 구제신청</td><td class="p-8 border text-2xl">적용 제외</td><td class="p-8 border font-black text-red-600 text-3xl">노동위 구제신청 가능 (절차 엄격)</td></tr>
                        <tr><td class="p-8 border bg-slate-50 text-2xl">주 52시간 근무제</td><td class="p-8 border text-2xl">미적용</td><td class="p-8 border font-black text-red-600 text-3xl">준수 의무 적용 (위반 시 구속 가능)</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="bg-emerald-50 rounded-[40px] border-4 border-emerald-200 p-12 print-break-inside-avoid">
                <h2 class="text-emerald-800 mb-10 border-b-4 border-emerald-200 pb-6 text-4xl font-black">💎 합법적 4대보험 비과세 항목 (매월 고정비 즉각 절감 설계)</h2>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div class="bg-white p-10 rounded-[30px] shadow-sm text-center border-2 border-emerald-100">
                        <p class="font-black text-slate-600 text-2xl mb-4">🍚 식대 (중식대)</p>
                        <p class="text-4xl text-emerald-600 font-black font-black">월 20만원</p>
                    </div>
                    <div class="bg-white p-10 rounded-[30px] shadow-sm text-center border-2 border-emerald-100">
                        <p class="font-black text-slate-600 text-2xl mb-4">🚗 자가운전보조</p>
                        <p class="text-4xl text-emerald-600 font-black">월 20만원</p>
                    </div>
                    <div class="bg-white p-10 rounded-[30px] shadow-sm text-center border-2 border-emerald-100">
                        <p class="font-black text-slate-600 text-2xl mb-4">👶 출산보육수당</p>
                        <p class="text-4xl text-emerald-600 font-black">월 20만원</p>
                    </div>
                    <div class="bg-white p-10 rounded-[30px] shadow-sm text-center border-2 border-emerald-100">
                        <p class="font-black text-slate-600 text-2xl mb-4">🔬 연구보조비</p>
                        <p class="text-4xl text-emerald-600 font-black">월 20만원</p>
                    </div>
                </div>
                <p class="text-2xl text-emerald-700 mt-12 text-center font-black">※ 위 항목 활용 시 사업주 4대보험료 약 10% 추가 절감 및 근로자 실수령액 증가 효과가 즉시 발생합니다.</p>
            </div>
        </div>

        <!-- 탭 3: 법인 전환 (On/Off 완전 연동) -->
        <div id="tab_corp" class="tab-content {'print-active' if show_corp_tab else ''}">
            <div class="bg-white rounded-[40px] border-4 border-slate-200 p-16">
                <h2 class="text-slate-800 mb-12 pb-6 border-b-8 border-indigo-500 inline-block font-black">⚖️ 개인사업자 vs 법인사업자 통합 세무 비용 비교</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 mb-16 items-center">
                    <div class="space-y-10">
                        <div class="bg-red-50 p-10 rounded-[40px] border-4 border-red-100">
                            <p class="text-2xl font-black text-red-800 mb-4">개인사업 유지 시 (종소세 + 지역건보료)</p>
                            <p class="text-7xl font-black text-red-600">{personal_total_cost:,.0f}<span class="text-3xl font-bold"> 만원</span></p>
                        </div>
                        <div class="bg-blue-50 p-10 rounded-[40px] border-4 border-blue-100">
                            <p class="text-2xl font-black text-blue-800 mb-4">법인 전환 시 (법인세 + 급여세 + 직장보험)</p>
                            <p class="text-7xl font-black text-blue-600">{corp_total_cost:,.0f}<span class="text-3xl font-bold"> 만원</span></p>
                        </div>
                        <div class="bg-emerald-100 p-10 rounded-[40px] text-center shadow-xl border-4 border-emerald-200">
                            <p class="text-4xl font-black text-emerald-900">💡 연간 약 <span class="text-7xl text-emerald-600">{max(0, tax_diff):,.0f}만 원</span> 절세 기대</p>
                        </div>
                    </div>
                    <div class="h-[500px] flex justify-center bg-slate-50 rounded-[40px] p-10 border-4 border-slate-100"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <!-- 탭 4: 인증 및 지원금 -->
        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="font-black mb-12 border-l-[14px] border-amber-400 pl-8 text-5xl">💰 고용지원금 수령 시뮬레이션</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
                {card_youth}{card_senior}{card_women}{card_continuous}{card_disabled}{card_parental}
            </div>
            
            <h2 class="font-black mb-12 border-l-[14px] border-blue-500 pl-8 text-5xl">🏆 기업 핵심 인증 상세 혜택 (클릭 강조)</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-10 rounded-[40px] border-4 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-[25px] hidden">✔️ 대상</div>
                    <h3 class="font-black text-3xl mb-6 text-slate-800">여성기업인증</h3>
                    <ul class="text-xl text-slate-600 space-y-3 font-bold">
                        <li>• 수의계약 5,000만원 한도 상향</li>
                        <li>• 공공기관 의무구매 대상 포함</li>
                        <li>• 정책자금 신청 시 우선 순위 부여</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-10 rounded-[40px] border-4 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-[25px] hidden">✔️ 대상</div>
                    <h3 class="font-black text-3xl mb-6 text-slate-800">직접생산 / 공장등록</h3>
                    <ul class="text-xl text-slate-600 space-y-3 font-bold">
                        <li>• 나라장터 조달 입찰 참여 필수 요건</li>
                        <li>• 제조업 전용 세제 감면 및 전기료 할인</li>
                        <li>• 공공시장 진입을 위한 기본 베이스</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-10 rounded-[40px] border-4 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-[25px] hidden">✔️ 대상</div>
                    <h3 class="font-black text-3xl mb-6 text-slate-800">메인비즈 / 이노비즈</h3>
                    <ul class="text-xl text-slate-600 space-y-3 font-bold">
                        <li>• 기술/경영 혁신형 중소기업 국가 공인</li>
                        <li>• 정책자금 금리 인하 및 한도 대폭 우대</li>
                        <li>• 정기 세무조사 3년 유예 혜택</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-10 rounded-[40px] border-4 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-[25px] hidden">✔️ 대상</div>
                    <h3 class="font-black text-3xl mb-6 text-slate-800">ISO 9001 / 45001</h3>
                    <ul class="text-xl text-slate-600 space-y-3 font-bold">
                        <li>• 글로벌 품질 및 안전보건 경영 표준</li>
                        <li>• 중대재해처벌법 대응 핵심 근거자료</li>
                        <li>• 대기업 및 해외 수출 필수 인증</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-10 rounded-[40px] border-4 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-[25px] hidden">✔️ 대상</div>
                    <h3 class="font-black text-3xl mb-6 text-slate-800">특허 확보 (원천기술)</h3>
                    <ul class="text-xl text-slate-600 space-y-3 font-bold">
                        <li>• 독점적 기술 권리 보호 (비용 400~1000만)</li>
                        <li>• 기업 가치 및 기술 등급 상향 필수 요소</li>
                        <li>• 무상 자금 유치를 위한 핵심 가점</li>
                    </ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-10 rounded-[40px] border-4 border-slate-100 shadow-sm hover:bg-blue-50 relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-lg font-bold px-6 py-2 rounded-bl-[25px] hidden">✔️ 대상</div>
                    <h3 class="font-black text-3xl mb-6 text-slate-800">기업부설연구소</h3>
                    <ul class="text-xl text-slate-600 space-y-3 font-bold">
                        <li>• 연구전담인력 인건비 25% 법인세 공제</li>
                        <li>• 연구원 인당 월 20만원 비과세 혜택</li>
                        <li>• 기업 R&D 역량 증명을 통한 자금 확대</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 탭 5: 기관별 자금 (상세 100% 복구) -->
        <div id="tab_fund" class="tab-content print-active">
            <h2 class="font-black mb-12 border-l-[14px] border-emerald-500 pl-8 text-5xl text-emerald-800">🏦 기관별 정책자금 및 지원사업 가이드</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div class="bg-emerald-50 p-12 rounded-[40px] border-4 border-emerald-200 print-break-inside-avoid">
                    <h3 class="font-black text-emerald-800 text-3xl mb-8 border-b-4 border-emerald-200 pb-6 text-center">🟢 1. 중소벤처기업진흥공단 및 바우처</h3>
                    <ul class="text-2xl space-y-6 text-emerald-800 font-bold leading-relaxed">
                        <li><b>[직접융자]</b> 고정금리 연 2.5~3.5% 수준<br><span class="text-lg text-emerald-600">운전자금 최대 5억 / 시설자금 최대 60억 한도</span></li>
                        <li><b>[혁신바우처]</b> 최대 5,000만원 무상 지원<br><span class="text-lg text-emerald-600">시제품 제작, 마케팅, 컨설팅 패키지 지원</span></li>
                        <li><b>[수출바우처]</b> 해외 진출 비용 최대 1억원 지원<br><span class="text-lg text-emerald-600">수출 활동 전반에 대한 90% 국고 보조</span></li>
                    </ul>
                </div>
                <div class="bg-blue-50 p-12 rounded-[40px] border-4 border-blue-200 print-break-inside-avoid">
                    <h3 class="font-black text-blue-800 text-3xl mb-8 border-b-4 border-blue-200 pb-6 text-center">🔵 2. 보증기관 (신보/기보) 및 금융권</h3>
                    <ul class="text-2xl space-y-6 text-blue-800 font-bold leading-relaxed">
                        <li><b>[보증서 대출]</b> 담보 없이 기술력으로 보증<br><span class="text-lg text-blue-600">금리 연 4.0~5.5% / 보증료율 감면 우대 혜택</span></li>
                        <li><b>[시중은행 연계]</b> 정책 연계 이자 감면<br><span class="text-lg text-blue-600">재무제표 기반 한도 최적화 및 이자 차액 지원</span></li>
                    </ul>
                </div>
                <div class="bg-red-50 p-12 rounded-[40px] border-4 border-red-200 print-break-inside-avoid">
                    <h3 class="font-black text-red-800 text-3xl mb-8 border-b-4 border-red-200 pb-6 text-center">🔴 3. 안전보건공단 지원 (보조금/융자)</h3>
                    <ul class="text-2xl space-y-6 text-red-800 font-bold leading-relaxed">
                        <li><b>[안전동행지원]</b> 고위험 설비 교체 무상지원<br><span class="text-lg text-red-600">최대 1억 지원 (국비 50% 매칭 보조금 방식)</span></li>
                        <li><b>[산재예방융자]</b> 안전 설비 도입 초저리 지원<br><span class="text-lg text-red-600"><b>연 1.5% 고정금리</b> (최대 10억원 한도 지원)</span></li>
                    </ul>
                </div>
                <div class="bg-purple-50 p-12 rounded-[40px] border-4 border-purple-200 print-break-inside-avoid">
                    <h3 class="font-black text-purple-800 text-3xl mb-8 border-b-4 border-purple-200 pb-6 text-center">🟣 4. 지자체 정책자금 (도/시 자금)</h3>
                    <ul class="text-2xl space-y-6 text-purple-800 font-bold leading-relaxed">
                        <li><b>[이차보전 지원]</b> 대출 이자 직접 대납<br><span class="text-lg text-purple-600">은행 금리 중 1.0~3.0%를 도/시에서 대신 납부</span></li>
                        <li><b>[관내 전용자금]</b> 시흥시 등 지자체 저리 융자<br><span class="text-lg text-purple-600">지자체 예산 조기 소진 전 적기 신청 및 관리 필수</span></li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 탭 6: 스케쥴 -->
        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-white rounded-[40px] border-4 border-slate-200 p-16 print-break-inside-avoid shadow-sm">
                <h2 class="font-black text-slate-800 mb-12 pb-6 border-b-8 border-slate-800 inline-block">📅 컨설팅 마스터 로드맵</h2>
                <div class="space-y-16">
                    <div class="flex gap-12 items-start">
                        <div class="bg-slate-800 text-white px-8 py-3 rounded-3xl font-black text-3xl">{m1:02d}월</div>
                        <div><p class="text-3xl font-black mb-3">인사/노무 기반 정비 및 비과세 최적화</p><p class="text-2xl text-slate-500 font-bold">근로계약서 전면 개편, 취업규칙 정비 및 4대보험 고정비 즉시 절감 설계</p></div>
                    </div>
                    <div class="flex gap-12 items-start">
                        <div class="bg-blue-600 text-white px-8 py-3 rounded-3xl font-black text-3xl">{m1:02d}월~{m2:02d}월</div>
                        <div><p class="text-3xl font-black mb-3">핵심 기업인증 프로세스 집중 가동</p><p class="text-2xl text-slate-500 font-bold">메인/이노비즈, ISO 통합인증, 특허 출원 등 정책 가점 확보 프로세스 완료</p></div>
                    </div>
                    <div class="flex gap-12 items-start">
                        <div class="bg-emerald-600 text-white px-8 py-3 rounded-3xl font-black text-3xl">{m3:02d}월~{m4:02d}월</div>
                        <div><p class="text-3xl font-black mb-3">법인 전환 및 재무 건전성 최적화</p><p class="text-2xl text-slate-500 font-bold">절세 시뮬레이션 기반 법인전환 및 자금 유치를 위한 재무제표 가결산 조정</p></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const now = new Date();
        document.getElementById('auto_date').innerText = now.getFullYear() + '년 ' + (now.getMonth()+1) + '월 ' + now.getDate() + '일';

        function switchTab(tabId, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('text-blue-600', 'border-blue-600', 'font-black'));
            element.classList.add('text-blue-600', 'border-blue-600', 'font-black');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        }}

        function toggleCert(el) {{
            el.classList.toggle('border-blue-500'); el.classList.toggle('ring-8'); el.classList.toggle('ring-blue-100');
            el.classList.toggle('bg-blue-50');
            const badge = el.querySelector('.cert-badge'); if (badge) badge.classList.toggle('hidden');
        }}

        function executePrint() {{
            // 현재 활성화된 탭들만 인쇄 리스트에 포함
            document.body.classList.add('force-print-mode');
            setTimeout(() => {{ 
                window.print(); 
                setTimeout(() => document.body.classList.remove('force-print-mode'), 500); 
            }}, 200);
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
                    borderRadius: 15
                }}]
            }},
            options: {{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ ticks: {{ font: {{ size: 16, weight: 'bold' }} }} }}, x: {{ ticks: {{ font: {{ size: 20, weight: 'bold' }} }} }} }}
            }}
        }});
        ''' if show_corp_tab else ""}
    </script>
</body>
</html>
"""

with col2:
    st.subheader(f"💻 {client_name} 제안서 미리보기 (가로형)")
    components.html(html_content, height=1000, scrolling=True)
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 25px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 15px; font-weight: bold; margin-top: 10px; font-size: 20px;">📥 [가로 출력 최적화] 제안서 파일 저장하기</a>', unsafe_allow_html=True)
