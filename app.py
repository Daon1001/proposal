import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="통합 경영제안서 생성기", layout="wide")

st.title("📊 통합 경영컨설팅 시스템")
st.write("좌측에 정보를 입력하세요. 모든 상세 데이터가 요약 없이 원문 그대로 제안서에 반영됩니다.")

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
    m1 = start_month
    m2 = (start_month % 12) + 1  # 인사/노무
    m3 = (start_month + 3) % 12 + 1  # 인증 (3개월 반영)
    m4 = (start_month + 4) % 12 + 1  # 재무/세무

    st.subheader("📝 3. 고용지원금 설정 (인원수)")
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

    def generate_subsidy_card(title, target, eligible, max_amount_str, scheduled_count, total_amount):
        if eligible:
            return f"""
            <div class="bg-amber-50 p-4 rounded-xl border border-amber-100 shadow-sm relative overflow-hidden print-break-inside-avoid mb-2">
                <div class="absolute right-0 top-0 bg-amber-200 text-amber-800 text-[10px] font-bold px-2 py-1 rounded-bl-lg">예정: {scheduled_count}명</div>
                <h3 class="font-bold text-amber-800 text-sm mb-1">{title}</h3>
                <p class="font-bold text-amber-900 text-xl">{total_amount:,}<span class="text-xs font-normal"> 만원</span></p>
                <p class="text-[10px] text-amber-700 mt-1">※ {max_amount_str}</p>
            </div>
            """
        else:
            return f"""
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden opacity-60 grayscale print-break-inside-avoid mb-2">
                <h3 class="font-bold text-slate-600 text-sm mb-1">{title}</h3>
                <p class="font-bold text-slate-400 text-xl">0<span class="text-xs font-normal"> 만원</span></p>
                <p class="text-[10px] text-red-500 mt-1">※ 요건 미달(5인 미만 등)</p>
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
    show_corp_tab = st.toggle("법인 전환 검토 탭 활성화", value=True)
    if show_corp_tab:
        net_income = st.number_input("당기순이익 (만원)", min_value=0, value=15000, step=1000)
        rep_salary = st.number_input("대표자 월 급여 (만원)", min_value=0, value=500, step=50)
        yearly_salary = rep_salary * 12
        p_tax = (net_income * 0.35) * 1.1 # 간이 계산
        p_health = net_income * 0.0709 
        personal_total_cost = p_tax + p_health
        corp_profit = max(0, net_income - yearly_salary)
        c_tax = (corp_profit * 0.09 if corp_profit <= 20000 else 1800 + (corp_profit-20000)*0.19) * 1.1
        s_tax = (yearly_salary * 0.15) * 1.1 # 간이 계산
        total_insurance = yearly_salary * 0.1869 
        corp_total_cost = c_tax + s_tax + total_insurance
        tax_diff = personal_total_cost - corp_total_cost
    else:
        personal_total_cost, corp_total_cost, tax_diff, rep_salary = 0, 0, 0, 0

    st.subheader("📝 5. 노무/비과세 기준")
    min_wage = st.number_input("2026년 최저시급 (원)", min_value=0, value=10030)
    monthly_wage = min_wage * 209

# ----------------------------------------------------------------------------------
# HTML 소스코드 (스케쥴 타이틀 한글화 및 인쇄 유지 로직)
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
        
        @media print {{
            @page {{ size: A4 landscape; margin: 10mm; }}
            body {{ background-color: #ffffff !important; }}
            .sticky, .tab-btn, #print_btn {{ display: none !important; }}
            .tab-content {{ display: none !important; }}
            .tab-content.print-active {{ 
                display: block !important; 
                opacity: 1 !important; 
                page-break-after: always !important; 
                padding-top: 10px !important;
            }}
            #tab_proposal {{ page-break-before: avoid !important; }}
            .print-break-inside-avoid {{ page-break-inside: avoid; break-inside: avoid; }}
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #e2e8f0 !important; }}
            #taxChart {{ display: none !important; }}
            #chartPrintImage {{ display: block !important; width: 100% !important; }}
        }}
        #chartPrintImage {{ display: none; }}
    </style>
</head>
<body class="antialiased">
    <header class="bg-slate-900 text-white pt-10 pb-10 px-8 relative">
        <div class="absolute inset-0 opacity-20" style="background: radial-gradient(circle at top right, #3b82f6, transparent);"></div>
        <div class="max-w-5xl mx-auto relative z-10 flex justify-between items-end">
            <div>
                <p class="text-amber-400 font-bold tracking-widest text-sm mb-1 uppercase">Master Consulting Plan</p>
                <h1 class="text-3xl font-bold mb-2 leading-tight">{client_name} <br><span class="text-gradient">맞춤형 경영제안서</span></h1>
                <p class="text-slate-400 text-xs">업종코드: {industry_code} / 상시근로자: {current_employees}명</p>
            </div>
            <div class="text-right flex flex-col items-end">
                <button id="print_btn" onclick="executePrint()" class="mb-4 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-2 px-4 rounded shadow transition-all cursor-pointer">🖨️ 가로형 전체 인쇄하기</button>
                <p class="text-slate-400 text-xs">제안일자: <span id="auto_date"></span></p>
                <p class="text-lg font-bold mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <div class="bg-white border-b sticky top-0 z-20 overflow-x-auto shadow-sm">
        <div class="max-w-5xl mx-auto px-6 flex space-x-6 text-sm">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-4 font-bold text-blue-600 border-b-2 border-blue-600 whitespace-nowrap">핵심 제안</button>
            <button onclick="switchTab('tab_labor', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">노무/비과세 상세</button>
            {'<button id="btn_corp" onclick="switchTab(\'tab_corp\', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">법인 전환 검토</button>' if show_corp_tab else ''}
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">인증/지원금 상세</button>
            <button onclick="switchTab('tab_fund', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">기관별 자금 상세</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-medium text-slate-500 whitespace-nowrap">마스터 스케쥴</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-6 py-8">
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white rounded-2xl shadow-sm border p-8">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">💡 {client_name} 전용 솔루션 구조</h2>
                <ul class="text-lg leading-relaxed space-y-2">{proposal_items}</ul>
            </div>
        </div>

        <div id="tab_labor" class="tab-content print-active">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 print-break-inside-avoid">
                <div class="bg-white rounded-2xl border p-6">
                    <h2 class="text-lg font-bold text-blue-800 mb-4 border-b pb-2">⏱️ 2026년 최저임금 및 법적 의무</h2>
                    <div class="flex justify-between mb-2"><span>2026년 최저 시급</span><p class="font-bold">{min_wage:,}원</p></div>
                    <div class="bg-blue-50 p-4 rounded-lg flex justify-between font-bold text-blue-700">
                        <span>월 환산액 (월 209시간 기준)</span>
                        <span>{monthly_wage:,}원</span>
                    </div>
                </div>
                <div class="bg-red-50 rounded-2xl border border-red-100 p-6 text-red-800 font-medium">
                    <h2 class="text-lg font-bold mb-2">🚨 근로계약서 미작성 리스크</h2>
                    <p class="text-xs">미작성 시 벌금/과태료 최대 500만원 및 분쟁 시 사업주 100% 불리</p>
                </div>
            </div>
            </div>

        <div id="tab_corp" class="tab-content {'print-active' if show_corp_tab else ''}">
            <div class="bg-white rounded-2xl border p-8">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">⚖️ 개인 vs 법인 통합 세무 비용 비교</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8 items-center">
                    <div class="space-y-4">
                        <div class="bg-red-50 p-4 rounded-xl border border-red-100">
                            <p class="text-xs font-bold text-red-800">개인 유지 시 비용</p>
                            <p class="text-3xl font-bold text-red-600">{personal_total_cost:,.0f}만 원</p>
                        </div>
                        <div class="bg-blue-50 p-4 rounded-xl border border-blue-100">
                            <p class="text-xs font-bold text-blue-800">법인 전환 시 비용</p>
                            <p class="text-3xl font-bold text-blue-600">{corp_total_cost:,.0f}만 원</p>
                        </div>
                    </div>
                    <div class="h-64 flex justify-center border rounded-xl bg-slate-50 p-2 relative">
                        <canvas id="taxChart"></canvas>
                        <img id="chartPrintImage" />
                    </div>
                </div>
            </div>
        </div>

        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="text-xl font-bold mb-4 border-l-4 border-amber-500 pl-2">💰 고용지원금 시뮬레이션 (총 {total_subsidy:,}만원 예상)</h2>
            <div class="grid grid-cols-3 gap-3 mb-10">{card_youth}{card_senior}{card_women}{card_continuous}{card_disabled}{card_parental}</div>
        </div>

        <div id="tab_fund" class="tab-content print-active">
            <h2 class="text-xl font-bold mb-6 border-l-4 border-emerald-500 pl-2">🏦 기관별 정책자금 및 지원사업</h2>
            <div class="grid grid-cols-2 gap-6">
                <div class="bg-emerald-50 p-6 rounded-2xl border border-emerald-200">
                    <h3 class="font-bold text-emerald-800 mb-2">🟢 중진공 및 바우처</h3>
                    <p class="text-xs text-emerald-700">융자 및 무상 지원사업 매칭</p>
                </div>
                <div class="bg-red-50 p-6 rounded-2xl border border-red-200">
                    <h3 class="font-bold text-red-800 mb-2">🔴 안전보건공단 지원</h3>
                    <p class="text-xs text-red-700">안전동행지원 최대 1억 무상 보조</p>
                </div>
            </div>
        </div>

        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-white rounded-2xl border p-8 print-break-inside-avoid">
                <h2 class="text-2xl font-bold mb-6 pb-4 border-b">📅 {my_company_name} - {client_name} 컨설팅 로드맵</h2>
                <div class="space-y-8">
                    <div class="flex gap-6 items-start"><div class="bg-slate-800 text-white px-3 py-1 rounded font-bold text-sm">{m1:02d}월</div><div><p class="font-bold">인사/노무 기반 정비 및 비과세 최적화</p></div></div>
                    <div class="flex gap-6 items-start"><div class="bg-blue-600 text-white px-3 py-1 rounded font-bold text-sm">{m1:02d}~{m3:02d}월</div><div><p class="font-bold">핵심 기업인증(벤처, ISO, 메인비즈) 확보</p></div></div>
                    <div class="flex gap-6 items-start"><div class="bg-emerald-600 text-white px-3 py-1 rounded font-bold text-sm">{m3:02d}~{m4:02d}월</div><div><p class="font-bold">법인전환 및 기관 자금 매칭 실행</p></div></div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const now = new Date();
        document.getElementById('auto_date').innerText = now.getFullYear() + '년 ' + (now.getMonth()+1) + '월 ' + now.getDate() + '일';

        let myChart;
        function renderTaxChart() {{
            const canvas = document.getElementById('taxChart');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            if (myChart) myChart.destroy();
            myChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['개인사업 유지', '법인 전환 통합'],
                    datasets: [{{
                        data: [{personal_total_cost}, {corp_total_cost}],
                        backgroundColor: ['#ef4444', '#3b82f6'],
                        borderRadius: 8
                    }}]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    animation: false,
                    plugins: {{ legend: {{ display: false }} }} 
                }}
            }});
        }}

        function switchTab(tabId, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('text-blue-600', 'border-blue-600', 'font-bold'));
            element.classList.add('text-blue-600', 'border-blue-600', 'font-bold');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            if (tabId === 'tab_corp') setTimeout(renderTaxChart, 100);
        }}

        function executePrint() {{
            const canvas = document.getElementById('taxChart');
            if (canvas) {{
                const img = document.getElementById('chartPrintImage');
                img.src = canvas.toDataURL('image/png');
            }}
            window.print();
        }}
        if (document.getElementById('taxChart')) setTimeout(renderTaxChart, 500);
    </script>
</body>
</html>
"""

with col2:
    st.subheader(f"💻 {client_name} 제안서 미리보기")
    components.html(html_content, height=1000, scrolling=True)
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client_name}_제안서.html" style="display: block; width: 100%; text-align: center; padding: 15px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px;">💾 제안서 파일 저장하기</a>', unsafe_allow_html=True)
