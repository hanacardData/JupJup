import asyncio
import sys

from bot.services.core.post_payload import async_post_message

prefix = sys.argv[1]
pr_title = sys.argv[2]
pr_author = sys.argv[3]
pr_url = sys.argv[4]
test_channel_id = sys.argv[5]

message = f"{prefix}\n제목: {pr_title}\n작성자: {pr_author}\n링크: {pr_url}"

if __name__ == "__main__":
    asyncio.run(async_post_message(message, test_channel_id))
