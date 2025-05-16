import requests
import json
import os
from datetime import datetime

# OpenWeatherMap API 설정
# 무료 API 키를 발급받아 사용해야 합니다: https://openweathermap.org/api
API_KEY = "YOUR_API_KEY" # 여기에 발급받은 API 키를 입력하세요
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_CACHE_FILE = "data/weather_cache.json"

# 날씨 아이콘 이모지 매핑
WEATHER_EMOJI = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌫️",
    "Sand": "🌫️",
    "Ash": "🌫️",
    "Squall": "💨",
    "Tornado": "🌪️"
}

def load_weather_cache():
    """날씨 캐시 파일 로드"""
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists(WEATHER_CACHE_FILE):
        try:
            with open(WEATHER_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    else:
        return {}

def save_weather_cache(cache):
    """날씨 캐시 저장"""
    with open(WEATHER_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_weather(city="Seoul", country_code="kr", use_cache=True):
    """특정 도시의 현재 날씨 정보 가져오기"""
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{city}_{country_code}_{today}"
    
    # 캐시에서 오늘 날씨 확인
    if use_cache:
        cache = load_weather_cache()
        if cache_key in cache:
            return cache[cache_key]
    
    # API 키가 설정되지 않은 경우
    if API_KEY == "YOUR_API_KEY":
        print("⚠️ OpenWeatherMap API 키가 설정되지 않았습니다.")
        return {
            "date": today,
            "weather": "Unknown",
            "description": "API 키 없음",
            "temp": 0,
            "feels_like": 0,
            "humidity": 0,
            "emoji": "❓"
        }
    
    # API에서 날씨 정보 가져오기
    params = {
        "q": f"{city},{country_code}",
        "appid": API_KEY,
        "units": "metric"  # 섭씨 온도
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if response.status_code == 200:
            weather = {
                "date": today,
                "weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temp": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "emoji": WEATHER_EMOJI.get(data["weather"][0]["main"], "🌡️")
            }
            
            # 결과 캐싱
            if use_cache:
                cache = load_weather_cache()
                cache[cache_key] = weather
                save_weather_cache(cache)
                
            return weather
        else:
            print(f"⚠️ 날씨 정보를 가져오는데 실패했습니다: {data.get('message', '알 수 없는 오류')}")
            return None
    except Exception as e:
        print(f"⚠️ 날씨 API 호출 중 오류 발생: {e}")
        return None

def get_weather_summary(weather_data):
    """날씨 정보를 요약해서 반환"""
    if not weather_data:
        return "날씨 정보 없음"
    
    emoji = weather_data.get("emoji", "")
    temp = weather_data.get("temp", 0)
    description = weather_data.get("description", "")
    
    return f"{emoji} {description.capitalize()} {temp}°C"

if __name__ == "__main__":
    # 테스트
    weather = get_weather()
    if weather:
        print(f"오늘의 날씨: {get_weather_summary(weather)}")
        print(f"온도: {weather['temp']}°C (체감: {weather['feels_like']}°C)")
        print(f"습도: {weather['humidity']}%") 