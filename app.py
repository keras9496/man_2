# app.py
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from korean_lunar_calendar import KoreanLunarCalendar

app = Flask(__name__)

# 천간(Cheongan)과 지지(Jiji) 정의
CHEONGAN = "갑을병정무기경신임계"
JIJI = "자축인묘진사오미신유술해"

# 띠(12지신) 정의
ZODIAC = "쥐 소 호랑이 토끼 용 뱀 말 양 원숭이 닭 개 돼지".split()

# 60갑자 순서
SIXTY_GAPJA = [CHEONGAN[i % 10] + JIJI[i % 12] for i in range(60)]

# 24절기 이름
SOLAR_TERMS_KO = [
    '입춘', '우수', '경칩', '춘분', '청명', '곡우',
    '입하', '소만', '망종', '하지', '소서', '대서',
    '입추', '처서', '백로', '추분', '한로', '상강',
    '입동', '소설', '대설', '동지', '소한', '대한'
]

calendar = KoreanLunarCalendar()

def get_solar_terms_for_year(year):
    """특정 연도의 24절기 날짜와 시간(datetime 객체)을 가져옵니다."""
    calendar.set_solar_date(year, 1, 1)
    solar_terms = {}
    for i in range(24):
        st_name = SOLAR_TERMS_KO[i]
        # 정확한 절기 시간을 얻기 위해 KoreanLunarCalendar 사용
        st_datetime_str = calendar.solar_term_24[i]
        st_datetime = datetime.strptime(f"{year}/{st_datetime_str}", "%Y/%m/%d %H:%M")
        solar_terms[st_name] = st_datetime
    return solar_terms

def get_year_pillar(year, month, day, hour, minute):
    """년주(Year Pillar) 계산"""
    current_date = datetime(year, month, day, hour, minute)
    
    # 해당 연도의 입춘 시간 가져오기
    solar_terms = get_solar_terms_for_year(year)
    ipchun_date = solar_terms['입춘']
    
    # 입춘 이전에 태어났으면 전년도를 기준으로 함
    calc_year = year if current_date >= ipchun_date else year - 1
    
    # 기준점: 1864년(갑자년)
    offset = (calc_year - 1864) % 60
    
    # 띠는 입춘 기준
    zodiac_year = year if current_date >= ipchun_date else year -1
    zodiac = ZODIAC[(zodiac_year - 4) % 12]

    return SIXTY_GAPJA[offset], zodiac

def get_month_pillar(year, month, day, hour, minute):
    """월주(Month Pillar) 계산"""
    current_date = datetime(year, month, day, hour, minute)
    
    # 년주 계산을 위해 입춘 기준 년도 다시 계산
    solar_terms_current_year = get_solar_terms_for_year(year)
    ipchun_date = solar_terms_current_year['입춘']
    calc_year = year if current_date >= ipchun_date else year - 1

    # 월주 계산을 위한 절기 리스트 (절기이름, 지지 인덱스)
    month_definitions = [
        ('입춘', 2), ('경칩', 3), ('청명', 4), ('입하', 5), ('망종', 6), ('소서', 7),
        ('입추', 8), ('백로', 9), ('한로', 10), ('입동', 11), ('대설', 0), ('소한', 1)
    ]
    
    # 해당 년도와 다음 년도의 절기 정보를 가져옴
    solar_terms = get_solar_terms_for_year(calc_year)
    solar_terms_next_year = get_solar_terms_for_year(calc_year + 1)
    
    month_jiji_index = -1

    for i in range(len(month_definitions)):
        term_name, jiji_idx = month_definitions[i]
        
        # 현재 절기 날짜
        if term_name in ['대설', '소한']: # 동지, 소한, 대한은 다음 해에 걸쳐 있을 수 있음
             term_date = solar_terms_next_year.get(term_name)
             if term_name == '대설' and term_date.month != 12 : # 12월이 아니면 전년도 대설
                 term_date = solar_terms.get(term_name)
        else:
            term_date = solar_terms[term_name]

        # 다음 절기 날짜
        next_term_name = month_definitions[(i + 1) % 12][0]
        if next_term_name in ['입춘', '경칩', '청명']:
            next_term_date = solar_terms_next_year.get(next_term_name)
        else:
            next_term_date = solar_terms.get(next_term_name, solar_terms_next_year.get(next_term_name))
            
        if term_date <= current_date < next_term_date:
            month_jiji_index = jiji_idx
            break
            
    # 예외 처리: 반복문에서 월주를 찾지 못한 경우 (연말연시 경계)
    if month_jiji_index == -1:
        if current_date >= solar_terms_next_year['소한'] or current_date < solar_terms_current_year['입춘']:
              month_jiji_index = 1 # 축월
        elif current_date >= solar_terms.get('대설', solar_terms_next_year.get('대설')):
              month_jiji_index = 0 # 자월


    # 년간(Heavenly Stem of the year)에 따른 월간(Heavenly Stem of the month) 계산
    year_pillar_gan, _ = get_year_pillar(year, month, day, hour, minute)
    year_cheongan = year_pillar_gan[0]
    year_cheongan_index = CHEONGAN.find(year_cheongan)
    
    # 년간에 따른 월간 조견표 (인월 기준)
    # 갑기년->병인월, 을경년->무인월, 병신년->경인월, 정임년->임인월, 무계년->갑인월
    month_cheongan_start_map = {'갑': '병', '을': '무', '병': '경', '정': '임', '무': '갑',
                                '기': '병', '경': '무', '신': '경', '임': '임', '계': '갑'}
    
    start_cheongan = month_cheongan_start_map[year_cheongan]
    start_cheongan_index = CHEONGAN.find(start_cheongan)
    
    # 인월(지지 인덱스 2)부터 시작하므로, 월 지지 인덱스에서 2를 빼서 월간을 계산
    month_cheongan_index = (start_cheongan_index + (month_jiji_index - 2)) % 10

    # 자월, 축월은 인월 이전이므로 보정
    if month_jiji_index < 2:
        month_cheongan_index = (start_cheongan_index + (month_jiji_index + 10)) % 10

    return CHEONGAN[month_cheongan_index] + JIJI[month_jiji_index]


