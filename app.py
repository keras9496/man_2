# main.py
from flask import Flask, render_template, request
from korean_lunar_calendar import KoreanLunarCalendar
from datetime import datetime, timedelta

app = Flask(__name__)

# 천간(Cheongan)과 지지(Jiji) 정의
CHEONGAN = "갑을병정무기경신임계"
JIJI = "자축인묘진사오미신유술해"

# 띠(12지신) 정의
ZODIAC = "쥐 소 호랑이 토끼 용 뱀 말 양 원숭이 닭 개 돼지".split()

# 60갑자 생성
GAPJA = [a + b for a in CHEONGAN for b in JIJI]
# 실제 60갑자 순서에 맞게 재정렬
SIXTY_GAPJA = [CHEONGAN[i % 10] + JIJI[i % 12] for i in range(60)]


def get_year_pillar(year):
    """년주(Year Pillar) 계산"""
    # 기준점: 1864년(갑자년)
    # 60갑자 순환을 이용
    offset = (year - 1864) % 60
    return SIXTY_GAPJA[offset], ZODIAC[(year - 4) % 12]

def get_month_pillar(year, month, day):
    """월주(Month Pillar) 계산"""
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)

    # 절기 기준 월 판별
    # 24절기 정보 가져오기
    solarterms = calendar.get_solar_terms()
    
    # 입춘(Ipcun)을 기준으로 년의 시작을 판단
    ipcun_date = datetime.strptime(solarterms[2], '%Y-%m-%d %H:%M:%S')
    
    current_date = datetime(year, month, day)

    # 입춘 이전에 태어났으면 전년도 띠를 따름
    if current_date < ipcun_date:
        year -= 1

    # 월지(Earthly Branch of the month)는 절기(Solar Term)에 따라 결정됨
    # 각 월의 시작 절기 (입춘, 경칩, 청명, ...)
    month_starts = [
        datetime.strptime(solarterms[2], '%Y-%m-%d %H:%M:%S'),  # 인(寅)월 - 입춘
        datetime.strptime(solarterms[4], '%Y-%m-%d %H:%M:%S'),  # 묘(卯)월 - 경칩
        datetime.strptime(solarterms[6], '%Y-%m-%d %H:%M:%S'),  # 진(辰)월 - 청명
        datetime.strptime(solarterms[8], '%Y-%m-%d %H:%M:%S'),  # 사(巳)월 - 입하
        datetime.strptime(solarterms[10], '%Y-%m-%d %H:%M:%S'), # 오(午)월 - 망종
        datetime.strptime(solarterms[12], '%Y-%m-%d %H:%M:%S'), # 미(未)월 - 소서
        datetime.strptime(solarterms[14], '%Y-%m-%d %H:%M:%S'), # 신(申)월 - 입추
        datetime.strptime(solarterms[16], '%Y-%m-%d %H:%M:%S'), # 유(酉)월 - 백로
        datetime.strptime(solarterms[18], '%Y-%m-%d %H:%M:%S'), # 술(戌)월 - 한로
        datetime.strptime(solarterms[20], '%Y-%m-%d %H:%M:%S'), # 해(亥)월 - 입동
        datetime.strptime(solarterms[22], '%Y-%m-%d %H:%M:%S'), # 자(子)월 - 대설
        datetime.strptime(solarterms[0], '%Y-%m-%d %H:%M:%S'),  # 축(丑)월 - 소한
    ]

    month_jiji_index = 0
    for i in range(len(month_starts) - 1):
        if month_starts[i] <= current_date < month_starts[i+1]:
            month_jiji_index = (i + 2) % 12 # 인월이 2부터 시작
            break
    else: # 마지막 절기(소한) 이후는 축월
        if current_date >= month_starts[-1] or current_date < month_starts[0]:
             month_jiji_index = 1 # 축월

    # 월간(Heavenly Stem of the month) 계산
    year_cheongan = get_year_pillar(year)[0][0]
    year_cheongan_index = CHEONGAN.find(year_cheongan)
    
    # 년간에 따른 월간 조견표 (갑기년->병인월, 을경년->무인월...)
    month_cheongan_start_map = [2, 4, 6, 8, 0] # 병, 무, 경, 임, 갑
    start_cheongan_index = month_cheongan_start_map[year_cheongan_index % 5]
    
    month_cheongan_index = (start_cheongan_index + month_jiji_index - 2) % 10
    if month_jiji_index < 2: # 자, 축월인 경우
        month_cheongan_index = (start_cheongan_index + month_jiji_index + 10) % 10


    return CHEONGAN[month_cheongan_index] + JIJI[month_jiji_index]


