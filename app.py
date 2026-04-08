import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="제이원 통합 경영제안서 시스템", layout="wide")

st.title("📊 주식회사 제이원 - 가로 출력 최적화 시스템")
st.write("모든 상세 데이터가 요약 없이 반영됩니다. [인쇄하기] 버튼 클릭 시 가로형 A4로 자동 분할됩니다.")

# 2. 화면 분할 (입력폼)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 1. 기본 및 고객사 정보")
    my_company_name = st.text_input("제안사 이름", "주식회사 제이원")
    client_name = st.text_input("고객사 이름", "(주)영광산업기계")
    current_employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3, step=1)
    industry_code = st.text_input("업종 코드 및 상태", "[21812] 뿌리기업 해당")

    st.subheader("📝 2. 컨설팅 제안 상세")
    proposal_input = st.text_area("핵심 제안 내용 (원문 보존)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장 진입에 따른 행정/노무 정비 및 지원금 수령")
    proposal_items = "".join([f"<li class='mb-2 flex items-start'><span class='text-blue-500 mr-2 font-bold'>✔</span><span class='break-keep font-medium'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    start_month = st.number_input("스케쥴 시작 월", min_value=1, max_value=12, value=4)
    m1 = start_month
    m2, m3, m4 = (start_month % 12)+1, (start_month+3)%12+1, (start_month+4)%12+1

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

    # 지원금 계산 로직
    youth_eligible = current_employees >= 5
    card_total_subsidy = (youth_count * (1200 if youth_eligible else 0)) + (senior_count * 240) + (women_count * 380) + (continuous_count * 720) + (disabled_count * 720) + (parental_count * 960)

    # 지원금 카드 HTML 생성기
    def generate_subsidy_card(title, target, eligible, max_amount_str, scheduled_count, total_amount):
        bg = "bg-amber-50" if eligible else "bg-slate-50"
        border = "border-amber-200" if eligible else "border-slate-200"
        opacity = "opacity-100" if eligible else "opacity-60 grayscale"
        return f"""
        <div class="{bg} p-4 rounded-xl border {border} shadow-sm relative print-break-inside-avoid {opacity} mb-2 h-full">
            <div class="absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg">예정: {scheduled_count}명</div>
            <h3 class="font-bold text-slate-800 text-sm mb-1">{title}</h3>
            <p class="font-black text-blue-800 text-xl">{total_amount:,}<span class="text-xs font-normal text-slate-600"> 만원</span></p>
            <p class="text-[10px] text-slate-500 mt-2 font-bold">※ {max_amount_str}</p>
        </div>
        """

    card_youth = generate_subsidy_card("청년도약장려금", "청년", youth_eligible, "1,200만원(2년)", youth_count, youth_count * (1200 if youth_eligible else 0))
    card_senior = generate_subsidy_card("시니어인턴십", "60세↑", True, "약 240만원", senior_count, senior_count * 240)
    card_women = generate_subsidy_card("새일여성인턴", "경단녀", True, "380만원", women_count, women_count * 380)
    card_continuous = generate_subsidy_card("고령자계속고용", "정년연장", True, "720만원(2년)", continuous_count, continuous_count * 720)
    card_disabled = generate_subsidy_card("장애인신규고용", "장애인", True, "약 720만원", disabled_count, disabled_count * 720)
    card_parental = generate_subsidy_card("육아휴직대체", "대체인력", True, "960만원(1년)", parental_count, parental_count * 960)

    st.subheader("⚖️ 4. 법인 전환 시뮬레이터")
    show_corp_tab = st.toggle("법인 전환 검토 탭 활성화", value=True)
    if show_corp_tab:
        net_income = st.number_input("당기순이익 (만원)", min_value=0, value=15000, step=1000)
        rep_salary = st.number_input("대표자 월 급여 (만원)", min_value=0, value=500, step=50)
        yearly_salary = rep_salary * 12
        p_tax_val = (net_income * 0.35) * 1.1 # 간이 계산용
        p_health_val = net_income * 0.0709 
        personal_total_cost = p_tax_val + p_health_val
        corp_profit = max(0, net_income - yearly_salary)
        c_tax_val = (corp_profit * 0.09 if corp_profit <= 20000 else 1800 + (corp_profit-20000)*0.19) * 1.1
        s_tax_val = (yearly_salary * 0.15) * 1.1 
        total_insurance = yearly_salary * 0.1869 
        corp_total_cost = c_tax_val + s_tax_val + total_insurance
        tax_diff = personal_total_cost - corp_total_cost
    else:
        personal_total_cost, corp_total_cost, tax_diff, rep_salary = 0, 0, 0, 0

    st.subheader("📝 5. 노무 기준")
    min_wage = st.number_input("2026년 최저시급 (원)", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# ----------------------------------------------------------------------------------
# HTML (그래프 복구 및 노무/비과세 통합 레이아웃)
# ----------------------------------------------------------------------------------
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .text-gradient {{ background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(to right, #1d4ed8, #059669); }}
        
        @media print {{
            @page {{ size: A4 landscape; margin: 10mm; }}
            body {{ background-color: #ffffff !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            .tab-content {{ display: none !important; }}
            .tab-content.print-active {{ 
                display: block !important; 
                opacity: 1 !important; 
                page-break-after: always !important; 
                margin-top: 0 !important;
                padding: 10px !important;
            }}
            #tab_schedule.print-active {{ page-break-after: auto !important; }}
            .print-break-inside-avoid {{ page-break-inside: avoid; break-inside: avoid; }}
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #e2e8f0 !important; }}
            h2 {{ font-size: 24pt !important; border-bottom: 4px solid #1e40af !important; padding-bottom: 8px !important; margin-bottom: 20px !important; }}
        }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-10 pb-10 px-8 relative">
        <div class="absolute inset-0 opacity-20" style="background: radial-gradient(circle at top right, #3b82f6, transparent);"></div>
        <div class="max-w-7xl mx-auto relative z-10 flex justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-sm mb-1 uppercase">Master Consulting Plan</p>
                <h1 class="text-3xl font-black mb-2 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 text-xs font-bold">업종코드: {industry_code} | 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right flex flex-col items-end">
                <button id="print_btn" onclick="executePrint()" class="mb-4 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-2 px-5 rounded-xl shadow-xl transition-all cursor-pointer">🖨️ 가로형 전체 인쇄하기</button>
                <p class="text-slate-400 text-xs">작성일: <span id="auto_date"></span></p>
                <p class="text-xl font-black mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <nav class="bg-white border-b sticky top-0 z-50 overflow-x-auto shadow-sm no-print">
        <div class="max-w-7xl mx-auto px-6 flex space-x-8 text-sm">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-4 font-bold text-blue-600 border-b-2 border-blue-600 whitespace-nowrap">핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">노무/비과세 통합</button>
            {'<button id="btn_corp" onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">법인 전환 검토</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">인증/지원금 상세</button>
            <button onclick="switchTab('tab_fund', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">기관별 자금 상세</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">마스터 스케쥴</button>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-8 py-10">
        <!-- 탭 1: 핵심 제안 -->
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white rounded-3xl shadow-sm border border-slate-100 p-10">
                <h2 class="text-2xl font-black text-slate-800 mb-8 border-b-4 border-blue-600 inline-block pb-2">💡 {client_name} 경영 최적화 전략</h2>
                <ul class="space-y-4 text-lg">{proposal_items}</ul>
            </div>
        </div>

        <!-- 탭 2: 노무 및 비과세 (한 페이지 통합 배치) -->
        <div id="tab_labor" class="tab-content print-active">
            <h2 class="text-2xl font-black text-slate-800 mb-6 border-b-4 border-blue-600 inline-block pb-2">🏢 노무 관리 고도화 및 비과세 최적화</h2>
            
            <div class="grid grid-cols-2 gap-6 mb-6">
                <!-- 최저임금 -->
                <div class="bg-white rounded-2xl border-2 border-blue-50 p-6 shadow-sm print-break-inside-avoid">
                    <h3 class="text-blue-800 font-bold mb-4 border-b pb-2 text-lg">⏱️ 2026 최저임금 기준</h3>
                    <div class="flex justify-between mb-2"><span>2026 결정 시급</span><p class="font-black text-xl">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-4 rounded-xl flex justify-between font-black text-blue-700">
                        <span>월 환산액 (209h)</span><span>{monthly_wage:,}원</span>
                    </div>
                </div>
                <!-- 계약서 리스크 -->
                <div class="bg-red-50 rounded-2xl border-2 border-red-100 p-6 text-red-900 shadow-sm print-break-inside-avoid">
                    <h3 class="font-black mb-2 text-lg">🚨 근로계약서 미작성 리스크</h3>
                    <ul class="text-xs space-y-1 font-bold">
                        <li>• 정규직 미작성: 벌금 최대 500만원 (전과 기록 남음)</li>
                        <li>• 기간제 미작성: 과태료 500만원 즉시 부과</li>
                        <li>• 분쟁 시 사업주 100% 입증 책임 및 불리</li>
                    </ul>
                </div>
            </div>

            <!-- 차이표 -->
            <div class="bg-white rounded-2xl border p-6 mb-6 print-break-inside-avoid shadow-sm">
                <h3 class="text-slate-800 font-bold mb-4 pl-4 border-l-4 border-slate-800 text-lg">상시근로자 5인 미만 vs 5인 이상 주요 차이</h3>
                <table class="w-full text-xs text-left border-collapse border border-slate-200">
                    <thead class="bg-slate-100 text-slate-700 font-bold">
                        <tr><th class="p-3 border">구분</th><th class="p-3 border">5인 미만 사업장</th><th class="p-3 border bg-blue-50 text-blue-700">5인 이상 사업장 (중점관리)</th></tr>
                    </thead>
                    <tbody class="text-slate-600 font-medium">
                        <tr><td class="p-3 border font-black bg-slate-50">가산수당</td><td class="p-3 border">의무 없음 (1배)</td><td class="p-3 border font-black text-red-600 text-sm">통상임금 50% 가산 (1.5배)</td></tr>
                        <tr><td class="p-3 border font-black bg-slate-50">연차유급휴가</td><td class="p-3 border">부여 의무 없음</td><td class="p-3 border font-black text-red-600 text-sm">법정 연차 발생 및 정산 의무</td></tr>
                        <tr><td class="p-3 border font-black bg-slate-50">부당해고구제</td><td class="p-3 border">적용 제외 (해고 자유)</td><td class="p-3 border font-black text-red-600 text-sm">노동위 신청 가능 (절차 엄격)</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- 비과세 (하단에 배치하여 페이지 채움) -->
            <div class="bg-emerald-50 rounded-2xl border-2 border-emerald-100 p-6 print-break-inside-avoid shadow-sm">
                <h3 class="text-emerald-800 font-black mb-4 text-lg">💎 합법적 4대보험 비과세 설계 (월 고정비 절감)</h3>
                <div class="grid grid-cols-4 gap-4">
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-50"><p class="text-[10px] font-bold text-slate-500 mb-1">식대</p><p class="text-lg font-black text-emerald-600">월 20만</p></div>
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-50"><p class="text-[10px] font-bold text-slate-500 mb-1">자가운전</p><p class="text-lg font-black text-emerald-600">월 20만</p></div>
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-50"><p class="text-[10px] font-bold text-slate-500 mb-1">보육수당</p><p class="text-lg font-black text-emerald-600">월 20만</p></div>
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-50"><p class="text-[10px] font-bold text-slate-500 mb-1">연구보조</p><p class="text-lg font-black text-emerald-600">월 20만</p></div>
                </div>
            </div>
        </div>

        <!-- 탭 3: 법인 전환 (그래프 포함) -->
        <div id="tab_corp" class="tab-content {'print-active' if show_corp_tab else ''}">
            <div class="bg-white rounded-3xl border border-slate-200 p-10 shadow-sm">
                <h2 class="text-2xl font-black text-slate-800 mb-8 border-b-4 border-indigo-500 inline-block pb-2">⚖️ 개인 vs 법인 통합 세무 분석</h2>
                <div class="grid grid-cols-2 gap-10 items-center">
                    <div class="space-y-6">
                        <div class="bg-red-50 p-6 rounded-2xl border border-red-100"><p class="text-xs font-bold text-red-800 mb-1">개인 유지 비용 (소득세+건보료)</p><p class="text-4xl font-black text-red-600">{personal_total_cost:,.0f}만 원</p></div>
                        <div class="bg-blue-50 p-6 rounded-2xl border border-blue-100"><p class="text-xs font-bold text-blue-800 mb-1">법인 전환 비용 (급여+보험 통합)</p><p class="text-4xl font-black text-blue-600">{corp_total_cost:,.0f}만 원</p></div>
                        <div class="bg-emerald-100 p-8 rounded-2xl text-center border-2 border-emerald-200 shadow-md">
                            <p class="text-3xl font-black text-emerald-900">💡 예상 절세액: {max(0, tax_diff):,.0f}만 원</p>
                        </div>
                    </div>
                    <div class="h-[350px] flex justify-center bg-slate-50 rounded-2xl p-4 shadow-inner"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <!-- 탭 4: 인증/지원금 -->
        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="text-2xl font-black mb-8 border-l-8 border-amber-400 pl-4">💰 고용지원금 시뮬레이션</h2>
            <div class="grid grid-cols-3 gap-4 mb-10">{card_youth}{card_senior}{card_women}{card_continuous}{card_disabled}{card_parental}</div>
            <h2 class="text-2xl font-black mb-8 border-l-8 border-blue-600 pl-4">🏆 기업 핵심 인증 상세 혜택</h2>
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-white border p-6 rounded-2xl shadow-sm relative transition-all" onclick="toggleCert(this)"><div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div><h4 class="font-black text-lg mb-3">여성기업인증</h4><p class="text-xs text-slate-500 font-bold">• 수의계약 5천만원 확대<br>• 공공입찰 가점 부여</p></div>
                <div class="bg-white border p-6 rounded-2xl shadow-sm relative transition-all" onclick="toggleCert(this)"><div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div><h4 class="font-black text-lg mb-3">직산 / 공장등록</h4><p class="text-xs text-slate-500 font-bold">• 나라장터 참여 필수<br>• 제조업 세제 혜택 부여</p></div>
                <div class="bg-white border p-6 rounded-2xl shadow-sm relative transition-all" onclick="toggleCert(this)"><div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div><h4 class="font-black text-lg mb-3">메인 / 이노비즈</h4><p class="text-xs text-slate-500 font-bold">• 기술/경영 혁신형 인증<br>• 정책자금 우대 금리</p></div>
                <div class="bg-white border p-6 rounded-2xl shadow-sm relative transition-all" onclick="toggleCert(this)"><div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div><h4 class="font-black text-lg mb-3">ISO 통합 인증</h4><p class="text-xs text-slate-500 font-bold">• 품질/환경/안전 규격<br>• 대기업 협력 필수 요건</p></div>
                <div class="bg-white border p-6 rounded-2xl shadow-sm relative transition-all" onclick="toggleCert(this)"><div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div><h4 class="font-black text-lg mb-3">특허 확보</h4><p class="text-xs text-slate-500 font-bold">• 원천 기술 보호 (4~1천만)<br>• 자금 유치 핵심 가점</p></div>
                <div class="bg-white border p-6 rounded-2xl shadow-sm relative transition-all" onclick="toggleCert(this)"><div class="cert-badge absolute right-0 top-0 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg hidden">대상</div><h4 class="font-black text-lg mb-3">기업부설연구소</h4><p class="text-xs text-slate-500 font-bold">• 인건비 25% 법인세 공제<br>• 연구인력 비과세 혜택</p></div>
            </div>
        </div>

        <!-- 탭 5: 기관별 자금 -->
        <div id="tab_fund" class="tab-content print-active">
            <h2 class="text-2xl font-black mb-10 border-l-8 border-emerald-500 pl-4 text-emerald-800">🏦 기관별 정책자금 상세 가이드</h2>
            <div class="grid grid-cols-2 gap-8">
                <div class="bg-white border-t-8 border-emerald-500 p-8 rounded-3xl shadow-xl print-break-inside-avoid">
                    <h3 class="font-black text-emerald-800 text-xl mb-4 border-b-2 pb-2">🟢 1. 중소벤처기업진흥공단 및 바우처</h3>
                    <ul class="text-sm space-y-4 text-slate-600 font-bold leading-relaxed">
                        <li>• <b>[융자]</b> 고정금리 2.5~3.5% (시설 최대 60억/운전 5억)</li>
                        <li>• <b>[혁신바우처]</b> 최대 5,000만원 무상 지원 (마케팅, 시제품 등)</li>
                        <li>• <b>[수출바우처]</b> 해외 진출 지원 최대 1억원 (90% 지원)</li>
                    </ul>
                </div>
                <div class="bg-white border-t-8 border-red-500 p-8 rounded-3xl shadow-xl print-break-inside-avoid">
                    <h3 class="font-black text-red-800 text-xl mb-4 border-b-2 pb-2">🔴 2. 안전보건공단 지원사업</h3>
                    <ul class="text-sm space-y-4 text-slate-600 font-bold leading-relaxed">
                        <li>• <b>[안전동행지원]</b> 고위험 설비 교체 보조금 최대 1억 (50% 매칭)</li>
                        <li>• <b>[산재예방융자]</b> <b>연 1.5% 고정금리</b> 초저리 지원 (최대 10억)</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 탭 6: 스케쥴 -->
        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-slate-900 text-white rounded-[40px] p-12 shadow-2xl">
                <h2 class="text-amber-400 font-black text-3xl mb-12 border-b border-slate-700 pb-6 text-center">📅 J-ONE 컨설팅 로드맵</h2>
                <div class="space-y-12">
                    <div class="flex gap-10 items-start">
                        <div class="text-5xl font-black text-slate-600">{m1:02d}월</div>
                        <div><p class="text-2xl font-black mb-2">인사/노무 기반 정비 및 비과세 최적화</p><p class="text-xl text-slate-400 font-bold">근로계약서 전면 개편 및 고정비 절감 설계 완료</p></div>
                    </div>
                    <div class="flex gap-10 items-start">
                        <div class="text-5xl font-black text-blue-500">{m1:02d}~{m3:02d}월</div>
                        <div><p class="text-2xl font-black mb-2">기업 핵심인증 집중 확보기</p><p class="text-xl text-slate-400 font-bold">벤처/메인/이노비즈 및 ISO 통합 인증 프로세스 완료</p></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const now = new Date();
        document.getElementById('auto_date').innerText = now.getFullYear() + '년 ' + (now.getMonth()+1) + '월 ' + now.getDate() + '일';

        function switchTab(tabId, element) {{
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('text-blue-600', 'border-blue-600', 'font-bold'));
            document.getElementById(tabId).classList.add('active');
            element.classList.add('text-blue-600', 'border-blue-600', 'font-bold');
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
    st.subheader(f"💻 제안서 실시간 미리보기")
    components.html(html_content, height=1000, scrolling=True)
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_제안서.html" style="display: block; width: 100%; text-align: center; padding: 18px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 12px; font-weight: bold; margin-top: 10px; font-size: 16px;">💾 제안서 파일 저장 및 출력용 다운로드</a>', unsafe_allow_html=True)
