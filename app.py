import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="제이원 경영제안서 시스템", layout="wide")

# 2. 사이드바 입력창 (모든 원문 보존)
with st.sidebar:
    st.header("📝 제안서 정보 입력")
    my_company = st.text_input("제안사 이름", "주식회사 제이원")
    client = st.text_input("고객사 이름", "(주)영광산업기계")
    employees = st.number_input("현재 상시 근로자 수 (명)", min_value=0, value=3)
    ind_code = st.text_input("업종 코드 및 상태", "[21812] 뿌리기업 해당")
    
    st.divider()
    
    # 핵심 제안 내용 (요약 금지 원칙)
    raw_proposal = st.text_area("핵심 제안 내용", 
        value="연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장에 따른 행정/노무 정비 및 지원금 수령",
        height=200)
    
    start_m = st.number_input("스케쥴 시작 월", min_value=1, max_value=12, value=4)
    min_w = st.number_input("2026 최저시급 (원)", value=10030)
    
    st.divider()
    
    # 법인 탭 On/Off
    show_corp = st.toggle("법인 전환 검토 탭 활성화", value=True)
    if show_corp:
        net_inc = st.number_input("예상 당기순이익 (만원)", value=15000)
        salary = st.number_input("법인 시 대표 월 급여 (만원)", value=500)
    else:
        net_inc, salary = 0, 0

# 3. 데이터 계산부
m_wage = min_w * 209
m1, m2, m3, m4 = start_m, (start_m % 12)+1, (start_m+2)%12+1, (start_m+3)%12+1

# 세금 시뮬레이션 계산
p_tax_total = (net_inc * 0.35 * 1.1) + (net_inc * 0.07) # 종소세 + 지역건보
c_tax_total = (max(0, net_inc - salary*12) * 0.1 * 1.1) + (salary*12 * 0.15 * 1.1) + (salary*12 * 0.18) # 법인세 + 근로세 + 직장보험
tax_diff = p_tax_total - c_tax_total

# 지원금 카드 생성 함수
def make_card(title, target, eligible, max_val, count):
    status = "신청 가능" if eligible else "신청 불가"
    color = "blue" if eligible else "red"
    opacity = "100" if eligible else "50"
    amt = (count * int(max_val.replace(',','').replace('만원',''))) if eligible else 0
    return f"""
    <div class="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm opacity-{opacity} relative print-break-inside-avoid h-full">
        <span class="absolute top-4 right-4 text-[10px] font-bold text-{color}-600 bg-{color}-50 px-2 py-0.5 rounded border border-{color}-100">{status}</span>
        <p class="text-slate-400 text-xs font-bold mb-1">{target}</p>
        <h3 class="text-slate-800 font-bold text-lg mb-3">{title}</h3>
        <p class="text-3xl font-black text-slate-900">{amt:,}<span class="text-sm font-bold text-slate-500 ml-1">만원</span></p>
        <div class="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500 font-medium">인원: {count}명 / 기준금액: {max_val}</div>
    </div>
    """

cards_html = "".join([
    make_card("청년일자리도약장려금", "만15~34세 청년", employees >= 5, "1,200만원", 1),
    make_card("고령자계속고용장려금", "정년 도달자 재고용", True, "720만원", 0),
    make_card("시니어인턴십", "만60세 이상 신규", True, "240만원", 1),
    make_card("장애인신규고용장려금", "장애인 근로자", True, "720만원", 0),
    make_card("새일여성인턴", "경력단절여성 등", True, "380만원", 1),
    make_card("육아휴직대체인력", "대체인력 채용 시", True, "960만원", 0)
])

