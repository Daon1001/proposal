import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="J-ONE 컨설팅 시스템", layout="wide")

# 사이드바 입력창 (심플하게 정리)
with st.sidebar:
    st.header("📝 제안서 설정")
    my_company = st.text_input("제안사", "주식회사 제이원")
    client = st.text_input("고객사", "(주)영광산업기계")
    employees = st.number_input("상시근로자수", min_value=0, value=3)
    ind_code = st.text_input("업종코드", "[21812] 뿌리기업 해당")
    
    st.divider()
    
    start_m = st.number_input("시작 월", min_value=1, max_value=12, value=4)
    min_w = st.number_input("2026 최저시급", value=10030)
    
    st.divider()
    
    show_corp = st.toggle("법인 전환 탭 활성화", value=True)
    if show_corp:
        net_inc = st.number_input("당기순이익(만원)", value=15000)
        salary = st.number_input("대표월급(만원)", value=500)
    else:
        net_inc, salary = 0, 0

# 데이터 계산
m_wage = min_w * 209
m1, m2, m3, m4 = start_m, (start_m % 12)+1, (start_m+2)%12+1, (start_m+3)%12+1

# 지원금 카드 HTML 생성 함수 (깔끔한 리스트형)
def get_subsidy_html(title, target, eligible, max_amt, count):
    status_color = "blue" if eligible else "red"
    status_text = "신청 가능" if eligible else "신청 불가"
    bg_color = "bg-white" if eligible else "bg-gray-50"
    opacity = "opacity-100" if eligible else "opacity-50"
    
    return f"""
    <div class="{bg_color} {opacity} border border-slate-200 p-5 rounded-xl shadow-sm print-break-inside-avoid h-full relative">
        <span class="absolute top-3 right-3 text-[10px] font-bold text-{status_color}-600 bg-{status_color}-50 px-2 py-0.5 rounded border border-{status_color}-100">{status_text}</span>
        <p class="text-slate-500 text-xs font-bold mb-1">{target}</p>
        <h3 class="text-slate-800 font-bold text-base mb-3">{title}</h3>
        <div class="flex items-baseline gap-1">
            <span class="text-2xl font-black text-slate-900">{(count * int(max_amt.replace(',','').replace('만원','')) if eligible else 0):,}</span>
            <span class="text-sm font-bold text-slate-500">만원</span>
        </div>
        <p class="text-[11px] text-slate-400 mt-3 border-t pt-2">예정인원: {count}명 / 기준: {max_amt}</p>
    </div>
    """

# 탭별 내용 구성 (오류 방지 위해 사전 정의)
card_html = "".join([
    get_subsidy_html("청년일자리도약장려금", "만15~34세 청년", employees >= 5, "1,200만원", 1),
    get_subsidy_html("고령자계속고용장려금", "정년 도달자", True, "720만원", 0),
    get_subsidy_html("시니어인턴십", "만60세 이상", True, "240만원", 1),
    get_subsidy_html("장애인신규고용장려금", "경/중증 장애인", True, "720만원", 0),
    get_subsidy_html("새일여성인턴", "경력단절여성", True, "380만원", 1),
    get_subsidy_html("육아휴직대체인력", "대체인력 채용", True, "960만원", 0)
])

# 세금 계산 (단순화 시뮬레이션)
p_tax = (net_inc * 0.35) * 1.1 + (net_inc * 0.07)
c_tax = (max(0, net_inc - salary*12) * 0.1) * 1.1 + (salary*12*0.15) * 1.1 + (salary*12*0.18)
diff = p_tax - c_tax

