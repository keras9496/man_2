# app.py
from flask import Flask, render_template, request
from korean_lunar_calendar import KoreanLunarCalendar
from datetime import datetime, timedelta

app = Flask(__name__)

# 천간(Cheongan)과 지지(Jiji) 정의
CHEONGAN = "갑을병정무기경신임계"
JIJI = "자축인묘진사오미신유술해"

# 띠(12지신) 정의
ZODIAC = "쥐 소 호랑이 토끼 용 뱀 말 양 원숭이 닭 개 돼지".split()

# 60갑자 순서
SIXTY_GAPJA = [CHEONGAN[i % 10] + JIJI[i % 12] for i in range(60)]

# 24절기 날짜 계산을 위한 간단한 테이블 (근사치)
SOLAR_TERMS_APPROX = {
    '소한': (1, 6), '대한': (1, 20),
    '입춘': (2, 4), '우수': (2, 19),
    '경칩': (3, 6), '춘분': (3, 21),
    '청명': (4, 5), '곡우': (4, 20),
    '입하': (5, 6), '소만': (5, 21),
    '망종': (6, 6), '하지': (6, 21),
    '소서': (7, 7), '대서': (7, 23),
    '입추': (8, 8), '처서': (8, 23),
    '백로': (9, 8), '추분': (9, 23),
    '한로': (10, 8), '상강': (10, 23),
    '입동': (11, 7), '소설': (11, 22),
    '대설': (12, 7), '동지': (12, 22)
}


def get_solar_term_date(year, term_name):
    """특정 년도의 절기 날짜를 계산 (근사치)"""
    month, day = SOLAR_TERMS_APPROX[term_name]
    return datetime(year, month, day)


def get_year_pillar(year):
    """년주(Year Pillar) 계산 - korean_lunar_calendar 라이브러리 사용"""
    try:
        calendar = KoreanLunarCalendar()
        # 해당 년도의 임의 날짜로 설정 (1월 15일)
        if calendar.setSolarDate(year, 1, 15):
            gapja_string = calendar.getGapJaString()
            # "갑자년 정축월 무인일" 형식에서 년주만 추출
            year_pillar = gapja_string.split()[0][:-1]  # "갑자년"에서 "년" 제거
            zodiac = ZODIAC[(year - 4) % 12]
            return year_pillar, zodiac
    except:
        pass
    
    # 라이브러리 실패시 기존 방식 사용
    offset = (year - 1864) % 60
    return SIXTY_GAPJA[offset], ZODIAC[(year - 4) % 12]


def get_month_pillar(year, month, day):
    """월주(Month Pillar) 계산 - korean_lunar_calendar 라이브러리 사용"""
    try:
        calendar = KoreanLunarCalendar()
        if calendar.setSolarDate(year, month, day):
            gapja_string = calendar.getGapJaString()
            # "갑자년 정축월 무인일" 형식에서 월주만 추출
            parts = gapja_string.split()
            if len(parts) >= 2:
                month_pillar = parts[1][:-1]  # "정축월"에서 "월" 제거
                return month_pillar
    except:
        pass
    
    # 라이브러리 실패시 기존 방식 사용
    current_date = datetime(year, month, day)
    ipcun_date = get_solar_term_date(year, '입춘')
    
    calc_year = year
    if current_date < ipcun_date:
        calc_year = year - 1
    
    month_terms = [
        ('입춘', 2), ('경칩', 3), ('청명', 4), ('입하', 5),
        ('망종', 6), ('소서', 7), ('입추', 8), ('백로', 9),
        ('한로', 10), ('입동', 11), ('대설', 0), ('소한', 1),
    ]
    
    month_jiji_index = 1
    for i, (term_name, jiji_idx) in enumerate(month_terms):
        term_date = get_solar_term_date(calc_year if i < 10 else calc_year + 1, term_name)
        if i < len(month_terms) - 1:
            next_term_date = get_solar_term_date(
                calc_year if i + 1 < 10 else calc_year + 1, 
                month_terms[i + 1][0]
            )
            if term_date <= current_date < next_term_date:
                month_jiji_index = jiji_idx
                break
        else:
            if current_date >= term_date or current_date < get_solar_term_date(calc_year, '입춘'):
                month_jiji_index = jiji_idx
    
    year_cheongan = get_year_pillar(calc_year)[0][0]
    year_cheongan_index = CHEONGAN.find(year_cheongan)
    
    month_cheongan_start_map = [2, 4, 6, 8, 0]
    start_cheongan_index = month_cheongan_start_map[year_cheongan_index % 5]
    
    month_cheongan_index = (start_cheongan_index + month_jiji_index - 2) % 10
    if month_jiji_index < 2:
        month_cheongan_index = (start_cheongan_index + month_jiji_index + 10) % 10
    
    return CHEONGAN[month_cheongan_index] + JIJI[month_jiji_index]


def get_day_pillar(year, month, day):
    """일주(Day Pillar) 계산 - korean_lunar_calendar 라이브러리 사용"""
    try:
        calendar = KoreanLunarCalendar()
        if calendar.setSolarDate(year, month, day):
            gapja_string = calendar.getGapJaString()
            # "갑자년 정축월 무인일" 형식에서 일주만 추출
            parts = gapja_string.split()
            if len(parts) >= 3:
                day_pillar = parts[2][:-1]  # "무인일"에서 "일" 제거
                return day_pillar
    except:
        pass
    
    # 라이브러리 실패시 기존 방식 사용
    ref_date = datetime(2000, 1, 1)
    target_date = datetime(year, month, day)
    delta = target_date - ref_date
    days_diff = delta.days
    ref_gapja_index = 46
    day_gapja_index = (ref_gapja_index + days_diff) % 60
    return SIXTY_GAPJA[day_gapja_index]


def get_hour_pillar(day_pillar_cheongan, hour):
    """시주(Hour Pillar) 계산"""
    # 시간대별 지지 매핑
    if hour == 23 or hour == 0:
        hour_jiji_index = 0  # 자시 (23:00-0:59)
    elif 1 <= hour <= 2:
        hour_jiji_index = 1  # 축시 (1:00-2:59)
    elif 3 <= hour <= 4:
        hour_jiji_index = 2  # 인시 (3:00-4:59)
    elif 5 <= hour <= 6:
        hour_jiji_index = 3  # 묘시 (5:00-6:59)
    elif 7 <= hour <= 8:
        hour_jiji_index = 4  # 진시 (7:00-8:59)
    elif 9 <= hour <= 10:
        hour_jiji_index = 5  # 사시 (9:00-10:59)
    elif 11 <= hour <= 12:
        hour_jiji_index = 6  # 오시 (11:00-12:59)
    elif 13 <= hour <= 14:
        hour_jiji_index = 7  # 미시 (13:00-14:59)
    elif 15 <= hour <= 16:
        hour_jiji_index = 8  # 신시 (15:00-16:59)
    elif 17 <= hour <= 18:
        hour_jiji_index = 9  # 유시 (17:00-18:59)
    elif 19 <= hour <= 20:
        hour_jiji_index = 10  # 술시 (19:00-20:59)
    else:  # 21-22시
        hour_jiji_index = 11  # 해시 (21:00-22:59)
    
    # 시간(지지)
    hour_jiji = JIJI[hour_jiji_index]
    
    # 시의 천간 계산 (일간 기준)
    day_cheongan_index = CHEONGAN.find(day_pillar_cheongan)
    
    # 일간에 따른 시천간 조견표
    hour_cheongan_start_map = [0, 2, 4, 6, 8]  # 갑, 병, 무, 경, 임
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
    app.run(host='0.0.0.0', port=5000, debug=True)