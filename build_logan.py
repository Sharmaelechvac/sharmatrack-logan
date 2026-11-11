#!/usr/bin/env python3
"""Build the Logan Construction (Bella Collina) SHARMATRACK app from the EXJ base.
HVAC-ONLY single job: Lot 69 Bella Collina, 16051 Vetta Dr, Montverde, FL 34756."""
import re, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
EXJ212 = os.path.expanduser("~/workspace/github-migration/exj-root-tracker/212/index.html")

# ---------- 1. Logan wordmark PNG (no real logo found on the web; DNR-style fallback) ----------
ARCH = os.path.expanduser("~/workspace/goodman-flyer/assets/Archivo-Bold.ttf")
def arch(size, weight=800, width=100):
    f = ImageFont.truetype(ARCH, size)
    try: f.set_variation_by_axes([weight, width])
    except Exception: pass
    return f
wm = Image.new("RGB", (1240, 400), "white")
wd = ImageDraw.Draw(wm)
def tracked_w(text, font, tr):
    return sum(wd.textbbox((0, 0), ch, font=font)[2] for ch in text) + tr * (len(text) - 1)
def draw_tracked_center(y, text, font, fill, tr):
    w = tracked_w(text, font, tr)
    x = (1240 - w) // 2
    for ch in text:
        wd.text((x, y), ch, font=font, fill=fill)
        x += wd.textbbox((0, 0), ch, font=font)[2] + tr
draw_tracked_center(58, "LOGAN", arch(150, 850, 112), (11, 45, 84), 26)
wd.line([(390, 252), (850, 252)], fill=(201, 162, 39), width=6)
draw_tracked_center(282, "CONSTRUCTION GROUP", arch(54, 700, 110), (86, 102, 118), 12)
wm.save(os.path.join(ROOT, "logo-logan.png"))
print("wordmark saved")

# ---------- 2. app.js: force HVAC for hvacOnly jobs ----------
p = os.path.join(ROOT, "app.js")
s = open(p).read()
old = 'if (trade !== "elec" && trade !== "hvac") trade = "elec";'
assert old in s
s = s.replace(old, old + '\n  if (JOB.hvacOnly) trade = "hvac";')
open(p, "w").write(s)
print("app.js patched (hvacOnly)")

# ---------- 3. home.js: HVAC checklist captions + job list ----------
p = os.path.join(ROOT, "home.js")
s = open(p).read()
app = open(os.path.join(ROOT, "app.js")).read()
def extract(listname):
    m = re.search(listname + r" = \[(.*?)\];", app, re.S)
    return re.findall(r'en: "([^"]+)"', m.group(1))
caps = extract("HTRIM") + extract("HSTART")
assert len(caps) == 20, len(caps)
newlist = "var ROUGH_EN = [\n    " + ",\n    ".join('"%s"' % c for c in caps) + "\n  ];"
s = re.sub(r"var ROUGH_EN = \[.*?\];", newlist, s, flags=re.S)
s = s.replace('var JOBS = ["212", "17385", "14065", "16321", "601"]; // seeded by tools/add_house.py',
              'var JOBS = ["lot69"];')
open(p, "w").write(s)
print("home.js patched (20 HVAC captions, JOBS=lot69)")

# ---------- 4. styles.css: Logan duo sizing ----------
p = os.path.join(ROOT, "styles.css")
s = open(p).read()
s += "\n/* Logan wordmark in the duo */\n.duo-logan{height:58px;width:auto;max-width:100%}\n"
open(p, "w").write(s)
print("styles.css patched")

# ---------- 5. Home page ----------
home = open(os.path.join(ROOT, "index.html")).read()
home = home.replace("<title>SHARMATRACK — Job Tracker · EXJ Root</title>",
                    "<title>SHARMATRACK — Job Tracker · Logan Construction</title>")
home = home.replace('<span class="duo-card"><img class="duo-exj" src="logo-exj.png" alt="EXJ Root LLC"></span>',
                    '<span class="duo-card"><img class="duo-logan" src="logo-logan.png" alt="Logan Construction Group"></span>')
home = home.replace('<div class="builder-ed">EXJ Root LLC · Builder edition</div>',
                    '<div class="builder-ed">Logan Construction Group · Builder edition</div>')
cards = re.findall(r'\n  <a class="jobbtn".*?</a>', home, re.S)
assert len(cards) == 5, len(cards)
for c in cards:
    home = home.replace(c, "")
