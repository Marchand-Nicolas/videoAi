import asyncio
import cv2
import numpy as np
from playwright.async_api import async_playwright
import random
import time

WIDTH, HEIGHT = 1920, 1080
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

        await asyncio.sleep(1)

        print("🔄 Scrolling and recording...")

        start = time.time()

        # Set up OpenCV video writer
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        out = cv2.VideoWriter("screen.mp4", fourcc, FPS, (WIDTH, HEIGHT))
        step_num = 0
        speed_multiplier = random.uniform(0.9, 1.1)
        for i in range(FPS * DURATION):
            scroll_i = i % (2 * FPS)
            new_step_num = step_num = i // (2 * FPS)
            if step_num != new_step_num:
                speed_multiplier = random.uniform(0.5, 1.5)
            scroll_speed = (
                bell_curve((scroll_i - FPS) / FPS)
                * 30
                * speed_multiplier
                * random.uniform(0.7, 1.1)
            )
            if FPS <= scroll_i:
                await page.evaluate(f"window.scrollBy(0, {scroll_speed})")
            screenshot_bytes = await page.screenshot(type="jpeg", quality=70)
            img_array = np.frombuffer(screenshot_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            await asyncio.to_thread(out.write, frame)

        out.release()
        await browser.close()
        print("✅ Saved to output.mp4")

        end = time.time()
        elapsed_time = end - start
        print(f"⏱️ Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(record_browser())
