#!/usr/bin/env python3
"""Moki — an animated ASCII cat for a GitHub profile README.

Moki sleeps curled up, an ear twitches, he wakes, stretches, sits up, waves a
paw hello, purrs with his tail flicking, yawns, and curls back down. Loops.

    python scripts/make_moki.py                  -> assets/moki-buddy.gif
    python scripts/make_moki.py --theme light    -> assets/moki-buddy-light.gif

The art is pure ASCII on a fixed 13-column grid so it stays aligned in any
monospace font, and the tail is attached to the body rather than floating.
Requires Pillow: ``python -m pip install Pillow``.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- palette ---

THEMES = {
    "dark": {
        "bg": (13, 17, 23),
        "card": (22, 27, 34),
        "border": (48, 54, 61),
        "cat": (245, 222, 190),
        "cat_dim": (176, 152, 122),
        "eye": (126, 231, 176),
        "zzz": (122, 162, 247),
        "text": (125, 133, 144),
        "accent": (126, 231, 176),
    },
    "light": {
        "bg": (255, 255, 255),
        "card": (246, 248, 250),
        "border": (208, 215, 222),
        "cat": (94, 71, 45),
        "cat_dim": (150, 124, 96),
        "eye": (26, 158, 108),
        "zzz": (84, 120, 214),
        "text": (110, 118, 129),
        "accent": (26, 158, 108),
    },
}

# ------------------------------------------------------------------- art ----
# Everything is drawn on a 13-column body grid. Tails attach at the right edge
# of a body line, so the cat always reads as one connected creature.


def sitting(eyes="o o", mouth="w", tail="~~,", paws="(_) (_)", wave=None):
    """Moki sitting upright.

    `tail` attaches to the body's right side. `wave` raises the *left* foreleg
    — paw, arm and shoulder are drawn as one connected limb, and it goes on the
    opposite side from the tail so the silhouette stays balanced.
    """
    lines = [
        "   /\\___/\\   ",
        f"  (  {eyes}  )  ",
        f"   >  {mouth}  <   ",
        "  /|     |\\  ",
        f" ( |     | ){tail}",
        "  \\|_____|/  ",
        f"   {paws}   ",
    ]

    if wave == "up":
        # paw(0,0) -> arm(1,1) -> arm(2,2) -> shoulder(2,3)
        lines[0] = "o  /\\___/\\   "
        lines[1] = f" \\(  {eyes}  )  "
        # Remove the resting left paw (`>`) while that same paw is raised.
        lines[2] = f"  |   {mouth}  <   "
        lines[3] = "  \\|     |\\  "
        lines[4] = f"   |     | ){tail}"
        lines[5] = "   |_____|/  "
    elif wave == "out":
        # the same limb, swung down a notch
        lines[1] = f"o (  {eyes}  )  "
        lines[2] = f" \\|   {mouth}  <   "
        lines[3] = "  \\|     |\\  "
        lines[4] = f"   |     | ){tail}"
        lines[5] = "   |_____|/  "

    return lines


def curled(eyes="-.-", mouth="w", tail="~~,"):
    """Moki curled into a loaf, asleep."""
    return [
        "   /\\___/\\   ",
        f"  (  {eyes}  )  ",
        f"  (   {mouth}   ){tail}",
        "  (_)___(_)  ",
    ]


def stretching(eyes="^ ^", mouth="o", tail="__,"):
    """Front legs out, back arched — the long stretch."""
    return [
        "   /\\___/\\    ",
        f"  (  {eyes}  )   ",
        f"   >  {mouth}  <    ",
        "  /|     |\\   ",
        f" ( |     | )--{tail}",
        "  \\|_____|/   ",
        "  (__)  (__)  ",
    ]


def zzz_layer(stage):
    """Sleep bubbles rising to the upper right. Three lines, always."""
    return [
        ["", "", "            z"],
        ["", "          z", "            Z"],
        ["        z", "          Z", "            z"],
        ["      z", "        z", "          Z"],
    ][stage]


# ----------------------------------------------------------------- frames ---


def build_frames():
    frames = []

    def add(body, sleep=None, ms=120, note=None, note_color="accent"):
        # Body and bubbles are kept apart so the renderer can anchor the cat's
        # feet to a fixed baseline (it grows upward when it sits up) while the
        # bubbles float above whatever the current head height is.
        frames.append({
            "body": body,
            "bubbles": zzz_layer(sleep) if sleep is not None else [],
            "ms": ms,
            "note": note,
            "note_color": note_color,
        })

    # --- asleep: slow breathing, tail drifting, bubbles rising ----------
    tails = ["~~,", "~~,", "~-,", "~-,", "~~,", "~~,", "-~,", "-~,"]
    for i in range(8):
        add(curled(eyes="-.-" if i % 4 < 2 else "- -", tail=tails[i]),
            sleep=i // 2, ms=280)

    # --- an ear twitches ------------------------------------------------
    add(curled(eyes="- -", tail="~~,"), sleep=3, ms=150)
    add(["   /\\___/|   ", "  (  - -  )  ", "  (   w   )~~,", "  (_)___(_)  "],
        sleep=3, ms=140)
    add(["   |\\___/\\   ", "  (  - -  )  ", "  (   w   )~~,", "  (_)___(_)  "],
        sleep=3, ms=140)
    add(curled(eyes="- -"), sleep=3, ms=220)

    # --- one eye opens, then both, then a blink -------------------------
    add(curled(eyes="- o"), ms=280)
    add(curled(eyes="o o"), ms=220)
    add(curled(eyes="- -"), ms=110)
    add(curled(eyes="o o", tail="~-,"), ms=260)

    # --- the stretch ----------------------------------------------------
    add(stretching(eyes="^ ^", mouth="o"), ms=220, note="mrrp",
        note_color="text")
    add(stretching(eyes="^ ^", mouth="O", tail="___,"), ms=300, note="mrrp",
        note_color="text")
    add(sitting(eyes="o o", tail="~-,"), ms=200)

    # --- sits up and waves ----------------------------------------------
    wave_poses = ["up", "out", "up", "out", "up", "out"]
    wave_tails = ["_/", "~~,", "\\_,", "~~,", "_/", "~~,"]
    for i in range(6):
        add(sitting(eyes="^ ^", tail=wave_tails[i], wave=wave_poses[i]),
            ms=170, note="hi!" if i > 0 else None)

    # --- purring, tail flicking, happy blinks ---------------------------
    purr_tails = ["~~,", "_/", "~~,", "\\_,", "~~,", "_/"]
    for i in range(6):
        add(sitting(eyes="^ ^" if i % 2 == 0 else "- -", tail=purr_tails[i]),
            ms=160, note="purrr" if i % 2 == 0 else "purr ",
            note_color="text")

    # --- a yawn, then settling down -------------------------------------
    add(sitting(eyes="- -", mouth="o"), ms=240)
    add(sitting(eyes="- -", mouth="O", tail="~-,"), ms=320, note="~yawn~",
        note_color="text")
    add(sitting(eyes="- -", mouth="w"), ms=200)
    add(curled(eyes="- -"), ms=260)

    # --- asleep again ---------------------------------------------------
    for i in range(4):
        add(curled(eyes="-.-", tail="~~," if i % 2 else "~-,"),
            sleep=min(i, 3), ms=320)

    return frames


# ---------------------------------------------------------------- render ---


def load_font(size, bold=True):
    if bold:
        candidates = [
            "DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
            r"C:\Windows\Fonts\consolab.ttf",
            "/System/Library/Fonts/SFNSMono.ttf",
        ]
    else:
        candidates = [
            "DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            r"C:\Windows\Fonts\consola.ttf",
            "/System/Library/Fonts/SFNSMono.ttf",
        ]

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def render(frames, palette, out_path, scale=3):
    """Render at `scale` then downsample — cheap anti-aliasing."""
    fs = 20 * scale
    font = load_font(fs)
    small = load_font(int(11 * scale), bold=False)

    cw = round(font.getlength("M"))
    line_h = int(fs * 1.18)

    width, height = 520 * scale, 360 * scale
    pad = 16 * scale

    # The cat's feet sit on a fixed baseline and the body grows *upward*, so
    # standing up looks like standing up rather than the whole cat sliding.
    feet_y = height - pad - 52 * scale
    # A fixed left origin (not per-frame centring) so the body never jitters
    # sideways when the tail changes width.
    left = (width - 16 * cw) // 2

    images, durations = [], []

    for frame in frames:
        image = Image.new("RGB", (width, height), palette["bg"])
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(
            [pad, pad, width - pad, height - pad],
            radius=16 * scale, fill=palette["card"],
            outline=palette["border"], width=max(1, scale),
        )

        for i, dot in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
            cx, cy = pad + (22 + i * 20) * scale, pad + 22 * scale
            r = 5 * scale
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dot)

        body = frame["body"]
        body_top = feet_y - (len(body) - 1) * line_h

        def put(line, y, body_row=None):
            for col, ch in enumerate(line):
                if ch == " ":
                    continue
                x = left + col * cw
                if ch in "zZ":
                    colour = palette["zzz"]
                elif body_row is not None and col >= 12:
                    colour = palette["cat_dim"]      # the tail
                elif body_row == 1 and 5 <= col <= 7 and ch in "o^":
                    colour = palette["eye"]      # eyes only, not a raised paw
                else:
                    colour = palette["cat"]
                draw.text((x, y), ch, font=font, fill=colour)

        # Bubbles float above the head, wherever the head currently is.
        for i, line in enumerate(frame["bubbles"]):
            put(line, body_top - (len(frame["bubbles"]) - i) * line_h)

        for row, line in enumerate(body):
            put(line, body_top + row * line_h, body_row=row)

        if frame["note"]:
            draw.text((width - pad - 110 * scale, height - pad - 38 * scale),
                      frame["note"], font=small,
                      fill=palette[frame["note_color"]])

        draw.text((pad + 22 * scale, height - pad - 30 * scale),
                  "moki", font=small, fill=palette["text"])

        image = image.resize((width // scale, height // scale), Image.LANCZOS)
        images.append(image.convert("P", palette=Image.ADAPTIVE, colors=128))
        durations.append(frame["ms"])

    images[0].save(out_path, save_all=True, append_images=images[1:],
                   duration=durations, loop=0, optimize=True, disposal=2)
    return out_path, len(images)


def main():
    parser = argparse.ArgumentParser(description="Render the Moki cat GIF.")
    parser.add_argument("--theme", choices=("dark", "light"), default="dark")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    default_name = ("moki-buddy.gif" if args.theme == "dark"
                    else "moki-buddy-light.gif")
    out = Path(args.out) if args.out else ROOT / "assets" / default_name
    out.parent.mkdir(parents=True, exist_ok=True)
    frames = build_frames()
    path, count = render(frames, THEMES[args.theme], out)
    total = sum(f["ms"] for f in frames) / 1000
    print(f"wrote {path}: {count} frames, {total:.1f}s loop, theme={args.theme}")


if __name__ == "__main__":
    main()
