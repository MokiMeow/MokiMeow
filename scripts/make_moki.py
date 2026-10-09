#!/usr/bin/env python3
"""Moki — an animated ASCII cat for a GitHub profile README.

Moki sleeps as a loaf, an ear twitches, he wakes, looks around, does a big
arms-up stretch, waves a paw hello, purrs little hearts with his tail
swishing, yawns, and loafs back down. Loops.

    python scripts/make_moki.py                  -> assets/moki-buddy.gif
    python scripts/make_moki.py --theme light    -> assets/moki-buddy-light.gif

The art is pure ASCII on a fixed 19-column grid so it stays aligned in any
monospace font. The face always lives on the same three rows and columns, and
the tail is attached to the body rather than floating.
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
        "nose": (255, 143, 171),
        "heart": (255, 143, 171),
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
        "nose": (214, 73, 113),
        "heart": (214, 73, 113),
        "zzz": (84, 120, 214),
        "text": (110, 118, 129),
        "accent": (26, 158, 108),
    },
}

# ------------------------------------------------------------------- art ----
# Everything is drawn on a 19-column body grid, centred on column 9 (the nose).
# Rows 0-2 are always the head: ears, eyes, whiskers. Tails attach at the right
# edge of the bottom rows, so the cat always reads as one connected creature.

GRID_W = 19
NOSE_COL = 9

# The pair of eyes, five characters wide; `look` slides them a column.
EYES_OPEN = "o   o"
EYES_SHUT = "-   -"
EYES_HAPPY = "^   ^"
EYES_SQUEEZE = ">   <"
EYES_WINK = "-   o"


def _eyes(pair, look=0):
    """Return the 9 characters between the cheeks; `look` is -1, 0 or +1."""
    return " " * (2 + look) + pair + " " * (2 - look)


def _stamp(line, col, text):
    """Overwrite `text` into `line` at `col`, growing the line if needed."""
    line = line.ljust(col + len(text))
    return line[:col] + text + line[col + len(text):]


def head(eyes=EYES_OPEN, look=0, nose="^", ears="/\\_____/\\"):
    return [
        f"     {ears}     ",
        f"    /{_eyes(eyes, look)}\\    ",
        f"   ( ==  {nose}  == )   ",
    ]


def _with_tail(lines, tail):
    """Attach a tail to the bottom-right of a body, growing up from the feet."""
    shapes = {
        "flat": ["~~,"],
        "flick": ["~-,"],
        "drift": ["-~,"],
        "up": ["/", " _,"],
        "high": ["/", " /", "  ,"],
    }
    base = len(lines[-1].rstrip())
    for rows_up, text in enumerate(shapes[tail]):
        row = len(lines) - 1 - rows_up
        lines[row] = _stamp(lines[row].rstrip(), base, text)
    return lines


def sitting(eyes=EYES_OPEN, look=0, nose="^", tail="flat", wave=None):
    """Moki sitting upright, front paws together.

    `wave` raises the *left* foreleg ("up" or "out"). The raised paw replaces
    the resting one, and it goes on the opposite side from the tail so the
    silhouette stays balanced.
    """
    lines = head(eyes, look, nose) + [
        "    )         (    ",
        "   (           )   ",
        "  ( (  )   (  ) )  ",
        " (__(__)___(__)__)",
    ]

    if wave:
        lines[5] = "  (        (  ) )  "
        lines[6] = " (_________(__)__)"
        if wave == "up":
            lines[0] = _stamp(lines[0], 2, "o")
            lines[1] = _stamp(lines[1], 3, "\\")
        else:
            lines[1] = _stamp(lines[1], 2, "o-")

    return _with_tail(lines, tail)


def loaf(eyes=EYES_SHUT, nose="^", tail="flat", ears="/\\_____/\\"):
    """Moki tucked into a loaf, asleep."""
    lines = head(eyes, 0, nose, ears) + [
        "  (_(__)___(__)_)",
    ]
    return _with_tail(lines, tail)


def stretching(nose="o", tail="up", reach=True):
    """Both front paws thrown up, body pulled a row taller — the big stretch."""
    lines = head(EYES_SQUEEZE, 0, nose) + [
        "    )         (    ",
        "   (           )   ",
        "   (           )   ",
        "  (             )  ",
        " (_______________)",
    ]
    if reach:
        lines[0] = _stamp(_stamp(lines[0], 2, "o"), 16, "o")
        lines[1] = _stamp(_stamp(lines[1], 3, "\\"), 15, "/")
    else:
        # halfway there: paws out to the sides
        lines[1] = _stamp(_stamp(lines[1], 2, "o-"), 15, "-o")
    return _with_tail(lines, tail)


# Things that float above the head: (rows above the ears, column, text, colour)

def zzz(stage):
    """Sleep bubbles rising to the upper right."""
    return [
        [(1, 15, "z", "zzz")],
        [(1, 15, "z", "zzz"), (2, 17, "Z", "zzz")],
        [(1, 15, "z", "zzz"), (2, 17, "Z", "zzz"), (3, 19, "z", "zzz")],
        [(2, 17, "z", "zzz"), (3, 19, "Z", "zzz")],
    ][stage]


def hearts(stage):
    """Little hearts drifting up while he purrs."""
    return [
        [(1, 15, "<3", "heart")],
        [(2, 16, "<3", "heart")],
        [(1, 2, "<3", "heart")],
        [(2, 1, "<3", "heart"), (1, 15, "<3", "heart")],
        [(2, 16, "<3", "heart")],
        [(1, 2, "<3", "heart")],
    ][stage]


def say(text, row=0, col=16):
    """A word next to the head. Negative `rows above` means beside the body."""
    return [(-row, col, text, "accent")]


# ----------------------------------------------------------------- frames ---


def build_frames():
    frames = []

    def add(body, extras=(), ms=120, status="sleeping"):
        # Body and extras are kept apart so the renderer can anchor the cat's
        # feet to a fixed baseline (it grows upward when it sits up) while the
        # bubbles float above whatever the current head height is.
        frames.append({"body": body, "extras": list(extras), "ms": ms,
                       "status": status})

    # --- asleep: tail drifting, bubbles rising --------------------------
    tails = ["flat", "flat", "flick", "flick", "flat", "flat", "drift", "drift"]
    for i in range(8):
        add(loaf(tail=tails[i]), zzz(i // 2), ms=280)

    # --- an ear twitches ------------------------------------------------
    add(loaf(ears="/\\_____/|"), zzz(3), ms=140)
    add(loaf(), zzz(3), ms=120)
    add(loaf(ears="/\\_____/|"), zzz(3), ms=140)
    add(loaf(), ms=260)

    # --- one eye opens, then both, a blink, a look around ---------------
    add(loaf(eyes=EYES_WINK), ms=320, status="waking up")
    add(loaf(eyes=EYES_OPEN), ms=240, status="waking up")
    add(loaf(eyes=EYES_SHUT), ms=110, status="waking up")
    add(loaf(eyes=EYES_OPEN, tail="flick"), ms=240, status="waking up")
    add(sitting(tail="flat"), ms=220, status="waking up")
    add(sitting(look=-1, tail="flick"), ms=300, status="waking up")
    add(sitting(look=1, tail="flat"), ms=300, status="waking up")
    add(sitting(tail="drift"), ms=200, status="waking up")

    # --- the big stretch ------------------------------------------------
    add(stretching(reach=False, tail="flat"), ms=180, status="big stretch")
    add(stretching(nose="o", tail="up"), say("mrrp", col=19), ms=260,
        status="big stretch")
    add(stretching(nose="O", tail="high"), say("mrrp", col=19), ms=420,
        status="big stretch")
    add(stretching(reach=False, tail="up"), ms=160, status="big stretch")
    add(sitting(tail="flat"), ms=220, status="big stretch")

    # --- waves hello ----------------------------------------------------
    wave_poses = ["out", "up", "out", "up", "out", "up", "out"]
    wave_tails = ["flat", "up", "flat", "up", "flat", "up", "flat"]
    for i in range(7):
        add(sitting(eyes=EYES_HAPPY, tail=wave_tails[i], wave=wave_poses[i]),
            say("hi!") if i > 0 else (), ms=170, status="saying hi")

    # --- purring: hearts, tail swishing, happy blinks -------------------
    purr_tails = ["flat", "up", "high", "up", "flat", "up"]
    for i in range(6):
        add(sitting(eyes=EYES_HAPPY if i % 3 else EYES_SHUT,
                    tail=purr_tails[i]),
            hearts(i), ms=220, status="purring")

    # --- a yawn, then settling down -------------------------------------
    add(sitting(eyes=EYES_SHUT, nose="o"), ms=220, status="sleepy again")
    add(sitting(eyes=EYES_SQUEEZE, nose="O", tail="flick"), ms=420,
        status="sleepy again")
    add(sitting(eyes=EYES_SHUT), ms=220, status="sleepy again")
    add(loaf(eyes=EYES_SHUT, tail="flick"), ms=320, status="sleepy again")

    # --- asleep again ---------------------------------------------------
    for i in range(3):
        add(loaf(tail="flat" if i % 2 else "flick"), ms=300)

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


def body_colour(row, col, ch, palette):
    """Pick a colour for one character of the cat, by where it sits."""
    if row == 1 and 5 <= col <= 13 and ch in "o^-><":
        return palette["eye"]
    if row == 2 and ch == "=":
        return palette["cat_dim"]            # whiskers
    if row == 2 and col == NOSE_COL:
        return palette["nose"]
    return palette["cat"]


def render(frames, palette, out_path, scale=3):
    """Render at `scale` then downsample — cheap anti-aliasing."""
    fs = 20 * scale
    font = load_font(fs)
    small = load_font(int(12 * scale), bold=False)

    cw = round(font.getlength("M"))
    line_h = int(fs * 1.18)

    width, height = 520 * scale, 360 * scale
    pad = 16 * scale

    # The cat's feet sit on a fixed baseline and the body grows *upward*, so
    # standing up looks like standing up rather than the whole cat sliding.
    feet_y = height - pad - 86 * scale
    # A fixed left origin (not per-frame centring) so the body never jitters
    # sideways when the tail changes width.
    left = (width - GRID_W * cw) // 2

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

        title = "moki.cat"
        draw.text(((width - small.getlength(title)) // 2, pad + 14 * scale),
                  title, font=small, fill=palette["text"])

        body = frame["body"]
        body_top = feet_y - (len(body) - 1) * line_h

        for row, line in enumerate(body):
            for col, ch in enumerate(line):
                if ch != " ":
                    draw.text((left + col * cw, body_top + row * line_h), ch,
                              font=font,
                              fill=body_colour(row, col, ch, palette))

        # Bubbles, hearts and words float relative to the ears, wherever the
        # head currently is.
        for rows_above, col, text, colour in frame["extras"]:
            draw.text((left + col * cw, body_top - rows_above * line_h), text,
                      font=font, fill=palette[colour])

        # A tiny status line, like a prompt at the bottom of the window.
        x, y = pad + 22 * scale, height - pad - 32 * scale
        draw.text((x, y), "> moki is ", font=small, fill=palette["text"])
        draw.text((x + small.getlength("> moki is "), y), frame["status"],
                  font=small, fill=palette["accent"])

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
