# Emotion MAP

감정 기록 및 시각화 용도
<img width="875" alt="image" src="https://github.com/user-attachments/assets/cc6211c1-eaff-4c40-aab8-7c1b324af04b" />


## 기능

- 매일 감정과 한 줄 일기를 기록
- 감정에 색상을 할당하여 직관적인 시각화
- 일/주/월 단위로 감정의 흐름 시각화
- 감정 분포 통계 제공

## 설치 및 실행

### 필수 라이브러리

```bash
pip install matplotlib numpy
```

### 실행 방법

```bash
python main.py
```

## 파일 구조

- `main.py`: 감정 기록 및 조회
- `visualize.py`: 감정 시각화 도구
- `emotion_map.json`: 감정-색상 매핑 정보
- `data/records.json`: 기록 데이터 저장소(기록된 data push)

## HTU

1. `main.py`를 실행하여 메인 메뉴에 접근
2. 원하는 기능 선택:
   - 오늘의 감정 기록하기
   - 주간/월간 감정 요약 보기
   - 전체 감정 지도 시각화

### 감정 시각화

```bash
python visualize.py
```

위 명령으로 시각화 메뉴에 직접 접근할 수 있습니다.

## 예시

### 감정 기록 예시
```
오늘 하루를 한 문장으로 표현해보세요.
👉 좋은 일이 생길 것만 같다.

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

✅ '기쁨'으로 저장되었습니다. (2023-05-20)
```

## Customize

### 감정-색상 매핑 수정
`emotion_map.json` 파일을 편집하여 감정과 색상을 원하는 대로 변경할 수 있습니다:

```json
{
  "행복": "#FFD700",
  "우울": "#1E90FF"
}
```

## License
Yohan Choi
