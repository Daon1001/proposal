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
    my_company_name = st.text_input("제안사 이름", "주식회사 제이원")
    client_name = st.text_input("고객사 이름", "(주)영광산업기계")
    current_employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3)
    
    st.subheader("📝 2. 맞춤 컨설팅 정보")
    industry_code = st.text_input("업종 코드 및 상태", "[21812] 뿌리기업 해당")
    proposal_input = st.text_area("핵심 제안 내용 (줄바꿈으로 구분)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장 진입에 따른 행정/노무 정비 및 지원금 수령")
    proposal_items = "".join([f"<li class='mb-2 flex items-start'><span class='text-blue-500 mr-2'>✔</span><span class='break-keep'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    start_month = st.number_input("스케쥴 시작 월", min_value=1, max_value=12, value=4)
    m1, m2, m3, m4 = start_month, (start_month % 12)+1, (start_month+1)%12+1, (start_month+2)%12+1

    st.subheader("📝 3. 고용지원금 설정")
    c1, c2, c3 = st.columns(3)
    with c1: 
        youth_count = st.number_input("청년도약", min_value=0, value=1)
        continuous_count = st.number_input("계속고용", min_value=0, value=0)
    with c2: 
        senior_count = st.number_input("시니어인턴", min_value=0, value=1)
        disabled_count = st.number_input("장애인", min_value=0, value=0)
    with c3: 
        women_count = st.number_input("새일여성", min_value=0, value=1)
        parental_count = st.number_input("대체인력", min_value=0, value=0)

    # 지원금 계산 로직
    youth_eligible = current_employees >= 5
    youth_total = youth_count * (1200 if youth_eligible else 0)
    senior_total, women_total = senior_count * 240, women_count * 380
    continuous_total, disabled_total, parental_total = continuous_count * 720, disabled_count * 720, parental_count * 960
    total_subsidy = youth_total + senior_total + women_total + continuous_total + disabled_total + parental_total

    st.subheader("⚖️ 4. 법인 전환 검토 설정")
    show_corp_tab = st.toggle("법인 전환 검토 탭 활성화", value=True)
    
    if show_corp_tab:
        net_income = st.number_input("예상 당기순이익 (단위: 만원)", min_value=0, value=15000, step=1000)
        rep_salary = st.number_input("법인 전환 시 대표자 월 급여 (단위: 만원)", min_value=0, value=500, step=50)
        yearly_salary = rep_salary * 12
        
        # 1. 개인사업자 세금 (종소세 + 지역건보료 약 7%)
        def calc_personal_tax(income):
            if income <= 1400: return income * 0.06
            elif income <= 5000: return 84 + (income - 1400) * 0.15
            elif income <= 8800: return 624 + (income - 5000) * 0.24
            elif income <= 15000: return 1536 + (income - 8800) * 0.35
            elif income <= 30000: return 3706 + (income - 15000) * 0.38
            else: return 9406 + (income - 30000) * 0.40 # 간략화
            
        p_tax = calc_personal_tax(net_income) * 1.1 # 지방세 포함
        p_health = net_income * 0.07 # 지역가입자 건보료 대략적 7%
        personal_total_cost = p_tax + p_health

        # 2. 법인 전환 시 세금 (법인세 + 대표 근로소득세 + 직장건보료)
        # 법인 이익 = 순이익 - 대표급여(비용처리)
        corp_profit = max(0, net_income - yearly_salary)
        c_tax = (corp_profit * 0.10 if corp_profit <= 20000 else 2000 + (corp_profit-20000)*0.20) * 1.1
        
        # 대표 근로소득세 (간이 계산)
        def calc_salary_tax(salary):
            return calc_personal_tax(salary * 0.8) # 근로소득공제 등 대략 반영
        s_tax = calc_salary_tax(yearly_salary) * 1.1
        
        # 4대보험 (직장가입자 - 요율 2026년 기준 근로자+사업주 합산 약 19%)
        # 건강보험 7.19% + 국민연금 9.5% + 고용/산재 약 2% = 약 18.69%
        total_insurance = yearly_salary * 0.1869
        
        corp_total_cost = c_tax + s_tax + total_insurance
        tax_diff = personal_total_cost - corp_total_cost
    else:
        net_income, personal_total_cost, corp_total_cost, tax_diff = 0, 0, 0, 0

    st.subheader("📝 5. 노무 기준")
    min_wage = st.number_input("최저시급 (원)", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# HTML/JS 템플릿
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>제안서</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-print-color-adjust: exact !important; }}
        .tab-content {{ display: none; animation: fadeIn 0.4s ease-in-out; }}
        .tab-content.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .text-gradient {{ background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(to right, #2563eb, #059669); }}
        .check-list li::before {{ content: '✔'; color: #0ea5e9; margin-right: 8px; font-weight: bold; }}
        body.force-print-mode .tab-content {{ display: block !important; page-break-before: always; }}
        @media print {{ .sticky, .tab-btn, #print_btn {{ display: none !important; }} }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-12 pb-12 px-8 relative">
        <div class="max-w-5xl mx-auto relative z-10 flex justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-sm mb-2">MASTER CONSULTING PLAN</p>
                <h1 class="text-4xl font-bold mb-3 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 font-light">업종코드: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right">
                <button id="print_btn" onclick="executePrint()" class="mb-4 bg-blue-600 text-white text-sm font-bold py-2 px-4 rounded shadow">🖨️ 전체 내용 인쇄하기</button>
                <p class="text-slate-400 text-sm">제안일자: <span id="auto_date"></span></p>
                <p class="text-xl font-bold mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <div class="bg-white border-b sticky top-0 z-20 overflow-x-auto">
        <div class="max-w-5xl mx-auto px-6 flex space-x-8">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-4 font-bold text-blue-600 border-b-2 border-blue-600 whitespace-nowrap">핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">노무 및 비과세</button>
            {'<button onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">법인 전환 검토</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">인증/자금/지원금</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">마스터 스케쥴</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-6 py-8">
        <div id="tab_proposal" class="tab-content active">
            <div class="bg-white rounded-2xl shadow-sm border p-8">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">💡 {client_name} 전용 솔루션 구조</h2>
                <ul class="text-lg leading-relaxed space-y-2">{proposal_items}</ul>
            </div>
        </div>

        <div id="tab_labor" class="tab-content">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="bg-white rounded-2xl border p-6">
                    <h2 class="text-lg font-bold text-blue-800 mb-4 border-b pb-2">⏱️ 2026 최저임금 ({min_wage:,}원)</h2>
                    <div class="flex justify-between mb-4"><span>최저 시급</span><p class="text-xl font-bold">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-3 rounded-lg flex justify-between"><b>월 환산액</b><p class="text-xl font-bold text-blue-600">{monthly_wage:,}원</p></div>
                </div>
                <div class="bg-red-50 rounded-2xl border p-6 text-sm text-red-800">
                    <h2 class="text-lg font-bold mb-4 border-b border-red-200 pb-2">🚨 미작성 리스크</h2>
                    <p>미작성 시 <b>벌금 및 과태료 최대 500만 원</b> 부과 및 분쟁 시 사업주 절대 불리</p>
                </div>
            </div>
            <div class="bg-emerald-50 rounded-2xl border p-6">
                <h2 class="text-lg font-bold text-emerald-800 mb-4 border-b pb-2">💎 4대보험 비과세 설계</h2>
                <ul class="grid grid-cols-2 gap-4 text-sm font-medium">
                    <li class="bg-white p-2 rounded flex justify-between"><span>🍚 식대</span><span>월 20만</span></li>
                    <li class="bg-white p-2 rounded flex justify-between"><span>🚗 자가운전</span><span>월 20만</span></li>
                    <li class="bg-white p-2 rounded flex justify-between"><span>👶 보육수당</span><span>월 20만</span></li>
                    <li class="bg-white p-2 rounded flex justify-between"><span>🔬 연구보조</span><span>월 20만</span></li>
                </ul>
            </div>
        </div>

        <div id="tab_corp" class="tab-content">
            <div class="bg-white rounded-2xl border p-8">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">⚖️ 개인 vs 법인 종합 세무 비용 비교</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    <div class="space-y-4">
                        <div class="bg-red-50 p-4 rounded-xl border border-red-100">
                            <p class="text-sm font-bold text-red-800">개인 유지 시 (소득세+지역건보료)</p>
                            <p class="text-3xl font-bold text-red-600">{personal_total_cost:,.0f}만 원</p>
                        </div>
                        <div class="bg-blue-50 p-4 rounded-xl border border-blue-100">
                            <p class="text-sm font-bold text-blue-800">법인 전환 시 (법인세+근로소득세+직장4대보험)</p>
                            <p class="text-3xl font-bold text-blue-600">{corp_total_cost:,.0f}만 원</p>
                        </div>
                        <div class="bg-emerald-100 p-5 rounded-xl text-center">
                            <p class="text-lg font-bold">💡 실질 절세 기대액: <span class="text-2xl text-emerald-700">{tax_diff:,.0f}만 원</span></p>
                            <p class="text-xs text-slate-500 mt-2">※ 법인 전환 시 대표자 급여 월 {rep_salary:,}만 원 비용처리 가정</p>
                        </div>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-xl flex justify-center"><canvas id="taxChart" style="max-height:250px;"></canvas></div>
                </div>
            </div>
        </div>

        <div id="tab_fixed" class="tab-content">
            <div class="mb-10"><h2 class="text-xl font-bold mb-4 border-l-4 border-amber-500 pl-2">💰 고용지원금 시뮬레이션</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">{card_youth}{card_senior}{card_women}</div></div>
            <div class="mb-10"><h2 class="text-xl font-bold mb-4 border-l-4 border-blue-500 pl-2">🏆 기업 핵심 인증</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 border rounded-xl bg-white shadow-sm"><b>벤처기업 인증</b><p class="text-xs text-slate-500">법인세 50% 감면, 취등록세 75% 감면</p></div>
                <div class="p-4 border rounded-xl bg-white shadow-sm"><b>이노비즈 / 메인비즈</b><p class="text-xs text-slate-500">금융 우대 및 가점 부여</p></div>
            </div></div>
        </div>

        <div id="tab_schedule" class="tab-content">
            <div class="bg-white rounded-2xl border p-8"><h2 class="text-2xl font-bold mb-6 pb-4 border-b">📅 마스터 로드맵</h2>
            <div class="space-y-6">
                <div class="flex gap-4"><b>{m1:02d}월</b><p>인사/노무 기반 정비 및 4대보험 절세 설계</p></div>
                <div class="flex gap-4"><b>{m2:02d}월</b><p>핵심 인증(벤처/ISO) 및 법인 전환 타당성 최종 검토</p></div>
                <div class="flex gap-4"><b>{m3:02d}월</b><p>정책 자금(중진공/신보) 및 바우처 신청 접수</p></div>
            </div></div>
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

        function executePrint() {{
            document.body.classList.add('force-print-mode');
            setTimeout(() => {{ window.print(); setTimeout(() => document.body.classList.remove('force-print-mode'), 500); }}, 200);
        }}

        const ctx = document.getElementById('taxChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['개인사업자', '법인전환(통합)'],
                datasets: [{{
                    data: [{personal_total_cost}, {corp_total_cost}],
                    backgroundColor: ['#ef4444', '#3b82f6']
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
        }});
    </script>
</body>
</html>
"""

with col2:
    st.subheader("💻 제안서 미리보기")
    components.html(html_content, height=900, scrolling=True)
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 15px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px;">📥 맞춤 제안서 파일로 다운로드</a>', unsafe_allow_html=True)
