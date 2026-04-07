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
    
    # 제안 일자 (기본값은 오늘 날짜로 세팅하되 자유롭게 수정 가능)
    today_str = datetime.now().strftime('%Y년 %m월 %d일')
    proposal_date = st.text_input("제안 일자", today_str)

    st.subheader("📝 2. 맞춤 컨설팅 정보")
    
    # 업종 코드
    industry_code = st.text_input("업종 코드 및 상태 (예: [21812] 뿌리기업 해당)", "[21812] 뿌리기업 해당")
    
    # 제안 내용 (여러 줄 입력)
    proposal_input = st.text_area(
        "핵심 컨설팅 제안 내용 (줄바꿈으로 구분)", 
        "연구개발비 산입 (경상연구개발비, 개발비 : 매출액 5%)\n뿌리기업 → 소부장인증 → 벤처인증 기업으로 빌드업\n경영혁신형(메인비즈) 및 가족친화인증기업 획득\n수출바우처 및 혁신성장바우처를 통한 무상 특허 확보\n5인 이상 사업장에 따른 행정/노무 정비 및 지원금 수령"
    )
    # 입력받은 텍스트를 HTML 리스트(<li>) 형태로 변환
    proposal_items = "".join([f"<li class='mb-2 flex items-start'><span class='text-blue-500 mr-2'>✔</span><span class='break-keep'>{line.strip()}</span></li>" for line in proposal_input.split('\n') if line.strip()])
    
    # 스케쥴표 시작 월 설정
    start_month = st.number_input("스케쥴 시작 월 (숫자만 입력)", min_value=1, max_value=12, value=4)
    
    # 스케쥴 달 계산 (12월이 넘어가면 1월로 순환)
    m1 = start_month
    m2 = (start_month % 12) + 1
    m3 = (start_month + 1) % 12 + 1
    m4 = (start_month + 2) % 12 + 1

    st.info("💡 지원금, 인증 혜택, 자금 종류(기관별 금리)는 템플릿 내부에 고정(Fix)되어 자동으로 출력됩니다.")

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
                <p class="text-slate-400 font-light">업종코드: {industry_code}</p>
            </div>
            <div class="mt-4 md:mt-0 text-right">
                <p class="text-slate-400 text-sm">제안일자: {proposal_date}</p>
                <p class="text-xl font-bold mt-1">{my_company_name}</p>
            </div>
        </div>
    </header>

    <!-- Navigation -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div class="max-w-5xl mx-auto px-6 flex space-x-8">
            <button onclick="switchTab('tab_proposal', this)" class="tab-btn py-4 font-bold text-blue-600 border-b-2 border-blue-600">핵심 제안 내용</button>
            <button onclick="switchTab('tab_fixed', this)" class="tab-btn py-4 font-medium text-slate-500 border-b-2 border-transparent">인증/자금/지원금 (고정)</button>
            <button onclick="switchTab('tab_schedule', this)" class="tab-btn py-4 font-medium text-slate-500 border-b-2 border-transparent">마스터 스케쥴</button>
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

        <!-- [고정] TAB 2: 인증 / 자금 / 노무지원금 -->
        <div id="tab_fixed" class="tab-content">
            
            <!-- 1. 고정 지원금 항목 -->
            <div class="mb-10">
                <h2 class="text-xl font-bold text-slate-800 mb-4 pl-2 border-l-4 border-amber-500">💰 고용 지원금 혜택 (채용 인력 대상)</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-amber-50 p-5 rounded-xl border border-amber-100">
                        <h3 class="font-bold text-amber-800 mb-2">청년도약장려금</h3>
                        <p class="text-sm text-amber-700 mb-1">대상: 만 15~34세 청년</p>
                        <p class="font-bold text-amber-900 text-lg">최대 1,200만원 (2년간)</p>
                    </div>
                    <div class="bg-amber-50 p-5 rounded-xl border border-amber-100">
                        <h3 class="font-bold text-amber-800 mb-2">신중년적합직무</h3>
                        <p class="text-sm text-amber-700 mb-1">대상: 만 50세 이상</p>
                        <p class="font-bold text-amber-900 text-lg">최대 960만원 (1년간)</p>
                    </div>
                    <div class="bg-amber-50 p-5 rounded-xl border border-amber-100">
                        <h3 class="font-bold text-amber-800 mb-2">시니어 인턴쉽</h3>
                        <p class="text-sm text-amber-700 mb-1">대상: 만 60세 이상</p>
                        <p class="font-bold text-amber-900 text-lg">최대 520만원 (3년간)</p>
                    </div>
                </div>
            </div>

            <!-- 2. 고정 인증 항목 -->
            <div class="mb-10">
                <h2 class="text-xl font-bold text-slate-800 mb-4 pl-2 border-l-4 border-blue-500">🏆 기업 핵심 인증별 혜택</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="font-bold text-blue-700 mb-2">연구전담부서 / 연구소</h3>
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
                </div>
            </div>

            <!-- 3. 고정 자금 종류 및 금리 현황 -->
            <div>
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

        <!-- [가변] TAB 3: 마스터 스케쥴 -->
        <div id="tab_schedule" class="tab-content">
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
                        <p class="text-slate-600 text-sm mt-1">연구전담부서 설립 신청, 뿌리기업/소부장 사전 점검 및 신청, 여성/벤처기업 신청 준비</p>
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
                        <p class="text-slate-600 text-sm mt-1">완성된 인증 및 재무제표를 바탕으로 중진공 및 은행 자금 검토, 고용지원금 지속 관리</p>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <script>
        function switchTab(tabId, element) {{
            // 탭 버튼 스타일 변경
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('text-blue-600', 'border-blue-600', 'font-bold');
                btn.classList.add('text-slate-500', 'border-transparent', 'font-medium');
            }});
            element.classList.remove('text-slate-500', 'border-transparent', 'font-medium');
            element.classList.add('text-blue-600', 'border-blue-600', 'font-bold');

            // 콘텐츠 전환
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.getElementById(tabId).classList.add('active');
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
    download_link = f'<a href="data:text/html;base64,{b64}" download="{client_name}_경영제안서.html" style="display: block; width: 100%; text-align: center; padding: 15px 0; background-color: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px; font-size: 16px;">📥 [ {client_name} ] 맞춤 제안서 파일로 다운로드</a>'
    
    st.markdown(download_link, unsafe_allow_html=True)
