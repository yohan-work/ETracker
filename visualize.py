import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.patches as mpatches
import calendar
import numpy as np
import os

def load_records():
    data_file = "data/records.json"
    if not os.path.exists(data_file) or os.path.getsize(data_file) == 0:
        return []
    
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("기록 파일을 불러오는 중 오류가 발생했습니다.")
        return []

def load_emotion_map():
    map_file = "emotion_map.json"
    try:
        with open(map_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 기본 감정 맵 반환
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

def draw_emotion_map(records, period='all'):
    if not records:
        print("표시할 기록이 없습니다.")
        return
    
    filtered_records = records
    title_suffix = ""
    
    # 기간별 필터링
    if period == 'month':
        # 이번 달 필터링
        current_month = datetime.now().strftime("%Y-%m")
        filtered_records = [r for r in records if r["date"].startswith(current_month)]
        title_suffix = f" - {datetime.now().strftime('%Y년 %m월')}"
    elif period == 'week':
        # 이번 주 필터링
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        filtered_records = []
        for r in records:
            record_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
            if start_of_week <= record_date <= end_of_week:
                filtered_records.append(r)
        
        title_suffix = f" - {start_of_week} ~ {end_of_week}"
    
    if not filtered_records:
        print(f"선택한 기간({period})에 표시할 기록이 없습니다.")
        return
    
    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in filtered_records]
    colors = [r["color"] for r in filtered_records]
    emotions = [r["emotion"] for r in filtered_records]
    notes = [r["note"] for r in filtered_records]
    
    # 날씨 정보 추출
    weathers = []
    temps = []
    for r in filtered_records:
        if "weather" in r and r["weather"]:
            weathers.append(r["weather"].get("emoji", ""))
            temps.append(r["weather"].get("temp", ""))
        else:
            weathers.append("")
            temps.append("")

    # 정렬
    sorted_data = sorted(zip(dates, colors, emotions, notes, weathers, temps), key=lambda x: x[0])
    dates, colors, emotions, notes, weathers, temps = zip(*sorted_data)

    # 두 개의 서브플롯 생성 (감정 타임라인 + 온도 그래프)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(10, len(dates)*0.5), 5), 
                                  gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

    # 감정 타임라인 그리기 (위쪽 서브플롯)
    for i, (date, color, note, weather) in enumerate(zip(dates, colors, notes, weathers)):
        rect = plt.Rectangle((i, 0), 0.8, 1, color=color)
        ax1.add_patch(rect)
        
        # 날씨 이모지가 있으면 표시
        if weather:
            ax1.text(i+0.4, 1.1, weather, fontsize=12, ha='center')
        
        # 이벤트에 마우스 호버시 툴팁으로 노트 표시
        tooltip_text = f"{date.strftime('%Y-%m-%d')}\n{note}"
        if weather:
            tooltip_text += f"\n{weather} {temps[i]}°C"
            
        ax1.annotate(tooltip_text, 
                    (i+0.4, 0.5),
                    xytext=(15, 15),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8),
                    arrowprops=dict(arrowstyle="->"),
                    visible=False)
    
    # 마우스 호버 이벤트 처리
    def hover(event):
        for i, rect in enumerate(ax1.patches):
            contains, _ = rect.contains(event)
            annotations = ax1.texts[i:i+len(dates)]  # 해당 사각형과 연관된 주석
            if contains and annotations:
                for ann in annotations[i:i+1]:
                    if not isinstance(ann, plt.Text) or not hasattr(ann, 'get_visible'):
                        continue
                    ann.set_visible(True)
            elif annotations:
                for ann in annotations[i:i+1]:
                    if not isinstance(ann, plt.Text) or not hasattr(ann, 'get_visible'):
                        continue
                    ann.set_visible(False)
        fig.canvas.draw_idle()
    
    fig.canvas.mpl_connect("motion_notify_event", hover)

    # 온도 그래프 그리기 (아래쪽 서브플롯)
    if any(temps) and all(t != "" for t in temps):
        # 온도 데이터가 있으면 그래프 그리기
        temp_values = [float(t) for t in temps if t]
        if temp_values:
            x_values = [i+0.4 for i in range(len(dates)) if temps[i]]
            if x_values and temp_values:
                # 막대 그래프
                ax2.bar(x_values, temp_values, width=0.6, color='skyblue', alpha=0.7)
                
                # 온도 값 텍스트로 표시
                for x, temp in zip(x_values, temp_values):
                    ax2.text(x, temp+0.5, f"{temp}°C", ha='center', va='bottom', fontsize=8)
                
                ax2.set_ylabel('온도 (°C)')
                
                # Y축 범위 설정
                if temp_values:
                    min_temp = min(temp_values) - 3
                    max_temp = max(temp_values) + 3
                    ax2.set_ylim(min_temp, max_temp)
    else:
        # 온도 데이터가 없으면 숨기기
        ax2.set_visible(False)
        fig.set_size_inches(max(10, len(dates)*0.5), 3)

    # 감정 타임라인 설정
    ax1.set_xlim(0, len(dates))
    ax1.set_ylim(0, 1.3)  # 날씨 이모지 공간 확보
    ax1.set_xticks(np.arange(len(dates)) + 0.4)
    ax1.set_xticklabels([d.strftime("%m/%d") for d in dates], rotation=45)
    ax1.set_yticks([])
    
    # 온도 그래프 설정
    ax2.set_xticks(np.arange(len(dates)) + 0.4)
    ax2.set_xticklabels([d.strftime("%m/%d") for d in dates], rotation=45)

    # 범례 생성 (중복 제거)
    unique_emotions = []
    for emotion, color in zip(emotions, colors):
        if (emotion, color) not in unique_emotions:
            unique_emotions.append((emotion, color))
    
    legend = [mpatches.Patch(color=color, label=emotion) for emotion, color in unique_emotions]
    ax1.legend(handles=legend, bbox_to_anchor=(1.01, 1), loc="upper left")

    ax1.set_title(f"감정 지도{title_suffix}")
    plt.tight_layout()
    plt.show()

