import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="제이원 경영제안서 시스템", layout="wide")

st.title("📊 주식회사 제이원 - 맞춤형 경영컨설팅 시스템")
st.write("대표님들을 위해 가독성을 높인 가로 출력 최적화 버전입니다.")

# 화면 분할
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 1. 기본 정보")
    my_company_name = st.text_input("제안사 이름", "주식회사 제이원")
    client_name = st.text_input("고객사 이름", "(주)영광산업기계")
    current_employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3)
    industry_code = st.text_input("업종 코드 및 상태", "[21812] 뿌리기업 해당")

    st.subheader("📝 2. 컨설팅 제안")
    proposal_input = st.text_area("핵심 제안 내용 (줄바꿈 구분)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장에 따른 행정/노무 정비 및 지원금 수령")
    proposal_items = "".join([f"<li class='mb-4 flex items-start'><span class='text-blue-600 mr-3 text-xl'>✔</span><span class='text-lg font-medium text-slate-700'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    start_month = st.number_input("스케쥴 시작 월", min_value=1, max_value=12, value=4)
    m1 = start_month
    m2, m3, m4 = (start_month % 12)+1, (start_month+3)%12+1, (start_month+4)%12+1

    st.subheader("📝 3. 지원금 인원")
    ca, cb, cc = st.columns(3)
    with ca: 
        youth_count = st.number_input("청년도약", min_value=0, value=1)
        continuous_count = st.number_input("계속고용", min_value=0, value=0)
    with cb: 
        senior_count = st.number_input("시니어인턴", min_value=0, value=1)
        disabled_count = st.number_input("장애인", min_value=0, value=0)
    with cc: 
        women_count = st.number_input("새일여성", min_value=0, value=1)
        parental_count = st.number_input("대체인력", min_value=0, value=0)

    def generate_subsidy_card(title, eligible, scheduled_count, total_amount, max_str):
        if eligible:
            return f"""
            <div class="bg-amber-50 p-5 rounded-2xl border border-amber-200 shadow-sm print-break-inside-avoid mb-4">
                <div class="flex justify-between items-start mb-2">
                    <span class="bg-amber-200 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-full">예정: {scheduled_count}명</span>
                </div>
                <h3 class="font-bold text-amber-900 text-lg mb-1">{title}</h3>
                <p class="font-bold text-amber-600 text-2xl">{total_amount:,} <span class="text-sm">만원</span></p>
                <p class="text-[11px] text-amber-700 mt-2 font-medium">※ {max_str}</p>
            </div>"""
        else:
            return f"""<div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 opacity-60 grayscale mb-4">
                <h3 class="font-bold text-slate-500 text-lg">{title}</h3>
                <p class="font-bold text-slate-400 text-2xl">0 만원</p>
            </div>"""

    youth_eligible = current_employees >= 5
    card_youth = generate_subsidy_card("청년일자리도약", youth_eligible, youth_count, youth_count * (1200 if youth_eligible else 0), "1,200만원(2년)")
    card_senior = generate_subsidy_card("시니어인턴십", True, senior_count, senior_count * 240, "약 240만원")
    card_women = generate_subsidy_card("새일여성인턴", True, women_count, women_count * 380, "380만원")
    card_continuous = generate_subsidy_card("고령자계속고용", True, continuous_count, continuous_count * 720, "720만원(2년)")
    card_disabled = generate_subsidy_card("장애인신규고용", True, disabled_count, disabled_count * 720, "약 720만원")
    card_parental = generate_subsidy_card("육아휴직대체", True, parental_count, parental_count * 960, "960만원(1년)")
    total_subsidy = (youth_count * (1200 if youth_eligible else 0)) + (senior_count * 240) + (women_count * 380) + (continuous_count * 720) + (disabled_count * 720) + (parental_count * 960)

    st.subheader("⚖️ 4. 법인 전환 설정")
    show_corp_tab = st.toggle("법인 전환 탭 활성화", value=True)
    if show_corp_tab:
        net_income = st.number_input("당기순이익 (만원)", min_value=0, value=15000)
        rep_salary = st.number_input("대표 월 급여 (만원)", min_value=0, value=500)
        yearly_salary = rep_salary * 12
        p_total = (net_income * 0.35 * 1.1) + (net_income * 0.07)
        c_total = (max(0, net_income-yearly_salary) * 0.1 * 1.1) + (yearly_salary * 0.15 * 1.1) + (yearly_salary * 0.1869)
        tax_diff = p_total - c_total
    else: p_total, c_total, tax_diff, rep_salary = 0, 0, 0, 0

    st.subheader("📝 5. 노무 기준")
    min_wage = st.number_input("2026 최저시급", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# ----------------------------------------------------------------------------------
# HTML/CSS 시작 (2pt 상향 가독성 버전)
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
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; font-size: 17px; }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        .text-gradient {{ background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(to right, #2563eb, #059669); }}
        
        @media print {{
            @page {{ size: A4 landscape; margin: 10mm; }}
            body {{ background-color: #ffffff !important; font-size: 18px !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            .tab-content {{ display: none !important; }}
            .tab-content.print-active {{ display: block !important; page-break-before: always !important; padding-top: 15px !important; }}
            #tab_proposal.print-active {{ page-break-before: avoid !important; }}
            .print-break-inside-avoid {{ page-break-inside: avoid; break-inside: avoid; }}
            h2 {{ font-size: 30px !important; margin-bottom: 25px !important; border-bottom: 4px solid #3b82f6 !important; }}
        }}
        
        h2 {{ font-size: 26px; font-weight: 700; }}
        .info-text {{ font-size: 18px; line-height: 1.7; }}
        table th, table td {{ padding: 12px; font-size: 16px; border: 1px solid #e2e8f0; }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-10 pb-10 px-10 relative">
        <div class="max-w-7xl mx-auto flex justify-between items-end relative z-10">
            <div>
                <p class="text-amber-400 font-bold text-sm mb-1 uppercase tracking-wider">Master Consulting Plan</p>
                <h1 class="text-4xl font-bold mb-2 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 text-sm font-medium">업종: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right">
                <button id="print_btn" onclick="executePrint()" class="mb-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all cursor-pointer">🖨️ 가로 전체 인쇄</button>
                <p class="text-slate-400 text-xs">제안일자: <span id="auto_date"></span></p>
                <p class="text-xl font-bold mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <div class="bg-white border-b sticky top-0 z-20 shadow-sm overflow-x-auto">
        <div class="max-w-7xl mx-auto px-10 flex space-x-10">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-5 font-bold text-blue-600 border-b-4 border-blue-600 whitespace-nowrap">1. 핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap">2. 노무/비과세</button>
            {'<button onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap">3. 법인 전환</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap">4. 인증/지원금</button>
            <button onclick="switchTab('tab_fund', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap">5. 기관별 자금</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-5 font-bold text-slate-500 whitespace-nowrap">6. 스케쥴</button>
        </div>
    </div>

    <main class="max-w-7xl mx-auto px-10 py-10">
        <!-- 핵심제안 -->
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white rounded-3xl shadow-sm border p-12">
                <h2 class="text-slate-800 mb-8 pb-4 border-b-4 border-blue-500 inline-block">💡 {client_name} 경영 고도화 전략</h2>
                <ul class="info-text space-y-4">{proposal_items}</ul>
            </div>
        </div>

        <!-- 노무 상세 -->
        <div id="tab_labor" class="tab-content print-active">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 print-break-inside-avoid">
                <div class="bg-white rounded-3xl border border-blue-100 p-8 shadow-sm">
                    <h2 class="text-blue-800 mb-6">⏱️ 2026 최저임금 의무</h2>
                    <div class="flex justify-between mb-4 items-center"><span>시급</span><p class="text-3xl font-bold">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-5 rounded-2xl flex justify-between font-bold text-blue-700">
                        <span>월 환산(209h)</span><span class="text-3xl">{monthly_wage:,}원</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-6 font-medium">※ 최저임금 미달 시 형사처벌 및 징역 대상이 될 수 있습니다.</p>
                </div>
                <div class="bg-red-50 rounded-3xl border border-red-200 p-8 text-red-900 shadow-sm">
                    <h2 class="mb-4">🚨 근로계약서 미작성 리스크</h2>
                    <ul class="space-y-3 text-lg font-medium">
                        <li>• 정규직 미작성: 벌금 최대 500만원 (전과 기록)</li>
                        <li>• 단시간 미작성: 과태료 500만원 즉시 부과</li>
                        <li>• 분쟁 발생 시 사업주 100% 입증 책임 및 불리</li>
                    </ul>
                </div>
            </div>
            <div class="bg-white rounded-3xl border p-10 mb-10 print-break-inside-avoid">
                <h2 class="mb-8">🏢 5인 미만 vs 5인 이상 차이표</h2>
                <table class="w-full text-left">
                    <thead class="bg-slate-800 text-white font-bold">
                        <tr><th class="p-4 border">구분</th><th class="p-4 border">5인 미만</th><th class="p-4 border text-amber-400">5인 이상 (관리 대상)</th></tr>
                    </thead>
                    <tbody class="text-slate-700 font-medium">
                        <tr><td class="p-4 border bg-slate-50">가산수당</td><td class="p-4 border">없음 (1배)</td><td class="p-4 border font-bold text-red-600">50% 가산 지급 (1.5배)</td></tr>
                        <tr><td class="p-4 border bg-slate-50">연차휴가</td><td class="p-4 border">의무 없음</td><td class="p-4 border font-bold text-red-600">법정 연차 발생 및 정산 의무</td></tr>
                        <tr><td class="p-4 border bg-slate-50">해고구제</td><td class="p-4 border">비교적 자유</td><td class="p-4 border font-bold text-red-600">노동위 부당해고 구제 신청 가능</td></tr>
                    </tbody>
                </table>
            </div>
            <div class="bg-emerald-50 rounded-3xl border border-emerald-200 p-10 print-break-inside-avoid">
                <h2 class="text-emerald-800 mb-8 border-b-2 border-emerald-200 pb-2">💎 4대보험 비과세 설계 (월 고정비 절감)</h2>
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-6 font-bold text-center">
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-sm mb-1">식대</p><p class="text-2xl text-emerald-600">월 20만</p></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-sm mb-1">자가운전</p><p class="text-2xl text-emerald-600">월 20만</p></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-sm mb-1">보육수당</p><p class="text-2xl text-emerald-600">월 20만</p></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-sm mb-1">연구보조비</p><p class="text-2xl text-emerald-600">월 20만</p></div>
                </div>
            </div>
        </div>

        <!-- 법인전환 -->
        <div id="tab_corp" class="tab-content {'print-active' if show_corp_tab else ''}">
            <div class="bg-white rounded-3xl border p-12 shadow-sm">
                <h2 class="text-slate-800 mb-10 pb-4 border-b-4 border-indigo-500 inline-block">⚖️ 개인 vs 법인 통합 세무 분석</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    <div class="space-y-6">
                        <div class="bg-red-50 p-8 rounded-3xl border border-red-100">
                            <p class="text-sm font-bold text-red-800 mb-1">개인사업 유지 시 비용</p>
                            <p class="text-5xl font-bold text-red-600">{p_total:,.0f} <span class="text-xl">만원</span></p>
                        </div>
                        <div class="bg-blue-50 p-8 rounded-3xl border border-blue-100">
                            <p class="text-sm font-bold text-blue-800 mb-1">법인 전환 시 비용 (급여 포함)</p>
                            <p class="text-5xl font-bold text-blue-600">{c_total:,.0f} <span class="text-xl">만원</span></p>
                        </div>
                        <div class="bg-emerald-100 p-8 rounded-3xl text-center border-2 border-emerald-200">
                            <p class="text-3xl font-bold text-emerald-900">💡 예상 절세액: <span class="text-5xl text-emerald-600">{max(0, tax_diff):,.0f}만 원</span></p>
                        </div>
                    </div>
                    <div class="h-80"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <!-- 인증/지원금 -->
        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="mb-10 border-l-8 border-amber-400 pl-4">💰 고용지원금 수령 시뮬레이션</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
                {card_youth}{card_senior}{card_women}{card_continuous}{card_disabled}{card_parental}
            </div>
            <h2 class="mb-10 border-l-8 border-blue-500 pl-4">🏆 기업 핵심 인증 리스트</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-6 rounded-2xl border-2 border-slate-100 shadow-sm relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl hidden">대상</div>
                    <h3 class="font-bold text-xl mb-3">여성기업인증</h3><ul class="text-sm text-slate-500 space-y-1 font-medium"><li>• 수의계약 5천만원 한도 상향</li><li>• 공공입찰 가점 및 우선 지원</li></ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-6 rounded-2xl border-2 border-slate-100 shadow-sm relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl hidden">대상</div>
                    <h3 class="font-bold text-xl mb-3">직접생산 / 공장등록</h3><ul class="text-sm text-slate-500 space-y-1 font-medium"><li>• 나라장터 조달 입찰 필수 요건</li><li>• 제조업 전용 세제 혜택 부여</li></ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-6 rounded-2xl border-2 border-slate-100 shadow-sm relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl hidden">대상</div>
                    <h3 class="font-bold text-xl mb-3">메인/이노비즈</h3><ul class="text-sm text-slate-500 space-y-1 font-medium"><li>• 기술/경영 혁신형 중소기업 인증</li><li>• 정책자금 금리 인하 및 한도 우대</li></ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-6 rounded-2xl border-2 border-slate-100 shadow-sm relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl hidden">대상</div>
                    <h3 class="font-bold text-xl mb-3">ISO 9001 / 45001</h3><ul class="text-sm text-slate-500 space-y-1 font-medium"><li>• 품질 및 안전보건 경영 표준</li><li>• 중대재해처벌법 대응 필수 요소</li></ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-6 rounded-2xl border-2 border-slate-100 shadow-sm relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl hidden">대상</div>
                    <h3 class="font-bold text-xl mb-3">특허 확보</h3><ul class="text-sm text-slate-500 space-y-1 font-medium"><li>• 핵심 기술 권리 보호 (400~1000만)</li><li>• 자금 유치를 위한 기술 가점</li></ul>
                </div>
                <div onclick="toggleCert(this)" class="cert-card cursor-pointer bg-white p-6 rounded-2xl border-2 border-slate-100 shadow-sm relative transition-all">
                    <div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl hidden">대상</div>
                    <h3 class="font-bold text-xl mb-3">기업부설연구소</h3><ul class="text-sm text-slate-500 space-y-1 font-medium"><li>• 법인세 25% 공제 혜택</li><li>• 연구원 인당 월 20만 비과세</li></ul>
                </div>
            </div>
        </div>

        <!-- 자금 상세 -->
        <div id="tab_fund" class="tab-content print-active">
            <h2 class="mb-10 border-l-8 border-emerald-500 pl-4 text-emerald-800">🏦 기관별 정책자금 가이드</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 font-medium">
                <div class="bg-emerald-50 p-10 rounded-3xl border border-emerald-200 print-break-inside-avoid">
                    <h3 class="font-bold text-emerald-800 text-2xl mb-6 border-b border-emerald-200 pb-3 text-center">🟢 1. 중진공 및 바우처</h3>
                    <ul class="text-lg space-y-4 text-emerald-700">
                        <li><b>[직접융자]</b> 고정금리 2.5~3.5% (운전 5억/시설 60억)</li>
                        <li><b>[혁신바우처]</b> 최대 5,000만원 무상 지원</li>
                        <li><b>[수출바우처]</b> 해외 진출 비용 1억원 한도 지원</li>
                    </ul>
                </div>
                <div class="bg-blue-50 p-10 rounded-3xl border border-blue-200 print-break-inside-avoid">
                    <h3 class="font-bold text-blue-800 text-2xl mb-6 border-b border-blue-200 pb-3 text-center">🔵 2. 보증기관 및 금융권</h3>
                    <ul class="text-lg space-y-4 text-blue-700">
                        <li><b>[보증서 대출]</b> 기술력 기반 보증서 발급 (금리 4.0~5.5%)</li>
                        <li><b>[시중은행]</b> 정책 연계 이자 감면 및 한도 최적화 매칭</li>
                    </ul>
                </div>
                <div class="bg-red-50 p-10 rounded-3xl border border-red-200 print-break-inside-avoid">
                    <h3 class="font-bold text-red-800 text-2xl mb-6 border-b border-red-200 pb-3 text-center">🔴 3. 안전보건공단 지원</h3>
                    <ul class="text-lg space-y-4 text-red-700">
                        <li><b>[안전동행]</b> 고위험 설비 교체 무상 지원 (최대 1억)</li>
                        <li><b>[산재예방융자]</b> 연 1.5% 고정금리 초저리 지원 (최대 10억)</li>
                    </ul>
                </div>
                <div class="bg-purple-50 p-10 rounded-3xl border border-purple-200 print-break-inside-avoid">
                    <h3 class="font-bold text-purple-800 text-2xl mb-6 border-b border-purple-200 pb-3 text-center">🟣 4. 지자체 자금 (이차보전)</h3>
                    <ul class="text-lg space-y-4 text-purple-700">
                        <li><b>[이차보전]</b> 대출 이자 중 1.0~3.0%를 지자체가 대신 납부</li>
                        <li><b>[관내자금]</b> 시흥시 등 관내 예산 기반 저리 융자 지원</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 스케쥴 -->
        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-white rounded-3xl border p-12 print-break-inside-avoid shadow-sm">
                <h2 class="mb-10 pb-4 border-b-4 border-slate-800 inline-block font-bold">📅 컨설팅 마스터 로드맵</h2>
                <div class="space-y-12">
                    <div class="flex gap-8 items-start">
                        <div class="bg-slate-800 text-white px-6 py-2 rounded-2xl font-bold text-xl">{m1:02d}월</div>
                        <div><p class="text-xl font-bold mb-1">인사/노무 정비 및 비과세 최적화</p><p class="text-lg text-slate-500 font-medium">근로계약서 전면 개편 및 고정비 절감 설계</p></div>
                    </div>
                    <div class="flex gap-8 items-start">
                        <div class="bg-blue-600 text-white px-6 py-2 rounded-2xl font-bold text-xl">{m1:02d}월~{m3:02d}월</div>
                        <div><p class="text-xl font-bold mb-1">핵심 기업인증 획득 (3개월 집중)</p><p class="text-lg text-slate-500 font-medium">벤처/메인/ISO 등 핵심 자격 완비</p></div>
                    </div>
                    <div class="flex gap-8 items-start">
                        <div class="bg-emerald-600 text-white px-6 py-2 rounded-2xl font-bold text-xl">{m3:02d}월~{m4:02d}월</div>
                        <div><p class="text-xl font-bold mb-1">법인전환 및 자금 유치</p><p class="text-lg text-slate-500 font-medium">절세 시뮬레이션 기반 법인전환 및 정책자금 실행</p></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const now = new Date();
        document.getElementById('auto_date').innerText = now.getFullYear() + '년 ' + (now.getMonth()+1) + '월 ' + now.getDate() + '일';

        function switchTab(tabId, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('text-blue-600', 'border-blue-600'));
            element.classList.add('text-blue-600', 'border-blue-600');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        }}

        function toggleCert(el) {{
            el.classList.toggle('border-blue-500'); el.classList.toggle('ring-4'); el.classList.toggle('ring-blue-100');
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
                labels: ['개인사업 유지', '법인 전환'],
                datasets: [{{
                    data: [{p_total}, {c_total}],
                    backgroundColor: ['#ef4444', '#3b82f6'],
                    borderRadius: 10
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
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 20px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 12px; font-weight: bold; margin-top: 10px; font-size: 18px;">📥 최종 제안서 파일 저장하기</a>', unsafe_allow_html=True)
