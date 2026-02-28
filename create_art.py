from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import math
import random
import numpy as np

W, H = 2400, 1600
img = Image.new('RGB', (W, H), (5, 8, 18))
draw = ImageDraw.Draw(img)

FONTS = "/mnt/skills/examples/canvas-design/canvas-fonts/"

rng = random.Random(777)

# ── Background gradient sky ──────────────────────────────────────────────────
sky = Image.new('RGB', (W, H))
sky_draw = ImageDraw.Draw(sky)
for y in range(H):
    t = y / H
    r = int(8 + 22 * t)
    g = int(12 + 25 * t)
    b = int(32 + 55 * t)
    sky_draw.line([(0, y), (W, y)], fill=(r, g, b))
img = Image.blend(img, sky, 1.0)
draw = ImageDraw.Draw(img)

# ── Noise / atmosphere layer ─────────────────────────────────────────────────
noise_arr = np.zeros((H, W, 3), dtype=np.uint8)
for _ in range(4000):
    x = rng.randint(0, W-1)
    y = rng.randint(0, H//2)
    v = rng.randint(5, 18)
    noise_arr[y, x] = [v, v+2, v+5]
noise_img = Image.fromarray(noise_arr)
img = ImageChops.add(img, noise_img)
draw = ImageDraw.Draw(img)

# ── City skyline ──────────────────────────────────────────────────────────────
def draw_building(d, x, w, h_top, h_bottom, base_col, win_col, win_amber=False):
    d.rectangle([x, h_top, x+w, h_bottom], fill=base_col)
    wx = x + 6
    while wx < x + w - 12:
        wy = h_top + 15
        while wy < h_bottom - 10:
            lit = rng.random() < 0.45
            if lit:
                if win_amber:
                    col = (rng.randint(180,255), rng.randint(100,160), rng.randint(10,40))
                else:
                    col = (rng.randint(40,80), rng.randint(80,140), rng.randint(150,220))
            else:
                col = (12, 15, 28)
            d.rectangle([wx, wy, wx+8, wy+12], fill=col)
            wy += 20
        wx += 18

# Background city (dark, far)
buildings_bg = []
x = 0
while x < W:
    bw = rng.randint(60, 180)
    bh = rng.randint(H//3, H*2//3)
    col = (rng.randint(20,35), rng.randint(25,40), rng.randint(45,65))
    buildings_bg.append((x, bw, bh))
    draw_building(draw, x, bw, H - bh, H, col, (30, 50, 80))
    x += bw - rng.randint(0, 20)

# Mid city
x = 0
while x < W:
    bw = rng.randint(40, 130)
    bh = rng.randint(H//4, H//2)
    col = (rng.randint(18,32), rng.randint(20,35), rng.randint(38,55))
    draw_building(draw, x, bw, H - bh, H, col, (40, 70, 110), win_amber=(x > W//2))
    x += bw - rng.randint(0, 10)

# Ground plane
draw.rectangle([0, H - 120, W, H], fill=(8, 10, 20))

# ── Surveillance side (left) ─────────────────────────────────────────────────
# Cold blue tint over left half
left_overlay = Image.new('RGBA', (W, H), (0, 20, 60, 0))
left_draw = ImageDraw.Draw(left_overlay)
left_draw.rectangle([0, 0, W//2, H], fill=(10, 25, 60, 35))
img = Image.alpha_composite(img.convert('RGBA'), left_overlay).convert('RGB')
draw = ImageDraw.Draw(img)

# Surveillance cameras
def draw_camera(d, cx, cy, angle=0):
    import math
    # Camera body
    d.rectangle([cx-18, cy-8, cx+18, cy+8], fill=(40,50,65))
    # Lens
    d.ellipse([cx+10, cy-6, cx+22, cy+6], fill=(20,30,45), outline=(60,80,100), width=2)
    # Mount
    d.rectangle([cx-3, cy+8, cx+3, cy+20], fill=(35,45,60))
    # Indicator LED (cold blue)
    d.ellipse([cx-15, cy-4, cx-9, cy+2], fill=(0, 150, 255))

for cam_x, cam_y in [(180, 320), (320, 480), (80, 600), (450, 250), (150, 720)]:
    draw_camera(draw, cam_x, cam_y)
    # Scan line from camera
    draw.line([(cam_x+16, cam_y), (cam_x + rng.randint(60,160), cam_y + rng.randint(30,80))],
              fill=(0, 80, 160, 80), width=1)

# Rigid grid lines (cold surveillance aesthetic)
for i in range(0, W//2, 120):
    alpha_val = rng.randint(8, 20)
    for row in range(H):
        draw.point((i, row), fill=(alpha_val, alpha_val+5, alpha_val+15))
for j in range(0, H, 90):
    for col in range(0, W//2):
        draw.point((col, j), fill=(8, 10, 22))

# ── Underground warm glow (right side) ──────────────────────────────────────
# Warm amber glow source - underground gathering
glow_cx, glow_cy = W * 3//4, H * 4//5

# Radial amber gradient
glow_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_layer)
for r in range(320, 0, -4):
    t = r / 320
    alpha = int((1 - t) * 90)
    amber_r = int(255 * (1-t*0.3))
    amber_g = int(140 * (1-t*0.5))
    amber_b = int(20 * (1-t*0.7))
    gd.ellipse([glow_cx - r, glow_cy - r, glow_cx + r, glow_cy + r],
               fill=(amber_r, amber_g, amber_b, alpha))
img = Image.alpha_composite(img.convert('RGBA'), glow_layer).convert('RGB')
draw = ImageDraw.Draw(img)

# Underground archway / opening
draw.ellipse([glow_cx - 110, glow_cy - 80, glow_cx + 110, glow_cy + 80],
             fill=(60, 35, 10))
draw.ellipse([glow_cx - 90, glow_cy - 65, glow_cx + 90, glow_cy + 65],
             fill=(90, 55, 15))
draw.ellipse([glow_cx - 70, glow_cy - 50, glow_cx + 70, glow_cy + 50],
             fill=(140, 85, 25))

# People silhouettes in the glow
for px, py, ph in [(glow_cx - 45, glow_cy - 10, 28),
                    (glow_cx - 15, glow_cy - 15, 32),
                    (glow_cx + 20, glow_cy - 8, 26),
                    (glow_cx + 50, glow_cy - 12, 30)]:
    # Body
    draw.rectangle([px - 6, py - ph, px + 6, py], fill=(20, 12, 5))
    # Head
    draw.ellipse([px - 7, py - ph - 14, px + 7, py - ph], fill=(20, 12, 5))

# Rays of warm light emanating upward
for angle_deg in range(-60, 61, 15):
    ang = math.radians(angle_deg - 90)
    length = rng.randint(150, 350)
    ex = glow_cx + int(math.cos(ang) * length)
    ey = glow_cy + int(math.sin(ang) * length)
    for _ in range(3):
        overlay2 = Image.new('RGBA', (W, H), (0,0,0,0))
        od = ImageDraw.Draw(overlay2)
        od.line([(glow_cx, glow_cy), (ex + rng.randint(-10,10), ey)],
                fill=(180, 100, 20, 20), width=2)
        img = Image.alpha_composite(img.convert('RGBA'), overlay2).convert('RGB')
draw = ImageDraw.Draw(img)

# ── Central holographic web of data ─────────────────────────────────────────
fig_x, fig_y = W // 2, H * 3 // 5  # figure position

# Web nodes
web_nodes = []
for i in range(28):
    angle = rng.uniform(0, 2 * math.pi)
    radius = rng.uniform(120, 420)
    nx = fig_x + int(math.cos(angle) * radius)
    ny = fig_y - 200 + int(math.sin(angle) * radius * 0.7)
    web_nodes.append((nx, ny))

# Web connections
web_layer = Image.new('RGBA', (W, H), (0,0,0,0))
wd = ImageDraw.Draw(web_layer)
for i, (nx, ny) in enumerate(web_nodes):
    for j in range(i+1, len(web_nodes)):
        mx, my = web_nodes[j]
        dist = math.hypot(nx-mx, ny-my)
        if dist < 280:
            alpha = int(max(0, (1 - dist/280) * 120))
            # Cyan-blue data lines
            wd.line([(nx, ny), (mx, my)], fill=(40, 160, 220, alpha), width=1)

# Brighten key nodes
for i, (nx, ny) in enumerate(web_nodes):
    brightness = rng.randint(60, 180)
    size = rng.randint(3, 8)
    wd.ellipse([nx-size, ny-size, nx+size, ny+size],
               fill=(brightness, int(brightness*0.9), 255, 200))
    # Small data text fragments
    if rng.random() < 0.4:
        labels = ["CLASSIFIED", "REDACTED", "TRUTH", "DATA", "LEAK", "NODE_7",
                  "SUPPRESS", "DECODE", "ALERT", "ENCRYPTED", "FREE", "SIGNAL"]
        lbl = rng.choice(labels)
        # tiny mono text vibe (just colored dots arranged)

img = Image.alpha_composite(img.convert('RGBA'), web_layer).convert('RGB')
draw = ImageDraw.Draw(img)

# Data text fragments floating in web
try:
    font_mono_sm = ImageFont.truetype(FONTS + "DMMono-Regular.ttf", 11)
    font_mono_tiny = ImageFont.truetype(FONTS + "DMMono-Regular.ttf", 9)
except:
    font_mono_sm = ImageFont.load_default()
    font_mono_tiny = font_mono_sm

fragments = ["CLASSIFIED", "NODE_Ω", "REDACTED▓", "TRUTH.DAT",
             "LEAK_07", "SUPPRESS", "DECODE→", "SIGNAL", "FREE",
             "ENCRYPTED", "CENSORED", "DATA_CHAIN", "FORBIDDEN",
             "ΔΨ∇", "NULL_REF", "OVERRIDE"]

for i, (nx, ny) in enumerate(web_nodes):
    if rng.random() < 0.5 and 100 < nx < W-100:
        lbl = rng.choice(fragments)
        alpha_c = rng.randint(80, 180)
        draw.text((nx + 8, ny - 6), lbl, font=font_mono_tiny,
                  fill=(40 + alpha_c//3, 160, 220))

# Headline strips (news/data documents unraveling)
try:
    font_headline = ImageFont.truetype(FONTS + "GeistMono-Regular.ttf", 13)
except:
    font_headline = ImageFont.load_default()

headlines = [
    "PRESS RELEASE #447-B ██████ WITHHELD",
    "INTERNAL MEMO: DO NOT DISTRIBUTE",
    "CITIZEN SURVEILLANCE LOG — LEVEL 5",
    "TRUTH COMMISSION — SEALED RECORDS",
    "BROADCAST OVERRIDE PROTOCOL ALPHA",
    "NETWORK BLACKOUT ORDER ISSUED",
    "OFFICIAL NARRATIVE v2.3 — APPROVED",
    "DISSENT INDEX: CRITICAL THRESHOLD",
]
for i, hl in enumerate(headlines):
    hx = rng.randint(W//4, W*3//4)
    hy = rng.randint(H//6, H*2//3)
    alpha_h = rng.randint(60, 130)
    tilt = rng.randint(-15, 15)
    # Draw tilted text via small rotation
    tmp = Image.new('RGBA', (500, 30), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    color_var = rng.random()
    if color_var < 0.5:
        tcol = (alpha_h//2, int(alpha_h*0.8), alpha_h, 200)  # blue-ish
    else:
        tcol = (alpha_h, int(alpha_h*0.6), 10, 200)  # amber-ish
    td.text((5, 5), hl, font=font_headline, fill=tcol)
    tmp_r = tmp.rotate(tilt, expand=True)
    img.paste(tmp_r, (hx, hy), tmp_r)

draw = ImageDraw.Draw(img)

# ── Main figure silhouette ────────────────────────────────────────────────────
fig_ground = H - 130

# Bright aura/glow BEHIND figure from holographic web
fig_glow = Image.new('RGBA', (W, H), (0,0,0,0))
fgd = ImageDraw.Draw(fig_glow)
for r in range(200, 0, -5):
    t = r / 200
    alpha = int((1 - t**1.5) * 60)
    fgd.ellipse([fig_x - r, fig_ground - 300 - r//2, 
                 fig_x + r, fig_ground - 300 + r//2 + r],
               fill=(20, 80, 140, alpha))
img = Image.alpha_composite(img.convert('RGBA'), fig_glow).convert('RGB')
draw = ImageDraw.Draw(img)

# Body silhouette
body_w = 70
body_h = 260
# Legs
draw.rectangle([fig_x - 20, fig_ground - 110, fig_x - 5, fig_ground], fill=(4, 6, 12))
draw.rectangle([fig_x + 5, fig_ground - 110, fig_x + 20, fig_ground], fill=(4, 6, 12))
# Torso
draw.rectangle([fig_x - body_w//2, fig_ground - body_h + 50,
                fig_x + body_w//2, fig_ground - 100], fill=(4, 6, 12))
# Arms slightly spread
draw.rectangle([fig_x - body_w//2 - 40, fig_ground - body_h + 80,
                fig_x - body_w//2, fig_ground - body_h + 160], fill=(4, 6, 12))
draw.rectangle([fig_x + body_w//2, fig_ground - body_h + 80,
                fig_x + body_w//2 + 40, fig_ground - body_h + 160], fill=(4, 6, 12))
# Head
draw.ellipse([fig_x - 28, fig_ground - body_h - 20,
              fig_x + 28, fig_ground - body_h + 40], fill=(4, 6, 12))

# Rim light (amber from underground glow on right edge)
for dy in range(body_h):
    intensity = max(0, 1 - abs(dy - body_h//2) / (body_h//2))
    rim_bright = int(130 * intensity)
    draw.point((fig_x + body_w//2, fig_ground - body_h + 50 + dy),
               fill=(rim_bright, int(rim_bright*0.55), 5))
    if intensity > 0.5:
        draw.point((fig_x + body_w//2 + 1, fig_ground - body_h + 50 + dy),
                   fill=(rim_bright//2, int(rim_bright*0.25), 2))

# Blue rim on left (surveillance cold light)
for dy in range(body_h):
    intensity = max(0, 1 - abs(dy - body_h//2) / (body_h//2))
    rim_bright = int(100 * intensity)
    draw.point((fig_x - body_w//2, fig_ground - body_h + 50 + dy),
               fill=(5, int(rim_bright*0.5), rim_bright))
    if intensity > 0.5:
        draw.point((fig_x - body_w//2 - 1, fig_ground - body_h + 50 + dy),
                   fill=(2, int(rim_bright*0.25), rim_bright//2))

# ── Ground reflection ─────────────────────────────────────────────────────────
for gy in range(H - 130, H):
    t = (gy - (H-130)) / 130
    r_col = int(5 + 12*(1-t))
    g_col = int(8 + 15*(1-t))
    b_col = int(18 + 30*(1-t))
    draw.line([(0, gy), (W, gy)], fill=(r_col, g_col, b_col))

# Puddle reflections on ground
puddle = Image.new('RGBA', (W, H), (0,0,0,0))
pd = ImageDraw.Draw(puddle)
for px2, pw, palpha in [(fig_x - 80, 160, 40), (W*3//4 - 60, 120, 60)]:
    pd.ellipse([px2, H-100, px2+pw, H-70],
               fill=(30, 60, 90, palpha))
img = Image.alpha_composite(img.convert('RGBA'), puddle).convert('RGB')
draw = ImageDraw.Draw(img)

# ── Atmospheric fog / haze ────────────────────────────────────────────────────
img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
draw = ImageDraw.Draw(img)

# Light fog bands
fog = Image.new('RGBA', (W, H), (0,0,0,0))
fd = ImageDraw.Draw(fog)
for fy in range(H*2//3, H, 40):
    fog_alpha = rng.randint(4, 12)
    fd.rectangle([0, fy, W, fy+20], fill=(20, 30, 50, fog_alpha))
img = Image.alpha_composite(img.convert('RGBA'), fog).convert('RGB')
draw = ImageDraw.Draw(img)

# ── Typography ────────────────────────────────────────────────────────────────
try:
    font_title = ImageFont.truetype(FONTS + "BigShoulders-Bold.ttf", 88)
    font_sub = ImageFont.truetype(FONTS + "JetBrainsMono-Regular.ttf", 20)
    font_tag = ImageFont.truetype(FONTS + "IBMPlexMono-Regular.ttf", 14)
except:
    font_title = ImageFont.load_default()
    font_sub = font_title
    font_tag = font_title



# Bottom left tag
draw.text((60, H - 60), "YEAR ZERO / SECTOR 7 / UNAUTHORIZED TRANSMISSION", 
          font=font_tag, fill=(40, 65, 95))

# Bottom right tag
right_tag = "THE TRUTH CANNOT BE SUPPRESSED"
bbox = draw.textbbox((0,0), right_tag, font=font_tag)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 60, H - 60), right_tag, font=font_tag, fill=(100, 60, 15))

# Dividing line (subtle)
draw.line([(W//2 - 2, 60), (W//2 - 2, H - 60)], fill=(25, 35, 55), width=1)
draw.line([(W//2 + 2, 60), (W//2 + 2, H - 60)], fill=(40, 25, 10), width=1)

# ── Final color grade ─────────────────────────────────────────────────────────
# Slight vignette
vig = Image.new('RGBA', (W, H), (0,0,0,0))
vd = ImageDraw.Draw(vig)
for r in range(max(W, H)//2, 0, -8):
    t = r / (max(W, H)//2)
    alpha = int((1 - t) * 80)
    vd.ellipse([W//2 - r, H//2 - r, W//2 + r, H//2 + r],
               fill=(0, 0, 0, alpha))
img = Image.alpha_composite(img.convert('RGBA'), vig).convert('RGB')

# Boost contrast slightly
arr = np.array(img).astype(np.float32)
arr = np.clip((arr - 128) * 1.25 + 138, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)

# Save
out_path = "/mnt/user-data/outputs/dystopian_truth.png"
img.save(out_path, "PNG", dpi=(300, 300))
print(f"Saved to {out_path}")
