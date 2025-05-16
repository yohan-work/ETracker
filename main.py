import json
import os
from datetime import datetime, timedelta
import calendar

# 날씨 모듈 추가
try:
    import weather
    WEATHER_ENABLED = True
except ImportError:
    WEATHER_ENABLED = False
    print("날씨 모듈을 불러올 수 없습니다. requests 패키지를 설치해주세요: pip install requests")

DATA_FILE = "data/records.json"
EMOTION_MAP_FILE = "emotion_map.json"

def load_emotion_map():
    try:
        with open(EMOTION_MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"감정 맵을 불러오는 중 오류 발생: {e}")
        return {
            "기쁨": "#FFD700",
            "슬픔": "#1E90FF",
            "화남": "#DC143C",
            "불안": "#8A2BE2",
            "공허함": "#A9A9A9",
            "평온": "#98FB98",
            "지침": "#CD853F",
            "설렘": "#FF69B4"
        }

def load_records():
    os.makedirs("data", exist_ok=True)
    
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 파일이 비어있거나 존재하지 않으면 빈 배열 반환
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []
    except json.JSONDecodeError:
        print("기록 파일이 손상되었습니다. 새로운 파일을 생성합니다.")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_record(entry):
    records = load_records()
    
    # 같은 날짜 기록이 있으면 업데이트
    for i, record in enumerate(records):
        if record["date"] == entry["date"]:
            # 기존 날씨 정보 보존
            if "weather" in record and "weather" not in entry:
                entry["weather"] = record["weather"]
            records[i] = entry
            break
    else:
        # 없으면 추가
        records.append(entry)
    
    # 날짜 기준으로 정렬
    records.sort(key=lambda x: x["date"])
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def view_monthly_summary():
    records = load_records()
    if not records:
        print("\n기록이 없습니다.")
        return
    
    # 현재 년월 구하기
    now = datetime.now()
    year, month = now.year, now.month
    
    # 월 선택 옵션
    print("\n확인할 월을 선택하세요:")
    print(f"1. 이번 달 ({month}월)")
    print("2. 지난 달")
    print("3. 다른 달 입력")
    
    choice = input("\n선택 (기본: 1): ").strip() or "1"
    
    if choice == "2":
        # 지난 달
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    elif choice == "3":
        # 사용자 입력
        year = int(input("연도: "))
        month = int(input("월 (1-12): "))
    
    # 해당 월의 기록만 필터링
    month_prefix = f"{year}-{month:02d}-"
    monthly_records = [r for r in records if r["date"].startswith(month_prefix)]
    
    if not monthly_records:
        print(f"\n{year}년 {month}월 기록이 없습니다.")
        return
    
    # 월간 캘린더 표시
    cal = calendar.monthcalendar(year, month)
    emotion_map = load_emotion_map()
    
    print(f"\n{year}년 {month}월 감정 캘린더")
    print("월  화  수  목  금  토  일")
    
    # 감정 기록을 날짜별로 매핑
    date_to_emotion = {r["date"]: r["emotion"] for r in monthly_records}
    
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "    "
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in date_to_emotion:
                    emoji = get_emotion_emoji(date_to_emotion[date_str])
                    week_str += f"{day:2d}{emoji} "
                else:
                    week_str += f"{day:2d}   "
        print(week_str)

def get_emotion_emoji(emotion):
    emoji_map = {
        "기쁨": "😊",
        "슬픔": "😢",
        "화남": "😠",
        "불안": "😰",
        "공허함": "😶",
        "평온": "😌",
        "지침": "😩",
        "설렘": "😍"
    }
    return emoji_map.get(emotion, "❓")

def view_weekly_summary():
    records = load_records()
    if not records:
        print("\n기록이 없습니다.")
        return
    
    # 이번 주의 시작일(월요일)과 종료일(일요일) 계산
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # 이번 주 기록만 필터링
    weekly_records = []
    for r in records:
        record_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
        if start_of_week <= record_date <= end_of_week:
            weekly_records.append(r)
    
    if not weekly_records:
        print("\n이번 주 기록이 없습니다.")
        return
    
    print(f"\n이번 주 감정 요약 ({start_of_week} ~ {end_of_week})")
    
    # 요일별 표시
    days = ["월", "화", "수", "목", "금", "토", "일"]
    for i, day in enumerate(days):
        curr_date = start_of_week + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        
        # 해당 날짜 기록 찾기
        day_record = next((r for r in weekly_records if r["date"] == date_str), None)
        
        if day_record:
            emoji = get_emotion_emoji(day_record["emotion"])
            weather_info = ""
            if "weather" in day_record:
                weather_emoji = day_record["weather"].get("emoji", "")
                weather_temp = day_record["weather"].get("temp", "")
                if weather_emoji and weather_temp:
                    weather_info = f" | {weather_emoji} {weather_temp}°C"
            
            print(f"{day} ({curr_date.day}일): {emoji} {day_record['emotion']}{weather_info} - {day_record['note']}")
        else:
            print(f"{day} ({curr_date.day}일): 기록 없음")