def get_day_pillar(year, month, day):
    """일주(Day Pillar) 계산"""
    # 기준점: 1년 1월 1일 (실제로는 그레고리력과 차이가 있어 보정이 필요)
    # 여기서는 datetime 객체를 사용하여 날짜 차이를 계산하는 간편한 방법을 사용
    # 기준일: 2000년 1월 1일 (경진일)
    ref_date = datetime(2000, 1, 1)
    target_date = datetime(year, month, day)
    
    delta = target_date - ref_date
    days_diff = delta.days
    
    # 2000년 1월 1일은 경진일(46번째 갑자)
    ref_gapja_index = 46 
    day_gapja_index = (ref_gapja_index + days_diff) % 60
    
    return SIXTY_GAPJA[day_gapja_index]


def get_hour_pillar(day_pillar_cheongan, hour):
    """시주(Hour Pillar) 계산"""
    # 자시(23:30 ~ 01:29) 처리
    # 야자시(전날)와 명자시(당일) 구분
    # 여기서는 간편하게 23시 이후를 다음날 자시로 처리
    if hour >= 23:
        # 날짜가 바뀌므로 일주 천간도 다음날로 계산해야 하나, 여기서는 단순화
        hour_jiji_index = 0 # 자시
    else:
        hour_jiji_index = (hour + 1) // 2 % 12

    # 시간(지지)
    hour_jiji = JIJI[hour_jiji_index]

    # 시의 천간 계산 (일간 기준)
    day_cheongan_index = CHEONGAN.find(day_pillar_cheongan)
    
    # 일간에 따른 시천간 조견표 (갑기일->갑자시, 을경일->병자시...)
    hour_cheongan_start_map = [0, 2, 4, 6, 8] # 갑, 병, 무, 경, 임
    start_cheongan_index = hour_cheongan_start_map[day_cheongan_index % 5]
    
    hour_cheongan_index = (start_cheongan_index + hour_jiji_index) % 10
    
    return CHEONGAN[hour_cheongan_index] + hour_jiji


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            birth_date_str = request.form['birth_date']
            birth_time_str = request.form['birth_time']
            
            birth_datetime = datetime.strptime(f"{birth_date_str} {birth_time_str}", '%Y-%m-%d %H:%M')
            
            year = birth_datetime.year
            month = birth_datetime.month
            day = birth_datetime.day
            hour = birth_datetime.hour

            # 1. 년주 계산
            year_pillar, zodiac = get_year_pillar(year)
            
            # 2. 월주 계산
            month_pillar = get_month_pillar(year, month, day)

            # 3. 일주 계산
            day_pillar = get_day_pillar(year, month, day)

            # 4. 시주 계산
            day_pillar_cheongan = day_pillar[0]
            hour_pillar = get_hour_pillar(day_pillar_cheongan, hour)
            
            result = {
                'birth_info': f"{year}년 {month}월 {day}일 {hour}시",
                'zodiac': zodiac,
                'year_pillar': year_pillar,
                'month_pillar': month_pillar,
                'day_pillar': day_pillar,
                'hour_pillar': hour_pillar,
            }

        except Exception as e:
            result = {'error': f"계산 중 오류가 발생했습니다: {e}"}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    # Render 배포를 위해 host='0.0.0.0' 사용
    app.run(host='0.0.0.0', port=5000, debug=True)