# 4. HTML/JS 통합 템플릿 (배치/간격 정돈 버전)
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; animation: fadeIn 0.4s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
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
<body>
    <header class="bg-slate-900 text-white px-12 py-10 flex justify-between items-end border-b-8 border-blue-600">
        <div>
            <h1 class="text-4xl font-black mb-2">{client} <span class="text-blue-400">맞춤 컨설팅 제안서</span></h1>
            <p class="text-slate-400 text-base font-medium">업종코드: {ind_code} | 상시근로자: {employees}명</p>
        </div>
        <div class="text-right">
            <button onclick="window.printMode()" class="no-print bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg mb-3 transition-all">🖨️ 가로 전체 인쇄하기</button>
            <p class="text-slate-500 text-xs">작성일: {datetime.now().strftime('%Y-%m-%d')} | 제안사: {my_company}</p>
        </div>
    </header>

    <nav class="no-print bg-white border-b sticky top-0 z-50 flex px-12 gap-10 shadow-sm">
        <button onclick="openTab(event, 'tab_proposal')" class="tab-btn py-5 text-base font-bold text-blue-600 border-b-4 border-blue-600">1. 핵심제안</button>
        <button onclick="openTab(event, 'tab_labor')" class="tab-btn py-5 text-base font-bold text-slate-500 border-b-4 border-transparent">2. 노무/비과세</button>
        {'<button onclick="openTab(event, \'tab_corp\')" class="tab-btn py-5 text-base font-bold text-slate-500 border-b-4 border-transparent">3. 법인전환</button>' if show_corp else ''}
        <button onclick="openTab(event, 'tab_fixed')" class="tab-btn py-5 text-base font-bold text-slate-500 border-b-4 border-transparent">4. 인증/지원금</button>
        <button onclick="openTab(event, 'tab_fund')" class="tab-btn py-5 text-base font-bold text-slate-500 border-b-4 border-transparent">5. 정책자금</button>
        <button onclick="openTab(event, 'tab_schedule')" class="tab-btn py-5 text-base font-bold text-slate-500 border-b-4 border-transparent">6. 스케쥴</button>
    </nav>

    <main class="max-w-[1400px] mx-auto p-12">
        <!-- 1. 핵심제안 -->
        <div id="tab_proposal" class="tab-content active print-active">
            <div class="bg-white border border-slate-200 rounded-[32px] p-16 shadow-sm">
                <h2 class="text-2xl font-black text-slate-800 mb-10 flex items-center gap-3">
                    <span class="w-2 h-8 bg-blue-600 rounded-full"></span> {client} 전용 경영 최적화 솔루션
                </h2>
                <ul class="space-y-8">
                    {"".join([f"<li class='flex items-start gap-5 text-xl text-slate-700 font-medium'><span class='text-blue-500 text-2xl'>●</span>{line}</li>" for line in raw_proposal.split('\\n') if line.strip()])}
                </ul>
            </div>
        </div>

        <!-- 2. 노무상세 -->
        <div id="tab_labor" class="tab-content print-active">
            <div class="grid grid-cols-2 gap-10 mb-10">
                <div class="bg-white border border-blue-100 rounded-[32px] p-10 shadow-sm print-break-inside-avoid">
                    <h3 class="text-blue-700 font-bold text-xl mb-8 border-b pb-4">⏱️ 2026년 최저임금 준수 의무</h3>
                    <div class="flex justify-between items-center mb-6">
                        <span class="text-slate-500 font-bold">2026 결정 최저시급</span>
                        <span class="text-4xl font-black text-slate-900">{min_w:,}원</span>
                    </div>
                    <div class="bg-blue-50 p-8 rounded-2xl flex justify-between items-center">
                        <span class="text-blue-800 font-bold text-lg">월 환산액 (209시간 기준)</span>
                        <span class="text-4xl font-black text-blue-600">{m_wage:,}원</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-6 leading-relaxed">※ 최저임금 미달 시 시정지시 없이 즉시 처벌(3년 이하 징역 또는 2천만원 이하 벌금) 대상입니다.</p>
                </div>
                <div class="bg-slate-900 text-white rounded-[32px] p-10 shadow-sm print-break-inside-avoid">
                    <h3 class="text-amber-400 font-bold text-xl mb-8 border-b border-slate-700 pb-4">🚨 근로계약서 미작성 시 리스크</h3>
                    <ul class="space-y-6 text-base font-medium">
                        <li class="flex items-start gap-4"><span class="bg-amber-500/20 text-amber-500 px-2 rounded">형사</span> 정규직 미작성: 벌금 최대 500만원 및 전과기록</li>
                        <li class="flex items-start gap-4"><span class="bg-amber-500/20 text-amber-500 px-2 rounded">행정</span> 기간제/단시간 미작성: 과태료 500만원 즉시 부과</li>
                        <li class="flex items-start gap-4"><span class="bg-amber-500/20 text-amber-500 px-2 rounded">입증</span> 분쟁(해고, 임금) 시 계약서 부재는 사업주 100% 패소 원인</li>
                    </ul>
                </div>
            </div>
            
            <div class="bg-white border border-slate-200 rounded-[32px] p-10 mb-10 shadow-sm print-break-inside-avoid">
                <h3 class="text-slate-800 font-bold text-xl mb-8">🏢 5인 미만 vs 5인 이상 노무관리 핵심 차이점</h3>
                <table class="w-full text-base text-left border-collapse">
                    <thead class="bg-slate-50 text-slate-600 font-bold">
                        <tr><th class="p-5 border border-slate-200">구분 법령</th><th class="p-5 border border-slate-200">5인 미만 사업장</th><th class="p-5 border border-slate-200 text-blue-600">5인 이상 사업장 (중점관리)</th></tr>
                    </thead>
                    <tbody class="text-slate-700 font-medium">
                        <tr><td class="p-5 border border-slate-200 font-bold bg-slate-50/50">가산수당</td><td class="p-5 border border-slate-200">지급 의무 없음 (1배)</td><td class="p-5 border border-slate-200 font-black text-red-600 text-xl">50% 가산 지급 (1.5배)</td></tr>
                        <tr><td class="p-5 border border-slate-200 font-bold bg-slate-50/50">연차유급휴가</td><td class="p-5 border border-slate-200">부여 의무 없음</td><td class="p-5 border border-slate-200 font-black text-red-600 text-xl">법정 연차 발생 및 정산 의무</td></tr>
                        <tr><td class="p-5 border border-slate-200 font-bold bg-slate-50/50">부당해고구제</td><td class="p-5 border border-slate-200">적용 제외 (해고 자유)</td><td class="p-5 border border-slate-200 font-black text-red-600 text-xl">노동위 구제신청 가능 (절차 엄격)</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="bg-emerald-50 border border-emerald-100 rounded-[32px] p-10 print-break-inside-avoid">
                <h3 class="text-emerald-800 font-bold text-xl mb-8">💎 합법적 4대보험 비과세 설계 (매월 고정비 즉시 절감)</h3>
                <div class="grid grid-cols-4 gap-6 text-center">
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-slate-500 font-bold mb-2">식대</p><p class="text-2xl font-black text-emerald-600">20만</p></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-slate-500 font-bold mb-2">자가운전</p><p class="text-2xl font-black text-emerald-600">20만</p></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-slate-500 font-bold mb-2">보육수당</p><p class="text-2xl font-black text-emerald-600">20만</p></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100"><p class="text-slate-500 font-bold mb-2">연구보조</p><p class="text-2xl font-black text-emerald-600">20만</p></div>
                </div>
                <p class="text-sm text-emerald-700 mt-8 text-center font-bold">※ 위 비과세 항목 세팅 시 사업주 4대보험료 약 10% 추가 절감 효과가 즉시 발생합니다.</p>
            </div>
        </div>

        <!-- 3. 법인전환 -->
        <div id="tab_corp" class="tab-content {'print-active' if show_corp else ''}">
            <div class="bg-white border border-slate-200 rounded-[32px] p-16 shadow-sm">
                <h2 class="text-2xl font-black text-slate-800 mb-12 border-b-4 border-indigo-500 pb-4 inline-block">⚖️ 개인 vs 법인 통합 세무 분석</h2>
                <div class="grid grid-cols-2 gap-16 items-center">
                    <div class="space-y-8">
                        <div class="bg-red-50 p-8 rounded-[24px] border border-red-100 shadow-inner">
                            <p class="text-sm font-bold text-red-800 mb-2">개인사업 유지 시 비용 (종소세+건보료)</p>
                            <p class="text-5xl font-black text-red-600">{p_total:,.0f} <span class="text-2xl">만원</span></p>
                        </div>
                        <div class="bg-blue-50 p-8 rounded-[24px] border border-blue-100 shadow-inner">
                            <p class="text-sm font-bold text-blue-800 mb-2">법인 전환 시 통합 비용 (법인세+근로세+직장보험)</p>
                            <p class="text-5xl font-black text-blue-600">{c_total:,.0f} <span class="text-2xl">만원</span></p>
                        </div>
                        <div class="bg-emerald-100 p-10 rounded-[24px] text-center border-2 border-emerald-200 shadow-lg">
                            <p class="text-3xl font-black text-emerald-900">💡 예상 절세액: <span class="text-6xl text-emerald-600">{max(0, diff):,.0f}만 원</span></p>
                        </div>
                    </div>
                    <div class="bg-slate-50 rounded-[24px] p-10 h-[450px] flex justify-center"><canvas id="taxChart"></canvas></div>
                </div>
            </div>
        </div>

        <!-- 4. 인증/지원금 -->
        <div id="tab_fixed" class="tab-content print-active">
            <h2 class="text-2xl font-black mb-10 flex items-center gap-3">💰 고용지원금 시뮬레이션</h2>
            <div class="grid grid-cols-3 gap-8 mb-16">
                {cards_html}
            </div>
            <h2 class="text-2xl font-black mb-10 flex items-center gap-3">🏆 핵심 기업인증 상세 혜택</h2>
            <div class="grid grid-cols-3 gap-8">
                <div class="bg-white border p-8 rounded-[24px] shadow-sm relative transition-all hover:bg-blue-50/30" onclick="this.classList.toggle('border-blue-500');this.classList.toggle('ring-4');this.classList.toggle('ring-blue-50')">
                    <h4 class="font-black text-lg mb-4 text-slate-800">여성기업인증</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-medium">• 수의계약 5천만원 한도 확대<br>• 공공입찰 가점 및 정책자금 우선 지원</p>
                </div>
                <div class="bg-white border p-8 rounded-[24px] shadow-sm relative transition-all hover:bg-blue-50/30" onclick="this.classList.toggle('border-blue-500');this.classList.toggle('ring-4');this.classList.toggle('ring-blue-50')">
                    <h4 class="font-black text-lg mb-4 text-slate-800">직접생산 / 공장등록</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-medium">• 조달청 나라장터 참여 필수 요건<br>• 제조업 각종 세제 감면 및 전기료 혜택</p>
                </div>
                <div class="bg-white border p-8 rounded-[24px] shadow-sm relative transition-all hover:bg-blue-50/30" onclick="this.classList.toggle('border-blue-500');this.classList.toggle('ring-4');this.classList.toggle('ring-blue-50')">
                    <h4 class="font-black text-lg mb-4 text-slate-800">메인 / 이노비즈</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-medium">• 기술/경영 혁신형 중소기업 국가공인<br>• 기보/신보 보증 우대 및 정책자금 금리 인하</p>
                </div>
                <div class="bg-white border p-8 rounded-[24px] shadow-sm relative transition-all hover:bg-blue-50/30" onclick="this.classList.toggle('border-blue-500');this.classList.toggle('ring-4');this.classList.toggle('ring-blue-50')">
                    <h4 class="font-black text-lg mb-4 text-slate-800">ISO 9001 / 45001</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-medium">• 글로벌 품질 및 안전보건 경영 표준 구축<br>• 중대재해처벌법 대응 필수 증빙 자료</p>
                </div>
                <div class="bg-white border p-8 rounded-[24px] shadow-sm relative transition-all hover:bg-blue-50/30" onclick="this.classList.toggle('border-blue-500');this.classList.toggle('ring-4');this.classList.toggle('ring-blue-50')">
                    <h4 class="font-black text-lg mb-4 text-slate-800">특허 확보 (원천기술)</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-medium">• 핵심 기술 보호 및 기술가치 상향<br>• 정책자금 한도 증액 및 무상 자금 유치 가점</p>
                </div>
                <div class="bg-white border p-8 rounded-[24px] shadow-sm relative transition-all hover:bg-blue-50/30" onclick="this.classList.toggle('border-blue-500');this.classList.toggle('ring-4');this.classList.toggle('ring-blue-50')">
                    <h4 class="font-black text-lg mb-4 text-slate-800">기업부설연구소</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-medium">• 연구인력 인건비 25% 법인세 공제<br>• 연구원 인당 월 20만 비과세 절세</p>
                </div>
            </div>
        </div>

        <!-- 5. 정책자금 -->
        <div id="tab_fund" class="tab-content print-active">
            <h2 class="text-2xl font-black mb-12 border-l-8 border-emerald-500 pl-6 text-emerald-800">🏦 기관별 정책자금 및 지원사업 상세 현황</h2>
            <div class="grid grid-cols-2 gap-12">
                <div class="bg-white border-t-8 border-emerald-500 p-10 rounded-[32px] shadow-lg print-break-inside-avoid h-full">
                    <h3 class="font-black text-emerald-800 text-xl mb-6">🟢 1. 중진공 및 혁신바우처</h3>
                    <ul class="text-base space-y-4 text-slate-600 font-bold leading-relaxed">
                        <li>• <b>[융자]</b> 고정금리 연 2.5~3.5% 수준, 시설 최대 60억/운전 5억</li>
                        <li>• <b>[혁신바우처]</b> 최대 5,000만원 무상 지원 (시제품, 마케팅, 컨설팅)</li>
                        <li>• <b>[수출바우처]</b> 해외 진출 비용 최대 1억원 (90% 국비 보조)</li>
                    </ul>
                </div>
                <div class="bg-white border-t-8 border-blue-500 p-10 rounded-[32px] shadow-lg print-break-inside-avoid h-full">
                    <h3 class="font-black text-blue-800 text-xl mb-6">🔵 2. 보증기관 (신보/기보) 및 금융권</h3>
                    <ul class="text-base space-y-4 text-slate-600 font-bold leading-relaxed">
                        <li>• <b>[보증서 대출]</b> 담보 부족 시 기술력으로 보증서 발급 (금리 4~5%)</li>
                        <li>• <b>[시중은행 연계]</b> 정책 연계 시 금리 우대 및 한도 최적화 매칭</li>
                    </ul>
                </div>
                <div class="bg-white border-t-8 border-red-500 p-10 rounded-[32px] shadow-lg print-break-inside-avoid h-full">
                    <h3 class="font-black text-red-800 text-xl mb-6">🔴 3. 안전보건공단 지원사업</h3>
                    <ul class="text-base space-y-4 text-slate-600 font-bold leading-relaxed">
                        <li>• <b>[안전동행]</b> 노후 설비 교체 무상 보조금 최대 1억 (50% 매칭)</li>
                        <li>• <b>[산재예방융자]</b> 안전 설비 도입 <b>연 1.5% 고정금리</b> 초저리 지원</li>
                    </ul>
                </div>
                <div class="bg-white border-t-8 border-purple-500 p-10 rounded-[32px] shadow-lg print-break-inside-avoid h-full">
                    <h3 class="font-black text-purple-800 text-xl mb-6">🟣 4. 지자체 정책자금 (도/시 자금)</h3>
                    <ul class="text-base space-y-4 text-slate-600 font-bold leading-relaxed">
                        <li>• <b>[이차보전]</b> 은행 대출 금리 중 1.0~3.0%를 지자체가 직접 대납</li>
                        <li>• <b>[시흥시 자금]</b> 관내 기업 전용 예산으로 저리 융자 (적기 신청 관리 필수)</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 6. 스케쥴 -->
        <div id="tab_schedule" class="tab-content print-active">
            <div class="bg-slate-900 text-white rounded-[40px] p-16 shadow-2xl">
                <h2 class="text-amber-400 font-black text-3xl mb-12 border-b border-slate-700 pb-6">📅 마스터 로드맵 스케쥴</h2>
                <div class="space-y-16">
                    <div class="flex gap-12 items-start">
                        <div class="text-5xl font-black text-slate-600">{m1:02d}월</div>
                        <div><p class="text-2xl font-black mb-3">인사/노무 기반 정비 및 비과세 최적화</p><p class="text-slate-400 text-xl font-bold">근로계약서 개편 및 4대보험 고정비 즉시 절감 설계 완료</p></div>
                    </div>
                    <div class="flex gap-12 items-start">
                        <div class="text-5xl font-black text-blue-500">{m1:02d}~{m3:02d}월</div>
                        <div><p class="text-2xl font-black mb-3">기업 핵심인증 집중 확보</p><p class="text-slate-400 text-xl font-bold">메인/이노비즈, ISO, 특허 등 정책 가점 필수 인증 프로세스 완료</p></div>
                    </div>
                    <div class="flex gap-12 items-start">
                        <div class="text-5xl font-black text-emerald-500">{m3:02d}~{m4:02d}월</div>
                        <div><p class="text-2xl font-black mb-3">법인전환 타당성 확정 및 정책자금 매칭</p><p class="text-slate-400 text-xl font-bold">절세 시뮬레이션 기반 법인전환 및 자금 유치를 위한 재무 가결산 조정</p></div>
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
                labels: ['개인사업 유지', '법인 전환 통합'],
                datasets: [{{
                    data: [{p_total_cost}, {c_tax_total}],
                    backgroundColor: ['#ef4444', '#3b82f6'],
                    borderRadius: 12
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});
        ''' if show_corp else ""}
    </script>
</body>
</html>
"""

# 5. Streamlit 출력 처리
with col2:
    components.html(html_template, height=1000, scrolling=True)
    b64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8')
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="{client}_제안서.html" style="display: block; width: 100%; text-align: center; padding: 18px 0; background-color: #0F172A; color: white; text-decoration: none; border-radius: 12px; font-weight: bold; margin-top: 10px; font-size: 16px;">💾 제안서 파일(HTML) 저장하기</a>', unsafe_allow_html=True)