card = ('\n  <a class="jobbtn" href="lot-69/" data-jobcard="lot69" data-search="16051 vetta dr montverde fl logan construction bella collina lot 69 hvac">'
        '<span class="a">16051 Vetta Dr</span><span class="b">Montverde, FL 34756</span>'
        '<span class="b2">Logan Construction · Lot 69 · Bella Collina · HVAC</span>'
        '<span class="crow"><span class="prog" data-prog>—/20</span><span class="chip" data-chip hidden></span></span><span class="arr">→</span></a>')
home = home.replace('<!-- HOUSE-CARDS: tools/add_house.py inserts one jobbtn card per house above this line -->',
                    '<!-- HOUSE-CARDS -->' + card)
open(os.path.join(ROOT, "index.html"), "w").write(home)
print("home page built")

# ---------- 6. Job page: Lot 69 ----------
src = open(EXJ212).read()
def grab(start_marker, end_marker):
    a = src.index(start_marker)
    b = src.index(end_marker, a)
    return src[a:b]
hvac_sections = grab('<div class="section" id="phase-hrough"', '<div class="st-footer">')
footer_block = grab('<div class="st-footer">', '<script>window.JOB_PAGE')
tail_scripts = src[src.index('<script>window.JOB_PAGE'):]
# lightbox markup sits between footer and JOB_PAGE script in EXJ pages; keep whatever is there
mid = src[src.index('<div class="st-footer">'):src.index('<script>window.JOB_PAGE')]
lightbox = mid[len(footer_block):] if mid.startswith(footer_block) else ""

page = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SHARMATRACK — 16051 Vetta Dr</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css?v=23">
<link rel="icon" href="../sharmatrack-app-icon.png">
<link rel="apple-touch-icon" href="../sharmatrack-app-icon.png">
<script>try{if(localStorage.getItem("sharma-theme")==="dark")document.documentElement.setAttribute("data-theme","dark")}catch(e){}</script>
</head><body>

<div class="langbar" role="group" aria-label="Language">
  <span class="lbl" data-i18n="language">Language</span>
  <button type="button" data-lang="en" class="on">🇺🇸 English</button>
  <button type="button" data-lang="es">🇲🇽 Español</button>
  <button type="button" data-lang="pt">🇧🇷 Português</button>
  <button type="button" class="theme-toggle" aria-label="Dark or white background">🌙 Dark</button>