def draw_monthly_calendar(year=None, month=None):
    if year is None or month is None:
        now = datetime.now()
        year, month = now.year, now.month
    
    records = load_records()
    if not records:
        print("표시할 기록이 없습니다.")
        return
    
    # 해당 월의 기록만 필터링
    month_prefix = f"{year}-{month:02d}-"
    monthly_records = [r for r in records if r["date"].startswith(month_prefix)]
    
    if not monthly_records:
        print(f"{year}년 {month}월 기록이 없습니다.")
        return
    
    # 월간 달력 생성
    cal = calendar.monthcalendar(year, month)
    
    # 날짜별 정보 매핑
    date_to_color = {r["date"]: r["color"] for r in monthly_records}
    date_to_emotion = {r["date"]: r["emotion"] for r in monthly_records}
    date_to_note = {r["date"]: r["note"] for r in monthly_records}
    date_to_weather = {}
    
    # 날씨 정보가 있으면 추가
    for r in monthly_records:
        if "weather" in r and r["weather"]:
            emoji = r["weather"].get("emoji", "")
            temp = r["weather"].get("temp", "")
            if emoji and temp:
                date_to_weather[r["date"]] = f"{emoji} {temp}°C"
    
    # 그림 설정
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # 요일 헤더
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    
    # 표 생성
    the_table = plt.table(cellText=[[""] * 7 for _ in cal],
                         colLabels=weekdays,
                         loc='center',
                         cellLoc='center')
    
    # 표 스타일 설정
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1, 3)  # 셀 크기 조정
    
    # 날짜와 감정 표시
    for i, week in enumerate(cal):
        for j, day in enumerate(week):
            if day == 0:  # 빈 셀
                continue
                
            date_str = f"{year}-{month:02d}-{day:02d}"
            cell_text = f"{day}"
            cell_color = "white"
            
            if date_str in date_to_color:
                cell_color = date_to_color[date_str]
                cell_text = f"{day}\n{date_to_emotion[date_str]}"
                
                # 날씨 정보가 있으면 추가
                if date_str in date_to_weather:
                    cell_text += f"\n{date_to_weather[date_str]}"
                
                # 셀에 툴팁으로 노트 추가
                cell = the_table[i+1, j]  # 요일 헤더가 있어서 i+1
                cell.get_text().set_text(cell_text)
                cell.set_facecolor(cell_color)
                
                # 노트 정보를 위한 툴팁
                note = date_to_note[date_str]
                tooltip_text = f"{date_str}\n{note}"
                if date_str in date_to_weather:
                    tooltip_text += f"\n{date_to_weather[date_str]}"
                
                ax.annotate(tooltip_text,
                           xy=(cell.get_x()+cell.get_width()/2, 
                               cell.get_y()+cell.get_height()/2),
                           xytext=(20, 20),
                           textcoords="offset points",
                           bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8),
                           arrowprops=dict(arrowstyle="->"),
                           visible=False)
            else:
                cell = the_table[i+1, j]
                cell.get_text().set_text(cell_text)
    
    # 마우스 호버 이벤트 처리
    def hover(event):
        for i, ann in enumerate(ax.texts):
            if ann.get_visible():
                ann.set_visible(False)
                
        for cell in the_table.get_celld().values():
            contains, _ = cell.contains(event)
            if contains:
                x, y = cell.get_x()+cell.get_width()/2, cell.get_y()+cell.get_height()/2
                for ann in ax.texts:
                    if abs(ann._x - x) < 0.01 and abs(ann._y - y) < 0.01:
                        ann.set_visible(True)
                        break
        
        fig.canvas.draw_idle()
    
    fig.canvas.mpl_connect("motion_notify_event", hover)
    
    plt.title(f"{year}년 {month}월 감정 캘린더")
    plt.tight_layout()
    plt.show()