# HTML 통합 템플릿
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+KR:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; animation: fadeIn 0.3s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        
        @media print {{
            @page {{ size: A4 landscape; margin: 12mm; }}
            body {{ background-color: #ffffff !important; }}
            .no-print {{ display: none !important; }}
            .tab-content {{ display: none !important; }}
            .tab-content.print-active {{ display: block !important; page-break-before: always !important; }}
            #tab_proposal.print-active {{ page-break-before: avoid !important; }}
            .shadow-sm {{ box-shadow: none !important; border: 1px solid #e2e8f0 !important; }}
        }}
    </style>
</head>
<body class="p-0 m-0">
    <header class="bg-slate-900 text-white px-10 py-8 flex justify-between items-center border-b-4 border-blue-600">
        <div>
            <h1 class="text-3xl font-black mb-1">{client} <span class="text-blue-400">컨설팅 제안서</span></h1>
            <p class="text-slate-400 text-sm font-medium">업종: {ind_code} | 상시근로자: {employees}명</p>
        </div>
        <div class="text-right">
            <button onclick="window.printMode()" class="no-print bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded text-sm mb-2 transition-all">🖨️ 가로 전체 인쇄하기</button>
            <p class="text-slate-500 text-xs">발행일: {datetime.now().strftime('%Y-%m-%d')} | 제안사: {my_company}</p>
        </div>
    </header>

    <nav class="no-print bg-white border-b sticky top-0 z-50 flex px-10 gap-8 shadow-sm">
        <button onclick="openTab(event, 'tab_proposal')" class="tab-btn py-4 text-sm font-bold text-blue-600 border-b-2 border-blue-600">핵심제안</button>
        <button onclick="openTab(event, 'tab_labor')" class="tab-btn py-4 text-sm font-bold text-slate-500 border-b-2 border-transparent">노무/비과세</button>
        {'<button onclick="openTab(event, \'tab_corp\')" class="tab-btn py-4 text-sm font-bold text-slate-500 border-b-2 border-transparent">법인전환</button>' if show_corp else ''}
        <button onclick="openTab(event, 'tab_fixed')" class="tab-btn py-4 text-sm font-bold text-slate-500 border-b-2 border-transparent">인증/지원금</button>
        <button onclick="openTab(event, 'tab_fund')" class="tab-btn py-4 text-sm font-bold text-slate-500 border-b-2 border-transparent">정책자금</button>
        <button onclick="openTab(event, 'tab_schedule')" class="tab-btn py-4 text-sm font-bold text-slate-500 border-b-2 border-transparent">스케쥴</button>
    </nav>

    <main class="max-w-7xl mx-auto p-10">
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white border border-slate-200 rounded-2xl p-10 shadow-sm">
                <h2 class="text-xl font-black text-slate-800 mb-8 flex items-center gap-2">
                    <span class="w-1.5 h-6 bg-blue-600 rounded-full"></span> {client} 경영 핵심 전략
                </h2>
                <ul class="space-y-6">
                    {"".join([f"<li class='flex items-start gap-4 text-lg text-slate-700'><span class='text-blue-500 mt-1'>●</span>{line}</li>" for line in proposal_input.split('\\n') if line.strip()])}
                </ul>
            </div>
        </div>

        <div id="tab_labor" class="tab-content print-active">
            <div class="grid grid-cols-2 gap-8 mb-8">
                <div class="bg-white border border-blue-200 rounded-2xl p-8 shadow-sm print-break-inside-avoid">
                    <h3 class="text-blue-700 font-bold text-lg mb-6 border-b pb-3">⏱️ 2026년 최저임금 기준</h3>
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-slate-500 font-bold text-sm">2026 최저시급</span>
                        <span class="text-3xl font-black text-slate-900">{min_w:,}원</span>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-xl flex justify-between items-center">
                        <span class="text-blue-800 font-bold text-sm">월 환산액 (209시간)</span>
                        <span class="text-3xl font-black text-blue-600">{m_wage:,}원</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-6 leading-relaxed">※ 최저임금법 위반 시 3년 이하 징역 또는 2천만원 이하 벌금 부과 대상입니다.</p>
                </div>
                <div class="bg-slate-900 text-white rounded-2xl p-8 shadow-sm print-break-inside-avoid">
                    <h3 class="text-amber-400 font-bold text-lg mb-6 border-b border-slate-700 pb-3">🚨 근로계약서 미작성 리스크</h3>
                    <ul class="space-y-4 text-sm font-medium">
                        <li class="flex items-start gap-3"><span class="text-amber-500">✔</span> 정규직 미작성 시: 벌금 최대 500만원 (형사처벌 대상)</li>
                        <li class="flex items-start gap-3"><span class="text-amber-500">✔</span> 기간제/단시간 미작성 시: 과태료 500만원 즉시 부과</li>
                        <li class="flex items-start gap-3"><span class="text-amber-500">✔</span> 노동 분쟁 시 계약서가 없으면 사업주가 100% 불리</li>
                    </ul>
                </div>
            </div>
            
            <div class="bg-white border border-slate-200 rounded-2xl p-8 mb-8 shadow-sm print-break-inside-avoid">
                <h3 class="text-slate-800 font-bold text-lg mb-6">🏢 상시근로자 5인 기준 노무관리 차이표</h3>
                <table class="w-full text-sm text-left border-collapse">
                    <thead class="bg-slate-50 text-slate-600 font-bold">
                        <tr><th class="p-4 border">구분</th><th class="p-4 border">5인 미만 사업장</th><th class="p-4 border text-blue-600">5인 이상 사업장 (중점관리)</th></tr>
                    </thead>
                    <tbody class="text-slate-700">
                        <tr><td class="p-4 border font-bold">가산수당</td><td class="p-4 border text-slate-400">의무 없음</td><td class="p-4 border font-bold text-red-600">통상임금 50% 가산 (1.5배)</td></tr>
                        <tr><td class="p-4 border font-bold">연차유급휴가</td><td class="p-4 border text-slate-400">의무 없음</td><td class="p-4 border font-bold text-red-600">법정 연차 발생 및 정산 의무</td></tr>
                        <tr><td class="p-4 border font-bold">부당해고구제</td><td class="p-4 border text-slate-400">적용 제외</td><td class="p-4 border font-bold text-red-600">노동위 구제신청 가능 (해고 제약)</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="bg-emerald-50 border border-emerald-100 rounded-2xl p-8 print-break-inside-avoid">
                <h3 class="text-emerald-800 font-bold text-lg mb-6">💎 합법적 4대보험 비과세 설계 (월 고정비 절감)</h3>
                <div class="grid grid-cols-4 gap-4">
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-100"><p class="text-xs text-slate-500 font-bold mb-1">식대</p><p class="text-lg font-black text-emerald-600">20만</p></div>
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-100"><p class="text-xs text-slate-500 font-bold mb-1">자가운전</p><p class="text-lg font-black text-emerald-600">20만</p></div>
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-100"><p class="text-xs text-slate-500 font-bold mb-1">보육수당</p><p class="text-lg font-black text-emerald-600">20만</p></div>
                    <div class="bg-white p-4 rounded-xl shadow-sm text-center border border-emerald-100"><p class="text-xs text-slate-500 font-bold mb-1">연구보조</p><p class="text-lg font-black text-emerald-600">20만</p></div>
                </div>
            </div>
        </div>

        <div id="tab_corp" class="tab-content {'print-active' if show_corp else ''}">
            <div class="bg-white border border-slate-200 rounded-2xl p-10 shadow-sm">
                <h2 class="text-xl font-black text-slate-800 mb-10 pb-4 border-b">⚖️ 개인 vs 법인 통합 세무 분석</h2>
                <div class="grid grid-cols-2 gap-12 items-center">
                    <div class="space-y-6">
                        <div class="bg-red-50 p-6 rounded-2xl border border-red-100">
                            <p class="text-xs font-bold text-red-800 mb-1">개인 유지 비용 (소득세+건보료)</p>
                            <p class="text-4xl font-black text-red-600">{p_total:,.0f}만원</p>
                        </div>
                        <div class="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                            <p class="text-xs font-bold text-blue-800 mb-1">법인 전환 비용 (법인세+근로세+직장보험)</p>
                            <p class="text-4xl font-black text-blue-600">{c_total:,.0f}만원</p>
                        </div>
                        <div class="bg-emerald-100 p-8 rounded-2xl text-center border border-emerald-200">
                            <p class="text-3xl font-black text-emerald-900">💡 연간 약 {max(0, diff):,.0f}만원 절세</p>
                            <p class="text-[11px] text-emerald-700 mt-2">※ 월 급여 {salary}만원 근로자 전환 시뮬레이션</p>
                        </div>
                    </div>
                    <div class="h-64"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="text-xl font-black mb-6 flex items-center gap-2">💰 고용지원금 시뮬레이션</h2>
            <div class="grid grid-cols-3 gap-5 mb-12">
                {card_html}
            </div>
            <h2 class="text-xl font-black mb-6 flex items-center gap-2">🏆 핵심 기업인증 상세 혜택</h2>
            <div class="grid grid-cols-3 gap-5">
                <div class="bg-white border p-6 rounded-xl shadow-sm"><h4 class="font-bold mb-2">여성기업인증</h4><p class="text-xs text-slate-500 leading-relaxed">수의계약 5천만원 확대, 입찰 가점, 정책자금 우선 지원</p></div>
                <div class="bg-white border p-6 rounded-xl shadow-sm"><h4 class="font-bold mb-2">직산 / 공장등록</h4><p class="text-xs text-slate-500 leading-relaxed">조달청 나라장터 참여 필수 요건, 제조업 각종 세제 감면</p></div>
                <div class="bg-white border p-6 rounded-xl shadow-sm"><h4 class="font-bold mb-2">메인 / 이노비즈</h4><p class="text-xs text-slate-500 leading-relaxed">정부 R&D 가점, 기보/신보 보증 우대, 정기 세무조사 유예</p></div>
                <div class="bg-white border p-6 rounded-xl shadow-sm"><h4 class="font-bold mb-2">ISO 9001/45001</h4><p class="text-xs text-slate-500 leading-relaxed">글로벌 표준 품질/안전 경영 구축, 중대재해법 대응 증빙</p></div>
                <div class="bg-white border p-6 rounded-xl shadow-sm"><h4 class="font-bold mb-2">특허 (권리 확보)</h4><p class="text-xs text-slate-500 leading-relaxed">독점 기술권 확보, 기술등급 상향(비용 400~1,000만원)</p></div>
                <div class="bg-white border p-6 rounded-xl shadow-sm"><h4 class="font-bold mb-2">기업부설연구소</h4><p class="text-xs text-slate-500 leading-relaxed">연구원 급여 25% 법인세 공제, 연구원 인당 월 20만 비과세</p></div>
            </div>
        </div>

        <div id="tab_fund" class="tab-content print-active">
            <h2 class="text-xl font-black mb-8">🏦 기관별 정책자금 및 지원사업 상세</h2>
            <div class="grid grid-cols-2 gap-8">
                <div class="bg-white border-l-8 border-emerald-500 p-8 rounded-2xl shadow-sm print-break-inside-avoid">
                    <h3 class="font-black text-emerald-800 text-lg mb-4">🟢 1. 중진공 및 혁신바우처</h3>
                    <ul class="text-sm space-y-3 text-slate-600 font-medium leading-relaxed">
                        <li>• <b>[융자]</b> 고정금리 연 2.5~3.5% 수준, 시설 최대 60억/운전 5억</li>
                        <li>• <b>[바우처]</b> 최대 5,000만원 무상 지원 (컨설팅, 시제품, 마케팅)</li>
                        <li>• <b>[수출]</b> 해외 마케팅 및 판로 지원 최대 1억원 (90% 지원)</li>
                    </ul>
                </div>
                <div class="bg-white border-l-8 border-blue-500 p-8 rounded-2xl shadow-sm print-break-inside-avoid">
                    <h3 class="font-black text-blue-800 text-lg mb-4">🔵 2. 보증기관 및 금융권</h3>
                    <ul class="text-sm space-y-3 text-slate-600 font-medium leading-relaxed">
                        <li>• <b>[신보/기보]</b> 담보 부족 시 기술/신용 기반 보증서 발급 (금리 4~5%)</li>
                        <li>• <b>[시중은행]</b> 정책 연계 시 금리 우대 및 한도 최적화 매칭</li>
                    </ul>
                </div>
                <div class="bg-white border-l-8 border-red-500 p-8 rounded-2xl shadow-sm print-break-inside-avoid">
                    <h3 class="font-black text-red-800 text-lg mb-4">🔴 3. 안전보건공단 지원사업</h3>
                    <ul class="text-sm space-y-3 text-slate-600 font-medium leading-relaxed">
                        <li>• <b>[안전동행]</b> 설비 교체 무상 보조금 최대 1억 (50% 매칭)</li>
                        <li>• <b>[산재융자]</b> <b>연 1.5% 고정금리</b> 초저리 지원 (최대 10억)</li>
                    </ul>
                </div>
                <div class="bg-white border-l-8 border-purple-500 p-8 rounded-2xl shadow-sm print-break-inside-avoid">
                    <h3 class="font-black text-purple-800 text-lg mb-4">🟣 4. 지자체 정책자금 (이차보전)</h3>
                    <ul class="text-sm space-y-3 text-slate-600 font-medium leading-relaxed">
                        <li>• <b>[경기도/시 자금]</b> 은행 금리 중 1~3%를 지자체가 대신 납부</li>
                        <li>• <b>[관내자금]</b> 시 전용 저리 융자 (조기 소진 시까지 선착순)</li>
                    </ul>
                </div>
            </div>
        </div>

        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-slate-900 text-white rounded-[40px] p-12 shadow-2xl">
                <h2 class="text-amber-400 font-black mb-10 pb-4 border-b border-slate-700">📅 컨설팅 마스터 로드맵</h2>
                <div class="space-y-12">
                    <div class="flex gap-10 items-start">
                        <div class="text-4xl font-black text-slate-500">{m1:02d}월</div>
                        <div><p class="text-xl font-bold mb-2">인사/노무 기반 정비</p><p class="text-slate-400 text-base font-medium">근로계약서 개편 및 4대보험 비과세 즉각 설계</p></div>
                    </div>
                    <div class="flex gap-10 items-start">
                        <div class="text-4xl font-black text-blue-500">{m1:02d}~{m3:02d}월</div>
                        <div><p class="text-xl font-bold mb-2">기업인증 집중 확보</p><p class="text-slate-400 text-base font-medium">메인/이노비즈, ISO, 특허 등 가점 필수 인증 완료</p></div>
                    </div>
                    <div class="flex gap-10 items-start">
                        <div class="text-4xl font-black text-emerald-500">{m3:02d}~{m4:02d}월</div>
                        <div><p class="text-xl font-bold mb-2">법인전환 및 자금 유치</p><p class="text-slate-400 text-base font-medium">세액 감면 적용 및 정책자금 매칭 완료</p></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) tabcontent[i].classList.remove("active");
            tablinks = document.getElementsByClassName("tab-btn");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].classList.remove("text-blue-600", "border-blue-600");
                tablinks[i].classList.add("text-slate-500", "border-transparent");
            }}
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("text-blue-600", "border-blue-600");
            evt.currentTarget.classList.remove("text-slate-500", "border-transparent");
        }}

        window.printMode = function() {{
            document.body.classList.add('force-print-mode');
            window.print();
            setTimeout(() => document.body.classList.remove('force-print-mode'), 500);
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
                    borderRadius: 8
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});
        ''' if show_corp else ""}
    </script>
</body>
</html>
"""

# Streamlit 출력
with col2:
    components.html(html_template, height=1000, scrolling=True)
    b64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client}_제안서.html" style="display: block; width: 100%; text-align: center; padding: 15px 0; background-color: #0F172A; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px;">💾 맞춤 제안서 파일 저장하기</a>', unsafe_allow_html=True)