</div>
<div class="jobbar"><span class="jb-brand"><a href="https://sharmaelechvac.github.io/sharmatrack" target="_blank" rel="noopener"><img src="../sharmatrack-app-icon.png" alt="">SHARMATRACK</a></span><span class="jb-addr">16051 Vetta Dr · Montverde, FL</span><span class="jb-num" id="jobbar-num">0/20</span></div>
<div class="wrap" data-job="lot69">
  <div class="hero">
    <div class="duo"><span class="duo-card"><img class="duo-sharma" src="../logo.png?v=2" alt="Sharma Electric &amp; HVAC"></span><span class="duo-card"><img class="duo-logan" src="../logo-logan.png" alt="Logan Construction Group"></span></div>
    <h1>16051 Vetta Dr</h1>
    <div class="city">Montverde, FL</div>
    <div class="lic">Sharma Electric &amp; HVAC · Lic. EC13013924 · CAC1823596</div>
    <div class="meta">
      <span class="tile"><i data-i18n="builder">Builder</i><b>Logan Construction</b></span>
      <span class="tile"><i>Job</i><b>Lot 69 · Bella Collina</b></span>
      <span class="tile"><i>Trade</i><b>HVAC</b></span>
      <span class="tile"><i>Systems</i><b>3 · R-454B</b></span>
      <span class="tile"><i data-i18n="phase">Phase</i><b>HVAC Rough</b></span>
    </div>
  </div>

  <div class="progress">
    <div class="ringwrap">
      <svg width="92" height="92" viewBox="0 0 92 92"><defs><linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2f7fc4"/><stop offset="1" stop-color="#004585"/></linearGradient></defs>
        <circle cx="46" cy="46" r="40" fill="none" stroke="#e2eaf2" stroke-width="9"/>
        <circle id="ring-fg" cx="46" cy="46" r="40" fill="none" stroke="url(#ringGrad)" stroke-width="9" stroke-linecap="round"/>
      </svg>
      <div class="num" id="ring-num">0/20</div>
    </div>
    <div><div class="pt" data-i18n="photoProgress">Photo progress</div>
    <div class="ps" id="ring-sub">0 of 20 captions</div></div>
  </div>
  <a class="mapsbtn" href="https://www.google.com/maps/search/?api=1&amp;query=16051+Vetta+Dr+Montverde+FL+34756" target="_blank" rel="noopener" data-i18n="openInMaps">Open in Maps</a>
  <details class="section">
    <summary data-i18n="howToUse">How to use</summary>
    <ol>
      <li data-step="0"></li>
      <li data-step="1"></li>
      <li data-step="2"></li>
      <li data-step="3"></li>
    </ol>
  </details>
  <div class="section scopebox">
    <h2>HVAC scope of work</h2>
    <ul>
      <li>Install 3 HVAC systems — R-454B refrigerant</li>
      <li>HVAC rough-in, equipment set &amp; trims, and start-up</li>
    </ul>
  </div>
  <div id="hvac-details">
  <div class="section jobmeta">
    <h2>HVAC job details</h2>
    <dl class="jm-rows">
      <div><dt>Trade</dt><dd>HVAC</dd></div>
      <div><dt data-i18n="lotNo">Lot #</dt><dd id="jm-lot">69</dd></div>
      <div><dt>Jurisdiction</dt><dd>Lake County</dd></div>
      <div><dt data-i18n="crewLbl">Assigned crew</dt><dd id="jm-crew">—</dd></div>
      <div><dt data-i18n="workDate">Work date</dt><dd id="jm-date">—</dd></div>
    </dl>
    <button type="button" class="jmedit" id="jm-edit" data-i18n="edit">Edit</button>
    <form id="jm-form" hidden>
      <label><span data-i18n="permitNo">Permit #</span><input id="jm-f-permit" type="text" autocomplete="off"></label>
      <label><span data-i18n="lotNo">Lot #</span><input id="jm-f-lot" type="text" autocomplete="off"></label>
      <label><span data-i18n="inspection">Inspection</span><select id="jm-f-status">
        <option value="" data-i18n="inspNone">Not requested</option>
        <option value="requested" data-i18n="inspRequested">Requested</option>
        <option value="passed" data-i18n="inspPassed">Passed</option>
        <option value="failed" data-i18n="inspFailed">Failed</option>
      </select></label>
      <label id="jm-f-reason-row" hidden><span data-i18n="failReason">Reason</span><input id="jm-f-reason" type="text" autocomplete="off"></label>
      <label><span data-i18n="crewLbl">Assigned crew</span><input id="jm-f-crew" type="text" autocomplete="off"></label>
      <label><span data-i18n="workDate">Work date</span><input id="jm-f-date" type="date"></label>
      <div class="jm-btns"><button type="submit" class="jmsave" data-i18n="save">Save</button><button type="button" id="jm-cancel" data-i18n="cancel">Cancel</button></div>
      <div class="upnote" id="jm-note"></div>
    </form>
  </div>
  <div class="section inspbox">
    <h2 data-i18n="inspections">Inspections</h2>
    <dl class="jm-rows">
      <div><dt data-i18n="inspStage">Stage</dt><dd>HVAC Rough</dd></div>
      <div><dt data-i18n="inspWhen">Date</dt><dd>—</dd></div>
      <div><dt data-i18n="inspStatus">Status</dt><dd id="jm-insp">—</dd></div>
      <div id="jm-reason-row" hidden><dt data-i18n="failReason">Reason</dt><dd id="jm-reason">—</dd></div>
    </dl>
  </div>
  </div>
  <div class="phasetabs" id="tabs-hvac" role="tablist">
    <button type="button" data-phase="hrough" data-i18n="tabHRough">HVAC Rough</button>
    <button type="button" data-phase="htrim" data-i18n="tabHTrim">Machine &amp; Trims</button>
    <button type="button" data-phase="hstart" data-i18n="tabHStart">Start-Up</button>
  </div>
"""
page += hvac_sections
page += footer_block + lightbox
page += '<script>window.JOB_PAGE = { id: "lot69", defaultMeta: {}, address: "16051 Vetta Dr, Montverde, FL", phase: "hrough", hvacOnly: true };</script>\n'
# app.js + any other trailing scripts from the EXJ page (skip its JOB_PAGE script tag itself)
tail = re.findall(r'<script src="[^"]+"></script>', tail_scripts)
page += "\n".join(tail) + "\n</body></html>\n"
open(os.path.join(ROOT, "lot-69", "index.html"), "w").write(page)
print("job page built:", len(page), "bytes")
