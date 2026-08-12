#!/usr/bin/env python3
"""Render a marketplace GIF of a GitHub PR whose secret scan fails."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
OUT = Path(__file__).resolve().parents[1] / "demos" / "redactcli-failed-pr.gif"

BG = (13, 17, 23)
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT = (230, 237, 243)
MUTED = (139, 148, 158)
LINK = (88, 166, 255)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
YELLOW = (210, 153, 34)
WHITE = (255, 255, 255)
CHIP = (33, 38, 45)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box, fill, radius: int = 10, outline=None) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def base() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 56), fill=(22, 27, 34))
    d.line((0, 56, W, 56), fill=BORDER)
    d.text((28, 16), "AshSgDe29071999 / acme-api", font=font(20, bold=True), fill=TEXT)
    d.rounded_rectangle((430, 14, 500, 42), radius=8, outline=BORDER)
    d.text((442, 18), "Public", font=font(13), fill=MUTED)
    tabs = [("Code", False), ("Issues", False), ("Pull requests 14", True), ("Actions", False)]
    x = 28
    for label, active in tabs:
        color = TEXT if active else MUTED
        d.text((x, 68), label, font=font(16, bold=active), fill=color)
        if active:
            d.line((x, 96, x + 8 * len(label), 96), fill=(247, 129, 102), width=3)
        x += 8 * len(label) + 28
    return img


def pr_header(d: ImageDraw.ImageDraw) -> None:
    d.ellipse((32, 118, 56, 142), outline=GREEN, width=2)
    d.text((68, 116), "chore: dump debug env for agent session", font=font(26, bold=True), fill=TEXT)
    d.text((32, 160), "Open", font=font(14, bold=True), fill=GREEN)
    d.text((86, 160), "#184 opened 2 minutes ago by dev-bot  ·  +12 −0  ·  into main", font=font(14), fill=MUTED)


def checks_card(
    d: ImageDraw.ImageDraw,
    rows: list[tuple[str, str, tuple[int, int, int]]],
    summary: str,
    summary_color: tuple[int, int, int],
) -> None:
    rounded(d, (32, 210, 1248, 520), PANEL, 12, BORDER)
    d.text((52, 228), "Checks", font=font(18, bold=True), fill=TEXT)
    d.text((1060, 230), summary, font=font(14), fill=summary_color)
    y = 270
    for title, detail, color in rows:
        d.ellipse((56, y + 6, 76, y + 26), fill=color)
        d.text((92, y), title, font=font(18, bold=True), fill=TEXT)
        d.text((92, y + 28), detail, font=font(14), fill=MUTED)
        y += 68


def annotation(d: ImageDraw.ImageDraw, *, visible: bool) -> None:
    if not visible:
        return
    rounded(d, (32, 540, 1248, 688), (47, 27, 30), 12, RED)
    d.text((52, 556), "redactcli Secret Scan", font=font(16, bold=True), fill=RED)
    d.text((52, 588), "agent.log:14:1: aws_access_key_id (high)  AWS_ACCESS_KEY_ID=AKIA…EXAMPLE", font=font(16), fill=TEXT)
    d.text((52, 620), "agent.log:15:1: github_pat (high)  GITHUB_TOKEN=ghp_…", font=font(16), fill=TEXT)
    d.text((52, 652), "2 finding(s)  ·  job failed  ·  secrets never left the runner", font=font(14), fill=MUTED)


def frame(state: str) -> Image.Image:
    img = base()
    d = ImageDraw.Draw(img)
    pr_header(d)

    if state == "pending":
        rows = [
            ("CI / test", "Queued — ubuntu-latest", YELLOW),
            ("redactcli Secret Scan", "Waiting to start…", MUTED),
            ("lint", "Waiting to start…", MUTED),
        ]
        checks_card(d, rows, "3 queued", MUTED)
        annotation(d, visible=False)
    elif state == "running":
        rows = [
            ("CI / test", "Passed in 18s", GREEN),
            ("redactcli Secret Scan", "Scanning git diff…", YELLOW),
            ("lint", "Passed in 7s", GREEN),
        ]
        checks_card(d, rows, "1 in progress", YELLOW)
        annotation(d, visible=False)
    else:
        rows = [
            ("CI / test", "Passed in 18s", GREEN),
            ("redactcli Secret Scan", "Failed in 4s — secrets in diff", RED),
            ("lint", "Passed in 7s", GREEN),
        ]
        checks_card(d, rows, "1 failing", RED)
        annotation(d, visible=True)
    d.text((32, H - 22), "Marketplace preview  ·  AshSgDe29071999/redactcli", font=font(12), fill=MUTED)
    return img


def main() -> None:
    frames = [
        (frame("pending"), 900),
        (frame("running"), 1100),
        (frame("failed"), 2200),
    ]
    images = [im.convert("P", palette=Image.ADAPTIVE, colors=64) for im, _ in frames]
    durations = [d for _, d in frames]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        OUT,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
