from datetime import datetime

import pandas as pd

from batch.security_monitor.prompt import SECURITY_PROMPT, SECURITY_TEXT_INPUT
from batch.variables import DATA_PATH
from bot.services.core.openai_client import openai_response
from logger import logger


def generate_security_alert_messages() -> list[str]:
    try:
        data = pd.read_csv(DATA_PATH)

        new_issues = data[data["is_posted"] == 0]

        if new_issues.empty:
            return ["오늘은 보안 관련 주목할만한 이슈가 없습니다."]

        messages = []
        for _, row in new_issues.iterrows():
            content = f"- 제목: {row['title']}\n- 내용: {row['description']}\n- 링크: {row['link']}"
            prompt_input = SECURITY_TEXT_INPUT.format(content=content)
            result = openai_response(prompt=SECURITY_PROMPT, input=prompt_input)

            if result:
                messages.append(
                    f"📌 {datetime.today().strftime('%Y-%m-%d')} 보안 이슈 알림\n\n{result}"
                )
                data.loc[data["link"] == row["link"], "is_posted"] = 1

        data.to_csv(DATA_PATH, index=False, encoding="utf-8")
        return messages

    except Exception as e:
        logger.error(f"보안 메시지 생성 실패: {e}")
        return ["보안 이슈 알림 생성 중 오류가 발생했습니다."]