def view_weather_info():
    if not WEATHER_ENABLED:
        print("\n날씨 기능을 사용할 수 없습니다.")
        print("requests 라이브러리를 설치해주세요: pip install requests")
        print("그리고 weather.py의 API_KEY를 설정해주세요.")
        return
    
    print("\n===== 날씨 정보 =====")
    
    # 도시 선택
    print("도시를 선택하세요:")
    print("1. 서울")
    print("2. 부산")
    print("3. 인천")
    print("4. 대구")
    print("5. 다른 도시 입력")
    
    choice = input("\n선택 (기본: 1): ").strip() or "1"
    
    city_map = {
        "1": "Seoul",
        "2": "Busan",
        "3": "Incheon",
        "4": "Daegu"
    }
    
    if choice in city_map:
        city = city_map[choice]
    else:
        city = input("도시 이름 (영문): ")
    
    country = input("국가 코드 (기본: kr): ").strip() or "kr"
    
    # 날씨 정보 가져오기
    weather_data = weather.get_weather(city, country)
    
    if weather_data:
        print(f"\n📍 {city.capitalize()}, {country.upper()} 날씨 정보:")
        print(f"날짜: {weather_data['date']}")
        print(f"날씨: {weather_data['emoji']} {weather_data['description']}")
        print(f"온도: {weather_data['temp']}°C (체감: {weather_data['feels_like']}°C)")
        print(f"습도: {weather_data['humidity']}%")
        
        # 현재 날씨를 오늘의 감정 기록에 저장할지 물어보기
        today = datetime.now().strftime("%Y-%m-%d")
        records = load_records()
        today_record = next((r for r in records if r["date"] == today), None)
        
        if today_record:
            save_choice = input("\n오늘의 감정 기록에 이 날씨 정보를 저장할까요? (y/n): ").strip().lower()
            if save_choice == "y":
                today_record["weather"] = weather_data
                save_record(today_record)
                print("✅ 날씨 정보가 오늘의 기록에 저장되었습니다.")
    else:
        print("날씨 정보를 가져오는데 실패했습니다.")

def run():
    while True:
        print("\n======= 마음기록기 =======")
        
        # 날씨 정보가 활성화된 경우 오늘의 날씨 표시
        if WEATHER_ENABLED:
            try:
                cached_weather = weather.get_weather(use_cache=True)
                if cached_weather:
                    weather_summary = weather.get_weather_summary(cached_weather)
                    print(f"오늘의 날씨: {weather_summary}")
            except Exception as e:
                pass  # 날씨 정보 표시 실패해도 무시
        
        print("1. 오늘의 감정 기록하기")
        print("2. 주간 감정 요약 보기")
        print("3. 월간 감정 요약 보기")
        print("4. 전체 감정 지도 보기")
        print("5. 날씨 정보 보기") # 새로운 메뉴 항목
        print("6. 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice == "1":
            record_today()
        elif choice == "2":
            view_weekly_summary()
        elif choice == "3":
            view_monthly_summary()
        elif choice == "4":
            try:
                import visualize
                records = load_records()
                if records:
                    visualize.draw_emotion_map(records)
                else:
                    print("\n기록이 없습니다.")
            except Exception as e:
                print(f"시각화 중 오류 발생: {e}")
        elif choice == "5":
            view_weather_info()
        elif choice == "6":
            print("\n프로그램을 종료합니다.")
            break
        else:
            print("\n잘못된 선택입니다. 다시 선택해주세요.")

def record_today():
    emotion_map = load_emotion_map()
    print("\n오늘 하루를 한 문장으로 표현해보세요.")
    note = input("👉 ")

    print("\n아래 감정 중 가장 가까운 걸 선택해주세요:")
    emotions = list(emotion_map.keys())
    for i, emotion in enumerate(emotions, start=1):
        emoji = get_emotion_emoji(emotion)
        print(f"{i}. {emotion} {emoji}")

    while True:
        try:
            choice = int(input("\n번호 입력: "))
            if 1 <= choice <= len(emotions):
                break
            print(f"1부터 {len(emotions)} 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
    
    emotion = emotions[choice - 1]
    color = emotion_map[emotion]

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "note": note,
        "emotion": emotion,
        "color": color
    }
    
    # 날씨 정보 추가 (날씨 모듈이 활성화된 경우)
    if WEATHER_ENABLED:
        try:
            weather_data = weather.get_weather(use_cache=True)
            if weather_data:
                entry["weather"] = weather_data
                print(f"📍 오늘의 날씨: {weather.get_weather_summary(weather_data)}")
        except Exception as e:
            print(f"날씨 정보를 가져오는 중 오류 발생: {e}")

    save_record(entry)
    print(f"\n✅ '{emotion}'으로 저장되었습니다. ({entry['date']})")

if __name__ == "__main__":
    run()