def draw_emotion_distribution():
    records = load_records()
    if not records:
        print("표시할 기록이 없습니다.")
        return
    
    # 감정별 횟수 계산
    emotion_counts = {}
    for record in records:
        emotion = record["emotion"]
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # 감정 맵 로드
    emotion_map = load_emotion_map()
    
    # 그래프 생성
    emotions = list(emotion_counts.keys())
    counts = list(emotion_counts.values())
    colors = [emotion_map.get(emotion, "#CCCCCC") for emotion in emotions]
    
    plt.figure(figsize=(10, 6))
    
    # 원형 그래프
    plt.subplot(1, 2, 1)
    patches, texts, autotexts = plt.pie(counts, labels=emotions, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('감정 분포 (전체 기간)')
    
    # 막대 그래프
    plt.subplot(1, 2, 2)
    bars = plt.bar(emotions, counts, color=colors)
    plt.title('감정별 기록 횟수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 막대 위에 숫자 표시
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

def analyze_weather_emotion():
    """날씨와 감정의 상관관계 분석"""
    records = load_records()
    weather_records = [r for r in records if "weather" in r and r["weather"]]
    
    if not weather_records or len(weather_records) < 3:
        print("날씨 정보가 충분하지 않습니다. (최소 3개 이상 필요)")
        return
    
    # 날씨별 감정 집계
    weather_emotion_map = {}
    
    for record in weather_records:
        weather_main = record["weather"].get("weather", "Unknown")
        temp = record["weather"].get("temp", 0)
        emotion = record["emotion"]
        
        # 온도 구간 (5도 단위)
        temp_range = f"{5 * (temp // 5)}-{5 * (temp // 5) + 5}"
        
        # 날씨별 집계
        if weather_main not in weather_emotion_map:
            weather_emotion_map[weather_main] = {}
        
        if emotion not in weather_emotion_map[weather_main]:
            weather_emotion_map[weather_main][emotion] = 0
        
        weather_emotion_map[weather_main][emotion] += 1
        
        # 온도별 집계
        key = f"온도 {temp_range}°C"
        if key not in weather_emotion_map:
            weather_emotion_map[key] = {}
        
        if emotion not in weather_emotion_map[key]:
            weather_emotion_map[key][emotion] = 0
        
        weather_emotion_map[key][emotion] += 1
    
    # 그래프 생성
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    
    # 1. 날씨별 감정 분포
    weather_types = [w for w in weather_emotion_map.keys() if not w.startswith("온도")]
    x_pos = np.arange(len(weather_types))
    
    width = 0.8 / len(set(emotion for record in weather_records for emotion in [record["emotion"]]))
    
    # 모든 감정 목록
    all_emotions = sorted(set(record["emotion"] for record in weather_records))
    
    # 감정 맵 로드해서 색상 가져오기
    emotion_map = load_emotion_map()
    
    # 각 감정별 막대 그래프 그리기
    for i, emotion in enumerate(all_emotions):
        heights = []
        for weather in weather_types:
            count = weather_emotion_map[weather].get(emotion, 0)
            heights.append(count)
        
        axs[0].bar(x_pos + i * width - width * len(all_emotions) / 2, 
                  heights, 
                  width=width, 
                  label=emotion,
                  color=emotion_map.get(emotion, "#CCCCCC"))
    
    axs[0].set_title('날씨별 감정 분포')
    axs[0].set_xticks(x_pos)
    axs[0].set_xticklabels(weather_types)
    axs[0].legend()
    
    # 2. 온도별 감정 분포
    temp_ranges = sorted([w for w in weather_emotion_map.keys() if w.startswith("온도")])
    x_pos = np.arange(len(temp_ranges))
    
    # 각 감정별 막대 그래프 그리기
    for i, emotion in enumerate(all_emotions):
        heights = []
        for temp_range in temp_ranges:
            count = weather_emotion_map[temp_range].get(emotion, 0)
            heights.append(count)
        
        axs[1].bar(x_pos + i * width - width * len(all_emotions) / 2, 
                  heights, 
                  width=width, 
                  label=emotion,
                  color=emotion_map.get(emotion, "#CCCCCC"))
    
    axs[1].set_title('온도별 감정 분포')
    axs[1].set_xticks(x_pos)
    axs[1].set_xticklabels(temp_ranges)
    axs[1].legend()
    
    plt.tight_layout()
    plt.show()

def show_menu():
    print("\n===== 감정 시각화 메뉴 =====")
    print("1. 전체 기간 감정 지도")
    print("2. 이번 달 감정 지도")
    print("3. 이번 주 감정 지도")
    print("4. 월간 감정 캘린더")
    print("5. 감정 분포 통계")
    print("6. 날씨-감정 상관관계 분석")
    print("7. 돌아가기")
    
    choice = input("\n선택: ").strip()
    
    if choice == "1":
        records = load_records()
        draw_emotion_map(records, 'all')
    elif choice == "2":
        records = load_records()
        draw_emotion_map(records, 'month')
    elif choice == "3":
        records = load_records()
        draw_emotion_map(records, 'week')
    elif choice == "4":
        now = datetime.now()
        year, month = now.year, now.month
        
        print("\n확인할 월을 선택하세요:")
        print(f"1. 이번 달 ({month}월)")
        print("2. 다른 달 입력")
        
        choice = input("\n선택 (기본: 1): ").strip() or "1"
        
        if choice == "2":
            try:
                year = int(input("연도: "))
                month = int(input("월 (1-12): "))
                if not 1 <= month <= 12:
                    print("유효한 월을 입력해주세요.")
                    return
            except ValueError:
                print("유효한 숫자를 입력해주세요.")
                return
        
        draw_monthly_calendar(year, month)
    elif choice == "5":
        draw_emotion_distribution()
    elif choice == "6":
        analyze_weather_emotion()
    elif choice == "7":
        return
    else:
        print("잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    show_menu()
