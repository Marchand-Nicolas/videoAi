import asyncio
import cv2
import numpy as np
from playwright.async_api import async_playwright
import random

WIDTH, HEIGHT = 1280, 720
FPS = 60
DURATION = 10  # seconds


def bell_curve(x, k=20):
    return np.exp(-k * (x - 0.5) ** 2)


async def record_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        try:
            await page.goto(
                "https://commons.wikimedia.org/wiki/Category:Fossils", timeout=60000
            )
        except Exception as e:
            print("⚠️ Page load error:", e)

        await asyncio.sleep(2)

        # Set up OpenCV video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter("output.mp4", fourcc, FPS, (WIDTH, HEIGHT))
        step_num = 0
        speed_multiplier = random.uniform(0.5, 1.5)
        for i in range(FPS * DURATION):
            scroll_i = i % (3 * FPS)
            new_step_num = step_num = i // (3 * FPS)
            if step_num != new_step_num:
                speed_multiplier = random.uniform(0.5, 1.5)
            scroll_speed = (
                bell_curve((scroll_i - FPS) / 2 / FPS)
                * 30
                * speed_multiplier
                * random.uniform(0.7, 1.1)
            )
            if FPS <= scroll_i:
                print(scroll_speed)
                await page.evaluate(f"window.scrollBy(0, {scroll_speed})")
            screenshot_bytes = await page.screenshot(type="png")
            img_array = np.frombuffer(screenshot_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            out.write(frame)

        out.release()
        await browser.close()
        print("✅ Saved to output.mp4")


if __name__ == "__main__":
    asyncio.run(record_browser())
