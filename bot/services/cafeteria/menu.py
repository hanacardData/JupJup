from datetime import datetime, timedelta

import pytz

from bot.services.cafeteria.variables import CAFETERIA_MENU


def get_weekly_menu_message() -> str:
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    today = now.strftime("%a")
    tomorrow = (now + timedelta(days=1)).strftime("%a")

    day_map = {
        "Mon": "월",
        "Tue": "화",
        "Wed": "수",
        "Thu": "목",
        "Fri": "금",
        "Sat": "토",
        "Sun": "일",
    }

    today_kr = day_map.get(today)
    tomorrow_kr = day_map.get(tomorrow)

    msg = f"📅 오늘({today_kr})과 내일({tomorrow_kr})의 구내식당 메뉴\n\n"

    # 오늘 메뉴
    msg += f"▶️ 오늘 ({today_kr}) 메뉴\n"
    today_menu = CAFETERIA_MENU.get(today_kr)
    if today_menu:
        msg += format_menu(today_menu)
    else:
        msg += "  🙅‍♀️ 오늘은 구내식당이 운영되지 않습니다.\n"

    # 내일 메뉴
    msg += f"\n▶️ 내일 ({tomorrow_kr}) 메뉴\n"
    tomorrow_menu = CAFETERIA_MENU.get(tomorrow_kr)
    if tomorrow_menu:
        msg += format_menu(tomorrow_menu)
    else:
        msg += "  🙅‍♀️ 내일은 구내식당이 운영되지 않습니다.\n"

    # 마무리멘트
    msg += "\n맛있는 하루 되세요~! 😄"

    return msg.strip()


def format_menu(menu: dict) -> str:
    msg = ""
    msg += f"  🍳 조식: {menu.get('조식', '정보 없음')}\n"

    lunch = menu.get("중식", {})
    msg += f"  🍚 중식(감성집밥): {lunch.get('감성집밥', '정보 없음')}\n"
    msg += f"  🥘 중식(BLANK): {lunch.get('BLANK', '정보 없음')}\n"
    msg += f"  🥗 중식(H-PLATE): {lunch.get('H-PLATE', '정보 없음')}\n"

    return msg
