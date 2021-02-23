import subprocess
import os


def create_screenshot(url: str) -> str:

    if os.path.exists("screenshot.png"):
        os.remove("screenshot.png")

    proc = subprocess.run(
        [
            "google-chrome",
            "--headless",
            "--screenshot",
            "--window-size=550,450",
            "--allow-file-access-from-files",
            "--lang=ja-JP",
            "--disable-gpu",
            "--virtual-time-budget=1000000",
            url,
        ]
    )

    return "screenshot.png"
    # os.rename("screenshot.png", "test.png")


if __name__ == "__main__":
    create_screenshot("embed.html")