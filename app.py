import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="제이원 종합 경영제안서 생성기", layout="wide")

st.title("📊 주식회사 제이원 - 통합 경영컨설팅 제안서 시스템")
st.write("좌측에 맞춤 정보를 입력하세요. 모든 상세 내용은 요약 없이 원문 그대로 반영됩니다.")

# 화면 분할 (입력폼 1 : 미리보기 2)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 1. 기본 및 고객사 정보")
    my_company_name = st.text_input("제안사 이름", "주식회사 제이원")
    client_name = st.text_input("고객사 이름", "(주)영광산업기계")
    current_employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3, step=1)
    industry_code = st.text_input("업종 코드 및 상태", "[21812] 뿌리기업 해당")

    st.subheader("📝 2. 컨설팅 제안 및 스케쥴")
    proposal_input = st.text_area("핵심 제안 내용 (줄바꿈 구분)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장 진입에 따른 행정/노무 정비 및 지원금 수령")
    proposal_items = "".join([f"<li class='mb-2 flex items-start'><span class='text-blue-500 mr-2'>✔</span><span class='break-keep'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    start_month = st.number_input("스케쥴 시작 월", min_value=1, max_value=12, value=4)
    m1, m2, m3, m4 = start_month, (start_month % 12)+1, (start_month+2)%12+1, (start_month+3)%12+1

    st.subheader("📝 3. 고용지원금 설정")
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

    # 지원금 계산 로직
    youth_eligible = current_employees >= 5
    youth_total = youth_count * (1200 if youth_eligible else 0)
    senior_total, women_total = senior_count * 240, women_count * 380
    continuous_total, disabled_total, parental_total = continuous_count * 720, disabled_count * 720, parental_count * 960
    total_subsidy = youth_total + senior_total + women_total + continuous_total + disabled_total + parental_total

    st.subheader("⚖️ 4. 법인 전환 검토 (개인사업자 전용)")
    show_corp_tab = st.toggle("법인 전환 검토 탭 활성화", value=True)
    
    if show_corp_tab:
        net_income = st.number_input("당기순이익 (만원)", min_value=0, value=15000, step=1000)
        rep_salary = st.number_input("대표자 월 급여 (만원)", min_value=0, value=500, step=50)
        yearly_salary = rep_salary * 12
        
        # 세금/건보료 상세 계산
        def calc_personal_tax(income):
            if income <= 1400: return income * 0.06
            elif income <= 5000: return 84 + (income - 1400) * 0.15
            elif income <= 8800: return 624 + (income - 5000) * 0.24
            elif income <= 15000: return 1536 + (income - 8800) * 0.35
            elif income <= 30000: return 3706 + (income - 15000) * 0.38
            elif income <= 50000: return 9406 + (income - 30000) * 0.40
            else: return 17406 + (income - 50000) * 0.42
            
        p_tax = calc_personal_tax(net_income) * 1.1 
        p_health = net_income * 0.0709 # 지역가입자 약 7.09%
        personal_total_cost = p_tax + p_health

        corp_profit = max(0, net_income - yearly_salary)
        c_tax = (corp_profit * 0.09 if corp_profit <= 20000 else 1800 + (corp_profit-20000)*0.19) * 1.1
        s_tax = calc_personal_tax(yearly_salary * 0.85) * 1.1 # 근로소득공제 반영 시뮬레이션
        total_insurance = yearly_salary * 0.1869 # 직장 4대보험 합산 요율
        
        corp_total_cost = c_tax + s_tax + total_insurance
        tax_diff = personal_total_cost - corp_total_cost
    else:
        personal_total_cost, corp_total_cost, tax_diff, rep_salary = 0, 0, 0, 0

    st.subheader("📝 5. 노무/비과세 기준")
    min_wage = st.number_input("2026년 최저시급", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# ----------------------------------------------------------------------------------
# HTML 소스코드 (디테일 복구)
# ----------------------------------------------------------------------------------
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .text-gradient {{ background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(to right, #2563eb, #059669); }}
        .check-list li::before {{ content: '✔'; color: #0ea5e9; margin-right: 8px; font-weight: bold; }}
        .danger-list li::before {{ content: '⚠️'; margin-right: 8px; }}
        
        body.force-print-mode .tab-content {{ display: block !important; opacity: 1 !important; page-break-before: always; }}
        body.force-print-mode #tab_proposal {{ page-break-before: avoid; }}
        body.force-print-mode .tab-btn, body.force-print-mode #print_btn {{ display: none !important; }}
        @media print {{
            body {{ background-color: #ffffff !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            .print-break-inside-avoid {{ page-break-inside: avoid; break-inside: avoid; }}
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #e2e8f0 !important; }}
        }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-12 pb-12 px-8 relative">
        <div class="max-w-5xl mx-auto relative z-10 flex justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-sm mb-2">MASTER CONSULTING PLAN</p>
                <h1 class="text-4xl font-bold mb-3 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 font-light text-sm">업종코드: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right flex flex-col items-end">
                <button id="print_btn" onclick="executePrint()" class="mb-4 bg-blue-600 text-white text-xs font-bold py-2 px-4 rounded shadow">🖨️ 전체 내용 인쇄하기</button>
                <p class="text-slate-400 text-xs">제안일자: <span id="auto_date"></span></p>
                <p class="text-lg font-bold mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <div class="bg-white border-b sticky top-0 z-20 overflow-x-auto shadow-sm">
        <div class="max-w-5xl mx-auto px-6 flex space-x-6 text-sm">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-4 font-bold text-blue-600 border-b-2 border-blue-600 whitespace-nowrap">핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">노무 및 비과세 상세</button>
            {'<button onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">법인 전환 검토</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">인증 및 지원금 상세</button>
            <button onclick="switchTab('tab_fund', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">기관별 자금 상세</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">마스터 스케쥴</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-6 py-8">
        <!-- 탭 1: 핵심 제안 -->
        <div id="tab_proposal" class="tab-content active">
            <div class="bg-white rounded-2xl shadow-sm border p-8">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">💡 {client_name} 전용 솔루션 구조</h2>
                <ul class="text-lg leading-relaxed space-y-2">{proposal_items}</ul>
            </div>
        </div>

        <!-- 탭 2: 노무 및 비과세 (상세 복구) -->
        <div id="tab_labor" class="tab-content">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="bg-white rounded-2xl border p-6 print-break-inside-avoid">
                    <h2 class="text-lg font-bold text-blue-800 mb-4 border-b pb-2">⏱️ 2026년 최저임금 상세</h2>
                    <div class="flex justify-between mb-2"><span>최저 시급</span><p class="font-bold">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-4 rounded-lg flex justify-between font-bold text-blue-700">
                        <span>월 환산액 (주 40시간/월 209시간 기준)</span>
                        <span>{monthly_wage:,}원</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-4 break-keep">※ 주휴수당 포함 금액이며, 위 금액 미달 시 임금체불 및 형사처벌 대상입니다.</p>
                </div>
                <div class="bg-red-50 rounded-2xl border border-red-100 p-6 text-red-800 print-break-inside-avoid">
                    <h2 class="text-lg font-bold mb-2">🚨 근로계약서 미작성 리스크 (사업주 필독)</h2>
                    <p class="text-sm mb-3 font-medium">근로계약서는 사업주를 보호하는 유일한 방어막입니다.</p>
                    <ul class="text-xs space-y-2 danger-list">
                        <li>정규직 미작성: <b>벌금 최대 500만 원 (전과기록 남음)</b></li>
                        <li>단시간/기간제 미작성: <b>즉시 과태료 500만 원 부과</b></li>
                        <li>임금체불 분쟁 시 계약서 부재 시 사업주가 100% 불리한 입증 책임 부담</li>
                    </ul>
                </div>
            </div>

            <div class="bg-white rounded-2xl border p-6 mb-8 print-break-inside-avoid">
                <h2 class="text-lg font-bold text-slate-800 mb-4 pl-2 border-l-4 border-slate-800">🏢 5인 미만 vs 5인 이상 노무관리 핵심 차이</h2>
                <table class="w-full text-xs text-left border-collapse border border-slate-200">
                    <thead class="bg-slate-100">
                        <tr><th class="p-3 border">구분</th><th class="p-3 border text-emerald-700">5인 미만 사업장</th><th class="p-3 border text-red-700">5인 이상 사업장</th></tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
                        <tr><td class="p-3 border font-medium">가산수당 (연장/야간/휴일)</td><td class="p-3 border">지급 의무 없음 (1배)</td><td class="p-3 border font-bold">50% 가산 지급 (1.5배)</td></tr>
                        <tr><td class="p-3 border font-medium">연차유급휴가</td><td class="p-3 border">부여 의무 없음</td><td class="p-3 border font-bold">법정 연차 발생 (미사용 시 수당)</td></tr>
                        <tr><td class="p-3 border font-medium">부당해고 구제신청</td><td class="p-3 border">적용 제외</td><td class="p-3 border font-bold">노동위 구제신청 가능 (해고 어려움)</td></tr>
                        <tr><td class="p-3 border font-medium">주 52시간제</td><td class="p-3 border">미적용</td><td class="p-3 border font-bold">준수 의무 적용</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="bg-emerald-50 rounded-2xl border border-emerald-100 p-6 print-break-inside-avoid">
                <h2 class="text-lg font-bold text-emerald-800 mb-4 border-b border-emerald-200 pb-2">💎 4대보험 비과세 항목 (매월 고정비 절감 설계)</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-white p-4 rounded shadow-sm text-center">
                        <p class="text-xs font-bold mb-1">🍚 식대</p>
                        <p class="text-sm text-emerald-600 font-bold">월 20만원</p>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm text-center">
                        <p class="text-xs font-bold mb-1">🚗 자가운전</p>
                        <p class="text-sm text-emerald-600 font-bold">월 20만원</p>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm text-center">
                        <p class="text-xs font-bold mb-1">👶 보육수당</p>
                        <p class="text-sm text-emerald-600 font-bold">월 20만원</p>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm text-center">
                        <p class="text-xs font-bold mb-1">🔬 연구보조</p>
                        <p class="text-sm text-emerald-600 font-bold">월 20만원</p>
                    </div>
                </div>
                <p class="text-[10px] text-emerald-700 mt-4 text-center">※ 비과세 세팅 시, 근로자 소득세 절감은 물론 사업주 4대보험료 약 10% 추가 절감 효과 발생</p>
            </div>
        </div>

        <!-- 탭 3: 법인 전환 -->
        <div id="tab_corp" class="tab-content">
            <div class="bg-white rounded-2xl border p-8">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">⚖️ 개인 vs 법인 통합 세무 비용 비교</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8 items-center">
                    <div class="space-y-4">
                        <div class="bg-red-50 p-4 rounded-xl border border-red-100">
                            <p class="text-xs font-bold text-red-800">개인 유지 시 (소득세 + 지역건보료)</p>
                            <p class="text-3xl font-bold text-red-600">{personal_total_cost:,.0f}만 원</p>
                        </div>
                        <div class="bg-blue-50 p-4 rounded-xl border border-blue-100">
                            <p class="text-xs font-bold text-blue-800">법인 전환 시 (법인세 + 급여세 + 직장4대보험)</p>
                            <p class="text-3xl font-bold text-blue-600">{corp_total_cost:,.0f}만 원</p>
                        </div>
                        <div class="bg-emerald-100 p-5 rounded-xl text-center">
                            <p class="text-lg font-bold">💡 연간 약 <span class="text-2xl text-emerald-700">{max(0, tax_diff):,.0f}만 원</span> 절감 기대</p>
                            <p class="text-[11px] text-slate-500 mt-2">※ 법인 전환 시 대표자 월 급여 {rep_salary:,}만원 비용처리 가정</p>
                        </div>
                    </div>
                    <div class="h-64 flex justify-center"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <!-- 탭 4: 인증 및 지원금 (상세 복구) -->
        <div id="tab_fixed" class="tab-content">
            <h2 class="text-xl font-bold mb-4 border-l-4 border-amber-500 pl-2">💰 고용지원금 수령 시뮬레이션 (총 {total_subsidy:,}만원 확보 예상)</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-10">
                {card_youth}{card_senior}{card_women}{card_continuous}{card_disabled}{card_parental}
            </div>
            <h2 class="text-xl font-bold mb-4 border-l-4 border-blue-500 pl-2">🏆 핵심 기업인증 패키지 (클릭 선택 가능)</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-5 rounded-xl border border-slate-200 transition-all hover:bg-blue-50 relative">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div>
                    <h3 class="font-bold text-sm mb-1">여성기업인증</h3>
                    <p class="text-[10px] text-slate-500 leading-tight">• 수의계약 5천만원 한도 확대<br>• 공공입찰 가점 부여</p>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-5 rounded-xl border border-slate-200 transition-all hover:bg-blue-50 relative">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div>
                    <h3 class="font-bold text-sm mb-1">직접생산확인서 / 공장등록</h3>
                    <p class="text-[10px] text-slate-500 leading-tight">• 나라장터 입찰 필수 요건<br>• 제조업 세제 혜택 기본</p>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-5 rounded-xl border border-slate-200 transition-all hover:bg-blue-50 relative">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div>
                    <h3 class="font-bold text-sm mb-1">ISO 9001/14001/45001</h3>
                    <p class="text-[10px] text-slate-500 leading-tight">• 품질/환경/안전 통합 인증<br>• 대기업 협력업체 필수 조건</p>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-5 rounded-xl border border-slate-200 transition-all hover:bg-blue-50 relative">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div>
                    <h3 class="font-bold text-sm mb-1">메인비즈 / 이노비즈</h3>
                    <p class="text-[10px] text-slate-500 leading-tight">• 경영/기술 혁신 인증<br>• 기보/신보 보증 우대</p>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-5 rounded-xl border border-slate-200 transition-all hover:bg-blue-50 relative">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div>
                    <h3 class="font-bold text-sm mb-1">특허 (비용 400~1000만)</h3>
                    <p class="text-[10px] text-slate-500 leading-tight">• 원천 기술 보호 및 권리화<br>• 기술 등급 상향 핵심</p>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-5 rounded-xl border border-slate-200 transition-all hover:bg-blue-50 relative">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div>
                    <h3 class="font-bold text-sm mb-1">기업부설연구소 / 전담부서</h3>
                    <p class="text-[10px] text-slate-500 leading-tight">• 법인세 25% 공제<br>• 연구인력 비과세 혜택</p>
                </div>
            </div>
        </div>

        <!-- 탭 5: 기관별 자금 (상세 복구) -->
        <div id="tab_fund" class="tab-content">
            <h2 class="text-xl font-bold mb-6 border-l-4 border-emerald-500 pl-2">🏦 기관별 정책자금 및 지원사업 상세 현황</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- 중진공 계열 -->
                <div class="bg-emerald-50 p-6 rounded-2xl border border-emerald-200 print-break-inside-avoid">
                    <h3 class="font-bold text-emerald-800 mb-3 border-b border-emerald-200 pb-2">1. 중진공 및 혁신바우처</h3>
                    <ul class="text-xs space-y-2 text-emerald-700">
                        <li><b>[직접융자]</b> 고정금리 연 2.5~3.5% 수준, 시설/운전자금 최대 5~60억</li>
                        <li><b>[혁신바우처]</b> 최대 5,000만원 무상 지원 (컨설팅, 시제품 제작, 마케팅 지원)</li>
                        <li><b>[수출바우처]</b> 해외 진출 비용 최대 3,000만원 ~ 1억원 지원</li>
                    </ul>
                </div>
                <!-- 보증기관 계열 -->
                <div class="bg-blue-50 p-6 rounded-2xl border border-blue-200 print-break-inside-avoid">
                    <h3 class="font-bold text-blue-800 mb-3 border-b border-blue-200 pb-2">2. 신보·기보 및 시중은행</h3>
                    <ul class="text-xs space-y-2 text-blue-700">
                        <li><b>[신용/기술보증]</b> 담보 없이 보증서 발급 대출 (금리 4.0~5.5%), 보증료 감면 혜택</li>
                        <li><b>[은행자금]</b> 재무제표 기준 자체 대출, 정책 자금과 연계 시 금리 우대</li>
                    </ul>
                </div>
                <!-- 안전공단 계열 -->
                <div class="bg-red-50 p-6 rounded-2xl border border-red-200 print-break-inside-avoid">
                    <h3 class="font-bold text-red-800 mb-3 border-b border-red-200 pb-2">3. 안전보건공단 지원사업</h3>
                    <ul class="text-xs space-y-2 text-red-700">
                        <li><b>[안전동행]</b> 50인 미만 고위험 사업장 설비 교체 보조금 (최대 1억, 50% 매칭)</li>
                        <li><b>[산재예방융자]</b> 위험 기계 도입 시 <b>연 1.5% 고정금리</b> 초저리 융자 (최대 10억)</li>
                    </ul>
                </div>
                <!-- 지자체 계열 -->
                <div class="bg-purple-50 p-6 rounded-2xl border border-purple-200 print-break-inside-avoid">
                    <h3 class="font-bold text-purple-800 mb-3 border-b border-purple-200 pb-2">4. 경기도 및 관내 지자체 자금</h3>
                    <ul class="text-xs space-y-2 text-purple-700">
                        <li><b>[이차보전]</b> 은행 대출 금리 중 1.0~3.0%를 도/시에서 대신 납부하여 이자 절감</li>
                        <li><b>[시흥시 자금]</b> 시 예산 기반 관내 기업 전용 저리 융자 (조기 소진 유의)</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 탭 6: 스케쥴 -->
        <div id="tab_schedule" class="tab-content">
            <div class="bg-white rounded-2xl border p-8 print-break-inside-avoid">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">📅 컨설팅 마스터 로드맵</h2>
                <div class="space-y-6">
                    <div class="flex gap-6 items-start">
                        <div class="bg-slate-800 text-white px-3 py-1 rounded font-bold text-sm">{m1:02d}월</div>
                        <div><p class="font-bold">인사/노무 기반 정비 및 비과세 설계</p><p class="text-sm text-slate-500">근로계약서, 취업규칙 정비 및 합법적 비과세 수당 세팅 완료</p></div>
                    </div>
                    <div class="flex gap-6 items-start">
                        <div class="bg-blue-600 text-white px-3 py-1 rounded font-bold text-sm">{m1:02d}월~{m2:02d}월</div>
                        <div><p class="font-bold">핵심 기업인증 획득 프로세스 가동 (3개월 집중)</p><p class="text-sm text-slate-500">메인/이노비즈, ISO, 특허 신청 및 현장 실사 대비</p></div>
                    </div>
                    <div class="flex gap-6 items-start">
                        <div class="bg-emerald-600 text-white px-3 py-1 rounded font-bold text-sm">{m3:02d}월~{m4:02d}월</div>
                        <div><p class="font-bold">법인 전환 타당성 검토 및 재무 결산</p><p class="text-sm text-slate-500">법인세/소득세 시뮬레이션 기반 법인 전환 여부 결정 및 가결산</p></div>
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
            el.classList.toggle('border-blue-500'); el.classList.toggle('ring-2'); el.classList.toggle('ring-blue-500'); el.classList.toggle('bg-blue-50');
            const badge = el.querySelector('.cert-badge'); if (badge) badge.classList.toggle('hidden');
        }}

        function executePrint() {{
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
                    borderRadius: 8
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
    st.subheader(f"💻 {client_name} 제안서 미리보기")
    components.html(html_content, height=1000, scrolling=True)
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 15px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px;">📥 제안서 HTML 파일로 저장</a>', unsafe_allow_html=True)