def get_day_pillar(year, month, day, hour):
    """일주(Day Pillar) 계산 (야자시 적용)"""
    target_date = datetime(year, month, day)

    # 야자시(23:00-23:59)인 경우 다음 날로 계산
    if hour == 23:
        target_date += timedelta(days=1)

    # 기준일: 2000년 1월 1일 (경진일, 47번째 갑자)
    ref_date = datetime(2000, 1, 1)
    delta = target_date - ref_date
    days_diff = delta.days
    
    ref_gapja_index = 46  # 경진일은 47번째 이므로 인덱스는 46
    day_gapja_index = (ref_gapja_index + days_diff) % 60
    
    return SIXTY_GAPJA[day_gapja_index]

def get_hour_pillar(day_pillar_cheongan, hour):
    """시주(Hour Pillar) 계산"""
    # 시간대별 지지 매핑 (야자시/조자시 구분)
    if 23 <= hour or hour < 1: hour_jiji_index = 0  # 자시
    elif 1 <= hour < 3: hour_jiji_index = 1   # 축시
    elif 3 <= hour < 5: hour_jiji_index = 2   # 인시
    elif 5 <= hour < 7: hour_jiji_index = 3   # 묘시
    elif 7 <= hour < 9: hour_jiji_index = 4   # 진시
    elif 9 <= hour < 11: hour_jiji_index = 5  # 사시
    elif 11 <= hour < 13: hour_jiji_index = 6 # 오시
    elif 13 <= hour < 15: hour_jiji_index = 7 # 미시
    elif 15 <= hour < 17: hour_jiji_index = 8 # 신시
    elif 17 <= hour < 19: hour_jiji_index = 9 # 유시
    elif 19 <= hour < 21: hour_jiji_index = 10# 술시
    else: hour_jiji_index = 11 # 해시 (21-23시)
    
    hour_jiji = JIJI[hour_jiji_index]
    
    # 일간에 따른 시천간 조견표 (자시 기준)
    # 갑기일->갑자시, 을경일->병자시, 병신일->무자시, 정임일->경자시, 무계일->임자시
    day_cheongan_index = CHEONGAN.find(day_pillar_cheongan)
    
    if day_pillar_cheongan in "갑기": start_cheongan_index = CHEONGAN.find("갑")
    elif day_pillar_cheongan in "을경": start_cheongan_index = CHEONGAN.find("병")
    elif day_pillar_cheongan in "병신": start_cheongan_index = CHEONGAN.find("무")
    elif day_pillar_cheongan in "정임": start_cheongan_index = CHEONGAN.find("경")
    else: start_cheongan_index = CHEONGAN.find("임") # 무계일

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
            minute = birth_datetime.minute

            # 1. 년주 계산
            year_pillar, zodiac = get_year_pillar(year, month, day, hour, minute)
            
            # 2. 월주 계산
            month_pillar = get_month_pillar(year, month, day, hour, minute)

            # 3. 일주 계산
            day_pillar = get_day_pillar(year, month, day, hour)

            # 4. 시주 계산
            day_pillar_cheongan = day_pillar[0]
            hour_pillar = get_hour_pillar(day_pillar_cheongan, hour)
            
            result = {
                'birth_info': f"{year}년 {month}월 {day}일 {hour}시 {minute}분",
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
    app.run(host='0.0.0.0', port=5000, debug=True)