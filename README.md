# ETracker

<img width="875" alt="image" src="https://github.com/user-attachments/assets/
cc6211c1-eaff-4c40-aab8-7c1b324af04b" />

## 기능

- 매일 감정과 한 줄 일기를 기록
- 감정에 색상을 할당하여 직관적인 시각화
- 일/주/월 단위로 감정의 흐름 시각화
- 감정 분포 통계 제공
- 날씨 정보 통합: 감정과 날씨의 연관성 분석

## 설치 및 실행

### 필수 라이브러리

```bash
pip install matplotlib numpy requests
```

### 실행 방법

```bash
python main.py
```

## 파일 구조

- `main.py`: 메인 프로그램 (감정 기록 및 조회)
- `visualize.py`: 감정 시각화 도구
- `weather.py`: 날씨 정보 처리 모듈
- `emotion_map.json`: 감정-색상 매핑 정보
- `data/records.json`: 기록 데이터 저장소
- `data/weather_cache.json`: 날씨 데이터 캐시

## 사용법

1. `main.py`를 실행하여 메인 메뉴에 접근
2. 원하는 기능 선택:
   - 오늘의 감정 기록하기
   - 주간/월간 감정 요약 보기
   - 전체 감정 지도 시각화
   - 날씨 정보 보기

### 날씨 기능 설정

`weather.py` 파일에서 OpenWeatherMap API 키를 설정해야 합니다:
1. [OpenWeatherMap](https://openweathermap.org/api)에서 무료 API 키 발급
2. `weather.py` 파일에서 `API_KEY = "YOUR_API_KEY"` 부분에 발급받은 키 입력

날씨 기능이 없어도 프로그램은 정상 작동합니다.

### 감정 시각화

```bash
python visualize.py
```

위 명령으로 시각화 메뉴에 직접 접근할 수 있습니다.

## 예시

### 감정 기록 예시
```
오늘 하루를 한 문장으로 표현해보세요.
👉 새로운 프로젝트를 시작해서 기분이 좋다

아래 감정 중 가장 가까운 걸 선택해주세요:
1. 기쁨 😊
2. 슬픔 😢
3. 화남 😠
4. 불안 😰
5. 공허함 😶
6. 평온 😌
7. 지침 😩
8. 설렘 😍

번호 입력: 1

📍 오늘의 날씨: ☀️ Clear sky 23.5°C
✅ '기쁨'으로 저장되었습니다. (2023-05-20)
```

### 날씨-감정 분석

감정 기록에 날씨 정보가 충분히 쌓이면, 날씨와 감정의 상관관계를 분석하는 기능을 사용할 수 있습니다. 이는 다음과 같은 인사이트를 제공합니다:

- 특정 날씨 조건에서 어떤 감정을 더 자주 느끼는지
- 온도 변화가 감정에 미치는 영향
- 계절별 감정 패턴

## 커스터마이징

### 감정-색상 매핑 수정
`emotion_map.json` 파일을 편집하여 감정과 색상을 원하는 대로 변경할 수 있습니다:

```json
{
  "행복": "#FFD700",
  "우울": "#1E90FF"
}
```

### 날씨 설정 변경
`weather.py` 파일에서 다음 설정을 변경할 수 있습니다:
- 기본 도시 변경: `get_weather(city="Seoul")`
- 온도 단위 변경: `"units": "imperial"`로 변경하면 화씨 단위 사용

## License
Yohan Choi
