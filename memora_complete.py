"""
Memora — Smart Photo Curator (Final Release)
=============================================
Brand palette:
  #083A4F  Navy   — sidebar, primary text, deep backgrounds
  #A58D66  Gold   — CTA buttons, accents, active states, highlights
  #C0D5D6  Aqua   — surfaces, card backgrounds, subtle fills
  #407E8C  Teal   — secondary buttons, progress bar, hover states

Design: Rounded corners everywhere, premium feel, no harsh edges.

Flow: Add folders → Analyse → Review → Export
First launch: Registration screen (name + email + heard from)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, shutil, math, os, sys, time, base64, io
import urllib.request as _req, urllib.parse as _parse
from pathlib import Path
from datetime import datetime

# ── Dependencies ──────────────────────────────────────────────────────────────
MISSING = []
try:    import cv2
except: MISSING.append("opencv-python")
try:
    from PIL import Image, ImageTk
    import PIL.ExifTags
except: MISSING.append("Pillow")
try:    import numpy as np
except: MISSING.append("numpy")
try:    import imagehash
except: MISSING.append("imagehash")
try:    from sklearn.cluster import AgglomerativeClustering  # noqa
except: MISSING.append("scikit-learn")

if MISSING:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("Memora",
        f"Missing libraries.\n\nRun:\npy -3.11 -m pip install {' '.join(MISSING)}")
    sys.exit(1)

try:
    from deepface import DeepFace
    DEEPFACE_OK = True
except: DEEPFACE_OK = False

try:
    import rawpy
    RAWPY_OK = True
except: RAWPY_OK = False

IMAGE_EXT = {
    ".jpg",".jpeg",".png",".bmp",".gif",".webp",
    ".tiff",".tif",".heic",".heif",
    ".cr2",".cr3",".nef",".arw",".orf",
    ".rw2",".dng",".raf",".pef",".srw",
}
RAW_EXT = {".cr2",".cr3",".nef",".arw",".orf",".rw2",".dng",".raf",".pef",".srw"}

# ── Brand palette ─────────────────────────────────────────────────────────────
NAVY      = "#083A4F"   # Deep navy — sidebar, headers
NAVY2     = "#052C3D"   # Darker navy — hover on navy
NAVY3     = "#0A4A63"   # Lighter navy — card borders, subtle navy

GOLD      = "#A58D66"   # Warm gold — CTA buttons, active nav, accents
GOLD2     = "#8A7350"   # Darker gold — hover on gold
GOLD_LITE = "#F5EFE6"   # Very light gold — gold tinted surfaces

AQUA      = "#C0D5D6"   # Soft aqua — main surface background
AQUA2     = "#A8C4C5"   # Darker aqua — hover, card borders
AQUA_DEEP = "#8BB0B2"   # Deep aqua — secondary text on light bg

TEAL      = "#407E8C"   # Mid teal — progress bar, secondary buttons
TEAL2     = "#316170"   # Darker teal — hover on teal
TEAL_LITE = "#E0ECED"   # Very light teal — alternate row fills

WHITE     = "#FFFFFF"
OFF_WHITE = "#F8FAFA"   # Slightly aqua-tinted white for cards
TEXT      = "#083A4F"   # Navy as main text color
TEXT2     = "#407E8C"   # Teal as secondary text
TEXT3     = "#8BB0B2"   # Deep aqua as hint text
DANGER    = "#B94040"

# Sidebar
SB_BG     = "#052C3D"   # Very deep navy
SB_TXT    = "#C0D5D6"   # Aqua text on dark sidebar
SB_SUB    = "#407E8C"   # Teal subtext
SB_ACT_BG = "#083A4F"   # Navy active item bg
SB_ACT_FG = "#A58D66"   # Gold active item text

# Fonts — Segoe UI for Windows, falls back gracefully
F_BIG   = ("Segoe UI", 22, "bold")
F_TITLE = ("Segoe UI", 16, "bold")
F_BODY  = ("Segoe UI", 12)
F_BOLD  = ("Segoe UI", 12, "bold")
F_SMALL = ("Segoe UI", 11)
F_TINY  = ("Segoe UI", 10)
F_MONO  = ("Consolas", 10)

R = 10   # Standard corner radius for rounded widgets

# ── Embedded brand icon ───────────────────────────────────────────────────────
ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAT+klEQVR4nO3dvYocWZoG4KiiGMTIktXG3MLYAyN/oGhHRt/AgCi/rYa6AkFb8ouGuQEZcpqC9bWw9t7CGLJkaRBjSGNoUsrKyp/IiPP/PQ80u6uVMk9FBPm+8cWpqouJJjx5/uJL7TUAlPLp3duL2muIzgkoSMgDnKYclOEgZyDoAdJTDNJyMBMQ+ADlKQTrOHgLCX2AdigD53PAZhL4AP1QCE5zgE4Q/AD9UgQOc2D2EPoA41EGHnIwtgh+gPEpAl+FPwhCHyCuyGUg7Bcu+AHYiFgEwn3Bgh+AQyIVgTBfqOAHYK4IRWD4L1DwA7DUyEVg2C9M8AOQyohF4LL2AnIQ/gCkNGKuDNVoRjxBALRllGnAMBMA4Q9ACaPkTfctpoUT8dtPP9ReAkA4L9+8r72ErqcB3S58msqHv6AHaF/pYtBrCehy0aWCX+AD9K9UIeitCHS12GnKG/4CH2B8OQtBTyWgm4VOU77wF/wA8eQqAr2UgC4WmSP4hT4AGznKQOtFoOnFTVP68Bf8ABySugi0XAKaXdg0pQ1/wQ/AXCmLQKsloMlFTVO68Bf8ACyVqgi0WAKaW9A0pQl/wQ9AKimKQGsloKnFCH4AWjZSEWjmdwEIfwBalyJnWvgR9tPUyARg7cEQ/ACUtnYaUHsSUH0CIPwB6NHa/Kk9CahaAIQ/AD3ruQRUGz+s+aIFPwCtWfNIoMbjgCoTAOEPwGjW5FONSUDxAiD8ARhVTyWg+ibAuYQ/AD3oJa+KFoCl7aaXgwkA07Q8t0pOAYoVAOEPQCStl4AiBUD4AxBRyyUgewEQ/gBE1moJyFoAhD8AtFkCmvsuAOEPwIhay7dsBWBJa2nt4ABASktyLtcUIEsBEP4AsF8rJSB5ARD+AHBcCyWguT0AAEB+SQuAu38AmKf2FCBZAID"

def _icon_img():
    try:
        data = base64.b64decode(ICON_B64 + "==")
        return Image.open(io.BytesIO(data))
    except Exception:
        # Fallback — generate simple icon
        img = Image.new("RGBA", (64,64), "#083A4F")
        return img

def _set_icon(win):
    try:
        ico = ImageTk.PhotoImage(_icon_img().resize((32,32), Image.LANCZOS))
        win.iconphoto(True, ico); win._ico = ico
    except: pass

# ── Registration ──────────────────────────────────────────────────────────────
REG_FILE     = str(Path.home() / ".memora_reg")
SHEETS_URL   = "%%SHEETS_URL%%"  # injected at build time
HEARD_OPTIONS = [
    "Select one…",
    "WhatsApp / Telegram",
    "Friend or family",
    "Instagram / Facebook",
    "Wedding photographer",
    "Google search",
    "Other",
]

def is_registered():
    return Path(REG_FILE).exists()

def mark_registered():
    Path(REG_FILE).write_text("1")

def send_to_sheets(data):
    def _go():
        try:
            payload = _parse.urlencode(data).encode()
            r = _req.Request(SHEETS_URL, data=payload, method="POST")
            r.add_header("Content-Type","application/x-www-form-urlencoded")
            _req.urlopen(r, timeout=8)
        except: pass
    threading.Thread(target=_go, daemon=True).start()

# ── Splash ────────────────────────────────────────────────────────────────────
class Splash:
    W, H = 440, 260
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.configure(bg=NAVY)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")
        self.root.lift(); self.root.attributes("-topmost", True)
        _set_icon(self.root)
        self._build(); self._step(0)

    def _build(self):
        bg = tk.Frame(self.root, bg=NAVY)
        bg.pack(fill="both", expand=True)
        tk.Frame(bg, bg=GOLD, height=4).pack(fill="x")
        try:
            pil = _icon_img().resize((60,60), Image.LANCZOS)
            self._ico = ImageTk.PhotoImage(pil)
            tk.Label(bg, image=self._ico, bg=NAVY).pack(pady=(18,0))
        except: tk.Frame(bg, bg=NAVY, height=16).pack()
        tk.Label(bg, text="memora", font=("Segoe UI",26,"bold"),
                 bg=NAVY, fg=WHITE).pack(pady=(6,1))
        tk.Label(bg, text="smart photo curator",
                 font=("Segoe UI",10), bg=NAVY, fg=AQUA).pack()
        wrap = tk.Frame(bg, bg=NAVY)
        wrap.pack(fill="x", padx=54, pady=(16,5))
        self.track = tk.Frame(wrap, bg=NAVY2, height=5)
        self.track.pack(fill="x")
        self.fill = tk.Frame(wrap, bg=GOLD, height=5)
        self.fill.place(in_=self.track, x=0, y=0, relheight=1, width=0)
        self.msg = tk.StringVar(value="Initialising…")
        tk.Label(bg, textvariable=self.msg, font=("Segoe UI",9),
                 bg=NAVY, fg=TEAL).pack()
        tk.Frame(bg, bg=TEAL, height=2).pack(fill="x", side="bottom")

    def _step(self, n):
        msgs = {0:"Initialising…",6:"Loading libraries…",
                14:"Preparing interface…",26:"Almost ready…",35:"Welcome!"}
        if n in msgs: self.msg.set(msgs[n])
        if n <= 38:
            w = self.track.winfo_width()
            if w > 1: self.fill.place(width=int(n/38*w))
            self.root.after(46, lambda: self._step(n+1))
        else: self.root.after(180, self.root.destroy)

    def run(self): self.root.mainloop()

# ── Tooltip ───────────────────────────────────────────────────────────────────
class Tip:
    def __init__(self, w, text):
        self.w=w; self.text=text; self.tip=None
        w.bind("<Enter>",self.show); w.bind("<Leave>",self.hide)
    def show(self, e=None):
        if self.tip: return
        x = self.w.winfo_rootx()+20; y = self.w.winfo_rooty()+28
        self.tip = tk.Toplevel(self.w)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, font=("Segoe UI",10),
                 bg=NAVY, fg=WHITE, wraplength=260, justify="left",
                 padx=12, pady=8).pack()
    def hide(self, e=None):
        if self.tip: self.tip.destroy(); self.tip=None

def tip_btn(parent, text, bg=AQUA):
    lbl = tk.Label(parent, text="?", font=("Segoe UI",9,"bold"),
                   bg=GOLD, fg=WHITE, width=2,
                   cursor="question_arrow", relief="flat",
                   padx=2, pady=1)
    Tip(lbl, text)
    return lbl

# ── ETR ───────────────────────────────────────────────────────────────────────
class ETR:
    def __init__(self, total):
        self.total=max(total,1); self.done=0; self.start=time.time()
    def update(self,n): self.done=n
    def text(self):
        if self.done<5: return "Estimating…"
        rate=self.done/max(time.time()-self.start,0.001)
        rem=(self.total-self.done)/rate
        if rem<60:   return f"{int(rem)}s remaining"
        if rem<3600: return f"{int(rem/60)}m {int(rem%60)}s remaining"
        return f"{int(rem/3600)}h {int((rem%3600)/60)}m remaining"

# ── Rounded scrollable frame ──────────────────────────────────────────────────
class Scroller(tk.Frame):
    def __init__(self, parent, bg=AQUA, **kw):
        super().__init__(parent, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", lambda e:
            self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1*(e.delta//120),"units"))

# ── Image loading ─────────────────────────────────────────────────────────────
def load_img(path):
    if Path(path).suffix.lower() in RAW_EXT and RAWPY_OK:
        try:
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(use_camera_wb=True, output_bps=8)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        except: pass
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is not None: return img
    try:
        pil = Image.open(path).convert("RGB")
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    except: return None

def load_pil(path):
    if Path(path).suffix.lower() in RAW_EXT and RAWPY_OK:
        try:
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(use_camera_wb=True, output_bps=8)
            return Image.fromarray(rgb)
        except: pass
    try: return Image.open(path).convert("RGB")
    except: return None

# ── Analysis engine ───────────────────────────────────────────────────────────
def sharpness(gray):
    h,w=gray.shape
    roi=gray[int(h*.15):int(h*.85),int(w*.15):int(w*.85)]
    return float(cv2.Laplacian(roi,cv2.CV_64F).var())

def expo(b):
    if b<40:  return max(0.0,b/40.0)
    if b>230: return max(0.0,(255-b)/25.0)
    if b<80:  return 0.7+(b-40)/40.0*0.3
    return 1.0

def face_n(img):
    try:
        cc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=cc.detectMultiScale(gray,1.1,5,minSize=(40,40))
        return len(faces)
    except: return 0

def exif_dt(pil):
    try:
        ex=pil._getexif()
        if ex:
            for tag,val in ex.items():
                if PIL.ExifTags.TAGS.get(tag)=="DateTimeOriginal":
                    return datetime.strptime(val,"%Y:%m:%d %H:%M:%S")
    except: pass
    return None

def analyse(path):
    try:
        img=load_img(path)
        if img is None: return None
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        pil=load_pil(path)
        if pil is None: pil=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        sh=sharpness(gray); br=float(gray.mean()); fn=face_n(img)
        dt=exif_dt(pil); w,h=pil.size
        try:   ph=str(imagehash.phash(pil.convert("RGB")))
        except: ph=str(hash(path))
        return {"path":path,"sharp":sh,"bright":br,"expo":expo(br),
                "faces":fn,"phash":ph,"dt":dt.isoformat() if dt else None,
                "mp":(w*h)/1_000_000,"emo":0.0}
    except: return None

def emo_score(path):
    if not DEEPFACE_OK: return 0.0
    try:
        r=DeepFace.analyze(img_path=path,actions=["emotion"],
                           enforce_detection=False,silent=True)
        if isinstance(r,list): r=r[0]
        e=r.get("emotion",{})
        return min(1.0,(e.get("happy",0)+e.get("surprise",0)*0.25)/100.0)
    except: return 0.0

def score(p):
    return (min(1.0,math.log1p(p["sharp"])/9.0)*4.5+p["expo"]*2.0+
            min(1.0,p["faces"]*0.25)*3.0+min(1.0,p["mp"]/8.0)*0.8+
            p.get("emo",0.0)*2.5)

def dedup(photos,thr=8):
    n=len(photos)
    if n==0: return []
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: par[ra]=rb
    hsh=[imagehash.hex_to_hash(p["phash"]) for p in photos]
    for i in range(n):
        for j in range(i+1,n):
            if abs(hsh[i]-hsh[j])<=thr: union(i,j)
    cl={}
    for i in range(n): cl.setdefault(find(i),[]).append(i)
    return [max([photos[i] for i in v],key=lambda x:x["_score"]) for v in cl.values()]

def diverse(cands,target):
    if not cands: return []
    if target>=len(cands): return cands
    scored=sorted(cands,key=lambda x:x["_score"],reverse=True)
    dated=[p for p in scored if p["dt"]]
    if len(dated)<target*0.4: return scored[:target]
    dated.sort(key=lambda x:x["dt"])
    bkt=max(1,len(dated)//target)
    sel=[]
    for i in range(0,len(dated),bkt):
        chunk=dated[i:i+bkt]
        if chunk: sel.append(max(chunk,key=lambda x:x["_score"]))
        if len(sel)>=target: break
    paths={p["path"] for p in sel}
    extras=[p for p in scored if p["path"] not in paths]
    while len(sel)<target and extras: sel.append(extras.pop(0))
    return sel[:target]

# ── Rounded button helper ─────────────────────────────────────────────────────
def btn(parent, text, cmd, style="gold",
        padx=18, pady=9, font=F_BOLD):
    styles = {
        "gold":      (GOLD,      WHITE,  GOLD2),
        "navy":      (NAVY,      WHITE,  NAVY2),
        "teal":      (TEAL,      WHITE,  TEAL2),
        "secondary": (TEAL_LITE, TEAL,   AQUA2),
        "outline":   (OFF_WHITE, NAVY,   AQUA),
        "danger":    (DANGER,    WHITE,  "#8B2020"),
    }
    bg,fg,hv = styles.get(style, styles["gold"])
    b = tk.Button(parent, text=text, command=cmd,
                  font=font, bg=bg, fg=fg,
                  relief="flat", bd=0,
                  padx=padx, pady=pady,
                  cursor="hand2",
                  activebackground=hv, activeforeground=fg)
    return b

def card_frame(parent, bg=OFF_WHITE, radius=R):
    """Rounded card using highlightbackground for border effect."""
    f = tk.Frame(parent, bg=bg,
                 highlightbackground=AQUA2,
                 highlightthickness=1)
    return f

# ── Registration screen ───────────────────────────────────────────────────────
class Registration(tk.Tk):
    W, H = 520, 560

    def __init__(self):
        super().__init__()
        self.title("Memora — Welcome!")
        self.configure(bg=AQUA)
        self.resizable(False, False)
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        self.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")
        _set_icon(self)
        self._build()

    def _build(self):
        # Navy banner with gold bottom strip
        banner = tk.Frame(self, bg=NAVY, height=118)
        banner.pack(fill="x")
        banner.pack_propagate(False)
        tk.Frame(banner, bg=GOLD, height=4).pack(fill="x", side="bottom")
        top = tk.Frame(banner, bg=NAVY)
        top.pack(expand=True)
        try:
            pil = _icon_img().resize((46,46), Image.LANCZOS)
            self._ri = ImageTk.PhotoImage(pil)
            tk.Label(top, image=self._ri, bg=NAVY).pack(side="left", padx=(0,14))
        except: pass
        tf = tk.Frame(top, bg=NAVY)
        tf.pack(side="left")
        tk.Label(tf, text="Welcome to Memora!",
                 font=("Segoe UI",18,"bold"), bg=NAVY, fg=WHITE).pack(anchor="w")
        tk.Label(tf, text="Tell us a little about yourself to get started.",
                 font=("Segoe UI",10), bg=NAVY, fg=AQUA).pack(anchor="w")

        # Form — aqua background
        form = tk.Frame(self, bg=AQUA)
        form.pack(fill="both", expand=True, padx=40, pady=22)

        self._fv,self._fe = self._field(form, "First name", "e.g. Rutvij")
        self._lv,self._le = self._field(form, "Last name",  "e.g. Pathak")
        self._ev,self._ee = self._field(form, "Email address", "e.g. rutvij@email.com")

        # Heard about
        tk.Label(form, text="Where did you hear about Memora?",
                 font=("Segoe UI",11,"bold"), bg=AQUA, fg=NAVY).pack(
                 anchor="w", pady=(12,4))
        self._hv = tk.StringVar(value=HEARD_OPTIONS[0])
        cb = ttk.Combobox(form, textvariable=self._hv,
                          values=HEARD_OPTIONS, state="readonly",
                          font=("Segoe UI",11))
        cb.pack(fill="x", ipady=5)

        # Error
        self._err = tk.StringVar(value="")
        tk.Label(form, textvariable=self._err, font=("Segoe UI",10),
                 bg=AQUA, fg=DANGER).pack(anchor="w", pady=(6,0))

        # Buttons
        btn_row = tk.Frame(form, bg=AQUA)
        btn_row.pack(anchor="w", pady=(6,0))
        self.sub_btn = btn(btn_row, "  Get started  →",
                           self._submit, "gold", padx=24, pady=11)
        self.sub_btn.pack(side="left")

        skip = tk.Label(form, text="Skip for now",
                        font=("Segoe UI",10,"underline"),
                        bg=AQUA, fg=TEAL, cursor="hand2")
        skip.pack(anchor="w", pady=(10,0))
        skip.bind("<Button-1>", lambda e: self._skip())

        # Teal bottom strip
        tk.Frame(self, bg=TEAL, height=3).pack(fill="x", side="bottom")

    def _field(self, parent, label, ph):
        tk.Label(parent, text=label, font=("Segoe UI",11,"bold"),
                 bg=AQUA, fg=NAVY).pack(anchor="w", pady=(10,4))
        var = tk.StringVar()
        e = tk.Entry(parent, textvariable=var, font=("Segoe UI",11),
                     fg=NAVY, bg=OFF_WHITE, relief="flat", bd=0,
                     insertbackground=NAVY,
                     highlightbackground=AQUA2,
                     highlightthickness=1,
                     highlightcolor=TEAL)
        e.pack(fill="x", ipady=6)
        e.insert(0, ph); e.configure(fg=TEXT3)
        e._ph = ph
        def fi(ev):
            if e.get()==e._ph: e.delete(0,"end"); e.configure(fg=NAVY)
        def fo(ev):
            if not e.get(): e.insert(0,e._ph); e.configure(fg=TEXT3)
        e.bind("<FocusIn>",fi); e.bind("<FocusOut>",fo)
        return var, e

    def _val(self,var,entry):
        v=var.get().strip()
        return "" if v==entry._ph else v

    def _submit(self):
        first=self._val(self._fv,self._fe)
        last =self._val(self._lv,self._le)
        email=self._val(self._ev,self._ee)
        heard=self._hv.get()
        if not first: self._err.set("Please enter your first name."); return
        if not last:  self._err.set("Please enter your last name."); return
        if not email or "@" not in email or "." not in email:
            self._err.set("Please enter a valid email address."); return
        if heard==HEARD_OPTIONS[0]:
            self._err.set("Please select where you heard about Memora."); return
        self._err.set("")
        self.sub_btn.configure(state="disabled",text="Saving…",bg=TEAL)
        self.update_idletasks()
        send_to_sheets({"first_name":first,"last_name":last,"email":email,
                        "heard_from":heard,"version":"3.0",
                        "platform":sys.platform,
                        "timestamp":datetime.now().isoformat()})
        mark_registered(); self.destroy()

    def _skip(self):
        mark_registered(); self.destroy()

# ── Main App ──────────────────────────────────────────────────────────────────
class Memora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memora — Smart Photo Curator")
        self.configure(bg=AQUA)
        self.geometry("1040x700")
        self.minsize(880,620)
        _set_icon(self)

        self.folders   = []
        self.out_dir   = tk.StringVar()
        self.count_var = tk.StringVar(value="200")
        self.sharp_var = tk.DoubleVar(value=0.0)
        self.dedup_var = tk.IntVar(value=8)
        self.prog_var  = tk.DoubleVar(value=0)
        self.stage_var = tk.StringVar(value="")
        self.status_var= tk.StringVar(value="")
        self.etr_var   = tk.StringVar(value="")
        self.selected  = []
        self._removed  = set()
        self._trefs    = []
        self._stats    = {}
        self.running   = False

        self._styles(); self._build(); self._go("home")

    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("M.Horizontal.TProgressbar",
                    background=TEAL, troughcolor=AQUA2,
                    bordercolor=AQUA2, lightcolor=TEAL,
                    darkcolor=TEAL, thickness=7)
        s.configure("TScrollbar", background=AQUA2,
                    troughcolor=AQUA, bordercolor=AQUA,
                    arrowcolor=TEAL)
        s.configure("TCombobox", fieldbackground=OFF_WHITE,
                    background=OFF_WHITE, foreground=NAVY,
                    selectbackground=TEAL, selectforeground=WHITE)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build(self):
        self.sb = tk.Frame(self, bg=SB_BG, width=216)
        self.sb.pack(side="left", fill="y")
        self.sb.pack_propagate(False)

        # Gold top accent line
        tk.Frame(self.sb, bg=GOLD, height=3).pack(fill="x")

        # Logo area
        lf = tk.Frame(self.sb, bg=SB_BG)
        lf.pack(fill="x", padx=20, pady=(18,6))
        try:
            pil = _icon_img().resize((36,36), Image.LANCZOS)
            self._sb_ico = ImageTk.PhotoImage(pil)
            tk.Label(lf, image=self._sb_ico, bg=SB_BG).pack(side="left", padx=(0,10))
        except: pass
        tf = tk.Frame(lf, bg=SB_BG)
        tf.pack(side="left")
        tk.Label(tf, text="memora", font=("Segoe UI",17,"bold"),
                 bg=SB_BG, fg=WHITE).pack(anchor="w")
        tk.Label(tf, text="photo curator", font=("Segoe UI",9),
                 bg=SB_BG, fg=SB_SUB).pack(anchor="w")

        # Aqua divider
        tk.Frame(self.sb, bg=AQUA, height=1).pack(fill="x", padx=16, pady=8)

        # Nav
        self._nbtns = {}
        for key,label in [("home","Home"),("select","Add photos"),
                           ("review","Review"),("export","Export")]:
            self._nbtns[key] = self._nitem(key, label)

        tk.Label(self.sb, text="v3.0  ·  Rutvij Pathak",
                 font=("Segoe UI",9), bg=SB_BG, fg="#3A6070").pack(
                 side="bottom", pady=12)

        # Teal bottom accent
        tk.Frame(self.sb, bg=TEAL, height=3).pack(side="bottom", fill="x")

        self.content = tk.Frame(self, bg=AQUA)
        self.content.pack(side="left", fill="both", expand=True)
        self.screens = {
            "home":   self._home(),
            "select": self._select(),
            "review": self._review(),
            "export": self._export(),
        }

    def _nitem(self, key, label):
        f = tk.Frame(self.sb, bg=SB_BG, cursor="hand2")
        f.pack(fill="x", padx=10, pady=2)
        inner = tk.Frame(f, bg=SB_BG)
        inner.pack(fill="x", padx=6, pady=2)
        lbl = tk.Label(inner, text=f"  {label}", font=("Segoe UI",11),
                       bg=SB_BG, fg=SB_TXT, anchor="w")
        lbl.pack(fill="x", padx=8, pady=8)
        for w in [f,inner,lbl]:
            w.bind("<Button-1>", lambda e,k=key: self._go(k))
        return {"f":f,"i":inner,"l":lbl}

    def _go(self, key):
        for s in self.screens.values(): s.pack_forget()
        self.screens[key].pack(fill="both", expand=True)
        for k,nb in self._nbtns.items():
            active = k==key
            bg = SB_ACT_BG if active else SB_BG
            fg = SB_ACT_FG if active else SB_TXT
            nb["f"].configure(bg=bg)
            nb["i"].configure(bg=bg)
            nb["l"].configure(bg=bg, fg=fg,
                font=("Segoe UI",11,"bold") if active else ("Segoe UI",11))
            nb["f"].configure(
                highlightbackground=GOLD if active else SB_BG,
                highlightthickness=2 if active else 0)

    # ── Home ──────────────────────────────────────────────────────────────────
    def _home(self):
        f = tk.Frame(self.content, bg=AQUA)

        # Hero — navy with gold strip
        hero = tk.Frame(f, bg=NAVY, height=148)
        hero.pack(fill="x")
        hero.pack_propagate(False)
        tk.Frame(hero, bg=GOLD, height=4).pack(fill="x", side="bottom")
        tk.Label(hero, text="Welcome to Memora",
                 font=("Segoe UI",20,"bold"), bg=NAVY, fg=WHITE).pack(
                 anchor="w", padx=38, pady=(32,3))
        tk.Label(hero,
                 text="Turn thousands of ceremony photos into a perfect album — automatically.",
                 font=("Segoe UI",11), bg=NAVY, fg=AQUA).pack(anchor="w", padx=38)

        body = tk.Frame(f, bg=AQUA)
        body.pack(fill="both", expand=True, padx=34, pady=22)

        tk.Label(body, text="How it works",
                 font=("Segoe UI",11,"bold"),
                 bg=AQUA, fg=TEAL).pack(anchor="w", pady=(0,12))

        row = tk.Frame(body, bg=AQUA)
        row.pack(fill="x")
        steps = [
            ("1", NAVY,  GOLD, "Add photos",  "Add all ceremony folders at once"),
            ("2", GOLD,  TEAL, "AI analyses", "Scores clarity, emotion & composition"),
            ("3", TEAL,  GOLD, "Review",       "Browse results, remove any you dislike"),
            ("4", NAVY,  TEAL, "Export",       "Numbered photos, album-ready"),
        ]
        for i,(num,fg,strip,title,desc) in enumerate(steps):
            c = tk.Frame(row, bg=OFF_WHITE,
                         highlightbackground=AQUA2, highlightthickness=1)
            c.pack(side="left", fill="both",
                   expand=True, padx=(0,10 if i<3 else 0))
            tk.Frame(c, bg=strip, height=4).pack(fill="x")
            tk.Label(c, text=num, font=("Segoe UI",18,"bold"),
                     bg=OFF_WHITE, fg=fg).pack(anchor="w", padx=14, pady=(12,3))
            tk.Label(c, text=title, font=F_BOLD,
                     bg=OFF_WHITE, fg=NAVY).pack(anchor="w", padx=14)
            tk.Label(c, text=desc, font=F_SMALL,
                     bg=OFF_WHITE, fg=TEXT2, wraplength=150,
                     justify="left").pack(anchor="w", padx=14, pady=(3,14))

        cta = tk.Frame(body, bg=AQUA)
        cta.pack(anchor="w", pady=18)
        btn(cta, "  Get started →",
            lambda: self._go("select"),
            "gold", padx=26, pady=11).pack(side="left")

        tk.Frame(body, bg=AQUA2, height=1).pack(fill="x", pady=(4,12))
        stats = tk.Frame(body, bg=AQUA)
        stats.pack(fill="x")
        for val,lbl in [("6,000+","photos per ceremony"),
                        ("100%","private & offline"),
                        ("20+ formats","JPG PNG HEIC RAW + more")]:
            s = tk.Frame(stats, bg=AQUA)
            s.pack(side="left", padx=(0,34))
            tk.Label(s, text=val, font=("Segoe UI",15,"bold"),
                     bg=AQUA, fg=NAVY).pack(anchor="w")
            tk.Label(s, text=lbl, font=F_SMALL,
                     bg=AQUA, fg=TEXT2).pack(anchor="w")
        return f

    # ── Select ────────────────────────────────────────────────────────────────
    def _select(self):
        outer = tk.Frame(self.content, bg=AQUA)

        ph = tk.Frame(outer, bg=AQUA)
        ph.pack(fill="x", padx=34, pady=(24,0))
        tk.Label(ph, text="Add photos", font=("Segoe UI",16,"bold"),
                 bg=AQUA, fg=NAVY).pack(side="left")
        tk.Frame(outer, bg=AQUA2, height=1).pack(fill="x", padx=34, pady=11)

        cols = tk.Frame(outer, bg=AQUA)
        cols.pack(fill="both", expand=True, padx=34)

        # Left col
        left = tk.Frame(cols, bg=AQUA)
        left.pack(side="left", fill="both", expand=True, padx=(0,14))

        # Folders card
        fc = card_frame(left, bg=OFF_WHITE)
        fc.pack(fill="x", pady=(0,10))
        fh = tk.Frame(fc, bg=OFF_WHITE)
        fh.pack(fill="x", padx=16, pady=(14,7))
        tk.Label(fh, text="Ceremony folders", font=F_BOLD,
                 bg=OFF_WHITE, fg=NAVY).pack(side="left")
        tip_btn(fh,
            "Add one or more folders containing your photos.\n\n"
            "Add all ceremonies at once:\n"
            "Haldi, Shadi, Bidai, Mehendi etc.\n\n"
            "Supported: JPG PNG HEIC WEBP BMP TIFF GIF\n"
            "RAW: CR2 CR3 NEF ARW DNG ORF and more",
            bg=OFF_WHITE).pack(side="left", padx=(6,0))
        btn(fh, "+ Add folder", self._add_folder,
            "outline", padx=12, pady=6, font=F_SMALL).pack(side="right")
        self._flist = tk.Frame(fc, bg=OFF_WHITE)
        self._flist.pack(fill="x", padx=16, pady=(0,14))
        self._render_folders()

        # Format pills card
        fmt = card_frame(left, bg=OFF_WHITE)
        fmt.pack(fill="x")
        tk.Label(fmt, text="Supported formats",
                 font=("Segoe UI",10,"bold"),
                 bg=OFF_WHITE, fg=NAVY).pack(anchor="w", padx=16, pady=(10,4))
        r1 = tk.Frame(fmt, bg=OFF_WHITE); r1.pack(anchor="w", padx=16, pady=(0,3))
        r2 = tk.Frame(fmt, bg=OFF_WHITE); r2.pack(anchor="w", padx=16, pady=(0,10))
        for ext in ["JPG","PNG","HEIC","WEBP","BMP","TIFF","GIF"]:
            tk.Label(r1, text=ext, font=("Segoe UI",9),
                     bg=TEAL_LITE, fg=TEAL, padx=7, pady=3,
                     relief="flat").pack(side="left", padx=(0,4))
        for ext in ["CR2","CR3","NEF","ARW","DNG","ORF","RW2","RAF"]:
            tk.Label(r2, text=ext, font=("Segoe UI",9),
                     bg=GOLD_LITE, fg=GOLD2, padx=7, pady=3,
                     relief="flat").pack(side="left", padx=(0,4))

        # Right col
        right = tk.Frame(cols, bg=AQUA, width=272)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        # Output folder card
        oc = card_frame(right, bg=OFF_WHITE)
        oc.pack(fill="x", pady=(0,10))
        oh = tk.Frame(oc, bg=OFF_WHITE)
        oh.pack(fill="x", padx=14, pady=(13,5))
        tk.Label(oh, text="Save selection to",
                 font=("Segoe UI",11,"bold"), bg=OFF_WHITE, fg=NAVY).pack(side="left")
        tip_btn(oh,
            "Where Memora copies your selected photos.\n\n"
            "Folder created automatically.\n"
            "Originals are NEVER moved or deleted.",
            bg=OFF_WHITE).pack(side="left", padx=(5,0))
        tk.Label(oc, textvariable=self.out_dir, font=F_MONO,
                 bg=OFF_WHITE, fg=TEAL, wraplength=238, justify="left").pack(
                 anchor="w", padx=14, pady=(0,4))
        btn(oc, "Browse…", self._browse_out,
            "secondary", padx=12, pady=6, font=F_SMALL).pack(
            anchor="w", padx=14, pady=(0,12))

        # Photo count card
        cc = card_frame(right, bg=OFF_WHITE)
        cc.pack(fill="x", pady=(0,10))
        ch = tk.Frame(cc, bg=OFF_WHITE)
        ch.pack(fill="x", padx=14, pady=(13,6))
        tk.Label(ch, text="Photos to select",
                 font=("Segoe UI",11,"bold"), bg=OFF_WHITE, fg=NAVY).pack(side="left")
        tip_btn(ch,
            "How many photos in your final album?\n\n"
            "50–100   Small highlights\n"
            "200       Standard photo book\n"
            "500+     Large detailed album",
            bg=OFF_WHITE).pack(side="left", padx=(5,0))
        cnt = tk.Frame(cc, bg=OFF_WHITE)
        cnt.pack(padx=14, pady=(0,6))
        btn(cnt,"−",lambda:self._adj(-50),"secondary",padx=9,pady=5,
            font=F_BOLD).pack(side="left")
        tk.Entry(cnt, textvariable=self.count_var,
                 font=("Segoe UI",18,"bold"),
                 fg=NAVY, bg=OFF_WHITE, width=6,
                 justify="center", relief="flat",
                 highlightbackground=AQUA2,
                 highlightthickness=1).pack(side="left", padx=6)
        btn(cnt,"+",lambda:self._adj(50),"secondary",padx=9,pady=5,
            font=F_BOLD).pack(side="left")
        pre = tk.Frame(cc, bg=OFF_WHITE)
        pre.pack(padx=14, pady=(0,12))
        for v in [50,100,200,500,1000]:
            tk.Button(pre, text=str(v), font=("Segoe UI",9),
                      bg=TEAL_LITE, fg=TEAL, relief="flat",
                      padx=7, pady=3, cursor="hand2",
                      command=lambda x=v: self.count_var.set(str(x))
                      ).pack(side="left", padx=2)

        # Settings card
        sc = card_frame(right, bg=OFF_WHITE)
        sc.pack(fill="x")
        tk.Label(sc, text="Advanced settings",
                 font=("Segoe UI",11,"bold"),
                 bg=OFF_WHITE, fg=NAVY).pack(anchor="w", padx=14, pady=(13,6))
        self._srow(sc, "Sharpness filter", self.sharp_var, 0, 300,
            "Removes blurry photos.\n\n"
            "0  → Keep all (best for portrait mode)\n"
            "50–100  → Remove clearly blurry shots\n"
            "200+  → Very strict\n\n"
            "Portrait mode has intentional blur —\nset to 0 to keep those photos.")
        self._srow(sc, "Duplicate removal", self.dedup_var, 1, 20,
            "How aggressively burst shots are removed.\n\n"
            "1–5  → Very strict\n"
            "8  → Balanced (recommended)\n"
            "15–20  → Relaxed, keeps more variations")

        # Action bar
        tk.Frame(outer, bg=AQUA2, height=1).pack(fill="x", padx=34, pady=(12,0))
        bot = tk.Frame(outer, bg=AQUA)
        bot.pack(fill="x", padx=34, pady=12)
        self.analyse_btn = btn(bot, "  ✦  Analyse & select photos",
                               self._start, "gold", padx=22, pady=11)
        self.analyse_btn.pack(side="left")
        btn(bot, "↩  Start over", self._undo, "secondary",
            padx=13, pady=11).pack(side="left", padx=(9,0))
        tip_btn(bot,
            "Clears results and lets you start again.\n"
            "Your original photos are never deleted.").pack(
            side="left", padx=(6,0))

        # Progress
        prog = tk.Frame(outer, bg=AQUA)
        prog.pack(fill="x", padx=34, pady=(0,12))
        tk.Label(prog, textvariable=self.stage_var,
                 font=("Segoe UI",11,"bold"),
                 bg=AQUA, fg=NAVY).pack(anchor="w")
        ttk.Progressbar(prog, variable=self.prog_var, maximum=100,
                        style="M.Horizontal.TProgressbar",
                        length=400).pack(fill="x", pady=(3,2))
        sr = tk.Frame(prog, bg=AQUA)
        sr.pack(fill="x")
        tk.Label(sr, textvariable=self.status_var, font=F_SMALL,
                 bg=AQUA, fg=TEXT2).pack(side="left")
        tk.Label(sr, textvariable=self.etr_var, font=F_SMALL,
                 bg=AQUA, fg=GOLD).pack(side="right")
        return outer

    def _srow(self, parent, label, var, lo, hi, tooltip):
        row = tk.Frame(parent, bg=OFF_WHITE)
        row.pack(fill="x", padx=14, pady=(0,10))
        lr = tk.Frame(row, bg=OFF_WHITE)
        lr.pack(fill="x")
        tk.Label(lr, text=label, font=F_TINY,
                 bg=OFF_WHITE, fg=TEXT2).pack(side="left")
        tip_btn(lr, tooltip, bg=OFF_WHITE).pack(side="left", padx=(4,0))
        vl = tk.Label(lr, text=str(int(var.get())),
                      font=F_TINY, bg=OFF_WHITE, fg=NAVY, width=4)
        vl.pack(side="right")
        ttk.Scale(row, from_=lo, to=hi, variable=var,
                  orient="horizontal",
                  command=lambda v,l=vl:
                      l.configure(text=str(int(float(v))))).pack(
                  fill="x", pady=(2,0))

    def _add_folder(self):
        p = filedialog.askdirectory(title="Select ceremony folder")
        if p and p not in self.folders:
            self.folders.append(p)
            self._render_folders()
            if not self.out_dir.get():
                self.out_dir.set(str(Path.home()/"Desktop"/"Memora Album"))

    def _render_folders(self):
        for w in self._flist.winfo_children(): w.destroy()
        if not self.folders:
            tk.Label(self._flist, text="No folders added yet.",
                     font=F_SMALL, bg=OFF_WHITE, fg=TEXT3).pack(anchor="w", pady=4)
            return
        for p in self.folders:
            try:
                n = sum(1 for x in Path(p).rglob("*")
                        if x.suffix.lower() in IMAGE_EXT)
            except: n=0
            row = tk.Frame(self._flist, bg=TEAL_LITE,
                           highlightbackground=AQUA2, highlightthickness=1)
            row.pack(fill="x", pady=2)
            lf = tk.Frame(row, bg=TEAL_LITE)
            lf.pack(side="left", fill="both", expand=True, padx=10, pady=7)
            tk.Label(lf, text=f"  {Path(p).name}",
                     font=F_BOLD, bg=TEAL_LITE, fg=NAVY).pack(anchor="w")
            tk.Label(lf, text=f"{n:,} photos  ·  {p}",
                     font=F_TINY, bg=TEAL_LITE, fg=TEXT2).pack(anchor="w")
            tk.Button(row, text="✕", font=F_TINY,
                      bg=TEAL_LITE, fg=DANGER, relief="flat",
                      cursor="hand2",
                      command=lambda x=p: self._del_folder(x)).pack(
                      side="right", padx=8)

    def _del_folder(self,p):
        self.folders.remove(p); self._render_folders()

    def _browse_out(self):
        p = filedialog.askdirectory(title="Save selection to…")
        if p: self.out_dir.set(p)

    def _adj(self,d):
        try: self.count_var.set(str(max(10,int(self.count_var.get())+d)))
        except: self.count_var.set("200")

    def _undo(self):
        if self.running:
            messagebox.showwarning("Memora","Please wait for analysis to finish.")
            return
        if messagebox.askyesno("Start over?",
            "Clear current results and start again?\n\nYour original photos are never deleted."):
            self.selected=[]; self._removed=set(); self._stats={}
            self.prog_var.set(0)
            self.stage_var.set(""); self.status_var.set(""); self.etr_var.set("")
            self._go("select")

    def _upd(self,stage,status,pct=None,etr=""):
        self.stage_var.set(stage); self.status_var.set(status)
        self.etr_var.set(etr)
        if pct is not None: self.prog_var.set(pct)
        self.update_idletasks()

    def _start(self):
        if not self.folders:
            messagebox.showwarning("Memora","Please add at least one folder first.")
            return
        if not self.out_dir.get():
            messagebox.showwarning("Memora","Please choose an output folder.")
            return
        try:
            t=int(self.count_var.get())
            if t<1: raise ValueError
        except:
            messagebox.showwarning("Memora","Please enter a valid photo count.")
            return
        if self.running: return
        self.running=True
        self.analyse_btn.configure(state="disabled",text="Analysing…",bg=AQUA_DEEP)
        threading.Thread(target=self._run,daemon=True).start()

    def _run(self):
        try:
            target=int(self.count_var.get())
            ms=float(self.sharp_var.get())
            dt=int(self.dedup_var.get())

            self._upd("Stage 1 of 5  ·  Scanning folders","Finding all photos…",2)
            all_files=[]
            for folder in self.folders:
                all_files.extend(str(p) for p in Path(folder).rglob("*")
                                 if p.suffix.lower() in IMAGE_EXT)
            total=len(all_files)
            self._upd("Stage 1 of 5  ·  Scanning folders",
                      f"Found {total:,} photos across {len(self.folders)} folder(s).",4)
            time.sleep(0.3)

            if total==0:
                self.after(0,lambda: messagebox.showwarning(
                    "Memora","No photos found in selected folders."))
                self.running=False; self.after(0,self._reset_btn); return

            results=[]; failed=0
            etr=ETR(total)
            self._upd("Stage 2 of 5  ·  Analysing quality",
                      f"0 of {total:,}…",5,"Estimating…")
            for i,path in enumerate(all_files):
                info=analyse(path)
                if info: results.append(info)
                else: failed+=1
                etr.update(i+1)
                if i%40==0:
                    pct=5+int((i/max(total,1))*25)
                    self._upd("Stage 2 of 5  ·  Analysing quality",
                              f"{i+1:,} of {total:,} analysed"
                              +(f" ({failed} unreadable)" if failed else ""),
                              pct,etr.text())

            if not results:
                self.after(0,lambda: messagebox.showerror(
                    "Memora",
                    "Could not read any photos.\n\n"
                    "Supported: JPG PNG HEIC WEBP TIFF BMP GIF\n"
                    "RAW: CR2 CR3 NEF ARW DNG and more\n\n"
                    "Try copying photos to Desktop first."))
                self.running=False; self.after(0,self._reset_btn); return

            self._upd("Stage 3 of 5  ·  Scoring emotions",
                      "Analysing happiness in photos…",32)
            if DEEPFACE_OK:
                etr2=ETR(len(results))
                for i,info in enumerate(results):
                    info["emo"]=emo_score(info["path"]); etr2.update(i+1)
                    if i%25==0:
                        pct=32+int((i/max(len(results),1))*18)
                        self._upd("Stage 3 of 5  ·  Scoring emotions",
                                  f"{i+1:,} of {len(results):,} scored…",
                                  pct,etr2.text())
            else:
                self._upd("Stage 3 of 5  ·  Scoring emotions",
                          "DeepFace not available — using quality scoring only.",50)
                time.sleep(0.3)

            self._upd("Stage 4 of 5  ·  Removing duplicates",
                      f"Scoring {len(results):,} photos…",53)
            for r in results: r["_score"]=score(r)
            before=len(results)
            filtered=([r for r in results if r["sharp"]>=ms] if ms>0 else results[:])
            if not filtered: filtered=results[:]
            removed_blur=before-len(filtered)
            unique=dedup(filtered,dt)
            removed_dupe=len(filtered)-len(unique)
            self._upd("Stage 4 of 5  ·  Removing duplicates",
                      f"Kept {len(unique):,} unique moments ({removed_dupe:,} removed).",72)
            time.sleep(0.2)

            self._upd("Stage 5 of 5  ·  Selecting best photos",
                      f"Picking {target} photos with timeline diversity…",78)
            self.selected=diverse(unique,min(target,len(unique)))
            self._stats={"total":total,"folders":len(self.folders),
                         "removed_blur":removed_blur,"removed_dupe":removed_dupe,
                         "selected":len(self.selected),
                         "emo_used":DEEPFACE_OK,"raw_supported":RAWPY_OK}
            self._upd("Complete  ✓",
                      f"{len(self.selected):,} photos selected from {total:,} originals.",
                      100,"Done!")
            self.after(0,self._done)

        except Exception as e:
            self.after(0,lambda: messagebox.showerror("Memora — Error",str(e)))
            self.running=False; self.after(0,self._reset_btn)

    def _reset_btn(self):
        self.analyse_btn.configure(state="normal",
                                    text="  ✦  Analyse & select photos",bg=GOLD)

    def _done(self):
        self.running=False; self._reset_btn()
        self._build_grid(); self._update_stats(); self._go("review")

    # ── Review ────────────────────────────────────────────────────────────────
    def _review(self):
        f = tk.Frame(self.content, bg=AQUA)
        hdr = tk.Frame(f, bg=AQUA)
        hdr.pack(fill="x", padx=34, pady=(24,0))
        tk.Label(hdr, text="Review selection",
                 font=("Segoe UI",16,"bold"), bg=AQUA, fg=NAVY).pack(side="left")
        self.rev_count = tk.Label(hdr, text="", font=F_SMALL, bg=AQUA, fg=TEAL)
        self.rev_count.pack(side="left", padx=10)
        hr = tk.Frame(f, bg=AQUA)
        hr.pack(fill="x", padx=34, pady=(3,0))
        tk.Label(hr,
                 text="Click any photo to remove it  ·  Click again to restore",
                 font=F_SMALL, bg=AQUA, fg=TEXT2).pack(side="left")
        tip_btn(hr,
            "Removed photos are greyed out but never deleted.\n"
            "Click again to restore them.\n\n"
            "Hover over any photo to see its quality score.").pack(
            side="left", padx=(8,0))
        tk.Frame(f, bg=AQUA2, height=1).pack(fill="x", padx=34, pady=9)
        self.rev_scroll = Scroller(f, bg=AQUA)
        self.rev_scroll.pack(fill="both", expand=True, padx=34)
        self.thumb_frame = self.rev_scroll.inner
        btm = tk.Frame(f, bg=AQUA)
        btm.pack(fill="x", padx=34, pady=12)
        btn(btm, "Export selected photos  →",
            lambda: self._go("export"), "gold", padx=20, pady=10).pack(side="left")
        btn(btm, "↩  Change settings", self._undo, "secondary",
            padx=13, pady=10).pack(side="left", padx=(9,0))
        return f

    def _build_grid(self):
        for w in self.thumb_frame.winfo_children(): w.destroy()
        self._trefs=[]; self._removed=set()
        COLS,SZ=7,108
        self.rev_count.configure(text=f"{len(self.selected)} photos")
        for i,photo in enumerate(self.selected):
            try:
                img=Image.open(photo["path"]); img.thumbnail((SZ,SZ))
                tkimg=ImageTk.PhotoImage(img)
            except: tkimg=None
            self._trefs.append(tkimg)
            r,c=divmod(i,COLS)
            cell=tk.Frame(self.thumb_frame, bg=AQUA,
                          highlightbackground=AQUA2,
                          highlightthickness=2, cursor="hand2")
            cell.grid(row=r, column=c, padx=3, pady=3)
            if tkimg:
                lbl=tk.Label(cell, image=tkimg, bg=AQUA, cursor="hand2")
                lbl.pack(padx=2, pady=2)
            else:
                lbl=tk.Label(cell, text="?", bg=TEAL_LITE,
                             width=11, height=6, cursor="hand2")
                lbl.pack()
            sv=photo.get("_score",0); ev=photo.get("emo",0); fv=photo.get("faces",0)
            tk.Label(cell, text=f"★{sv:.1f}",
                     font=("Segoe UI",9), bg=AQUA, fg=GOLD).pack()
            Tip(lbl,
                f"Quality score:  {sv:.2f}\n"
                f"Happiness:      {ev:.0%}\n"
                f"Faces:          {fv}\n"
                f"Sharpness:      {photo.get('sharp',0):.0f}\n"
                f"Resolution:     {photo.get('mp',0):.1f} MP\n\n"
                f"Click to remove.")
            lbl.bind("<Button-1>",
                     lambda e,idx=i,ce=cell,lb=lbl: self._toggle(idx,ce,lb))
        self.rev_scroll.canvas.update_idletasks()
        self.rev_scroll.canvas.configure(
            scrollregion=self.rev_scroll.canvas.bbox("all"))

    def _toggle(self,idx,cell,lbl):
        if idx in self._removed:
            self._removed.discard(idx)
            cell.configure(bg=AQUA, highlightbackground=AQUA2)
            lbl.configure(bg=AQUA)
        else:
            self._removed.add(idx)
            cell.configure(bg=TEAL_LITE, highlightbackground=TEAL_LITE)
            lbl.configure(bg=TEAL_LITE)
        self.rev_count.configure(
            text=f"{len(self.selected)-len(self._removed)} photos")

    # ── Export ────────────────────────────────────────────────────────────────
    def _export(self):
        f = tk.Frame(self.content, bg=AQUA)
        tk.Label(f, text="Export", font=("Segoe UI",16,"bold"),
                 bg=AQUA, fg=NAVY).pack(anchor="w", padx=34, pady=(24,0))
        tk.Frame(f, bg=AQUA2, height=1).pack(fill="x", padx=34, pady=13)
        self.stats_frame = tk.Frame(f, bg=AQUA)
        self.stats_frame.pack(fill="x", padx=34, pady=(0,14))
        br = tk.Frame(f, bg=AQUA)
        br.pack(fill="x", padx=34, pady=(0,6))
        self.exp_btn = btn(br, "  📋  Copy photos to output folder",
                           self._do_export, "gold", padx=22, pady=11)
        self.exp_btn.pack(side="left")
        tip_btn(br,
            "Copies selected photos to the output folder.\n\n"
            "Photos are numbered (001_, 002_…) to keep album order.\n\n"
            "Your ORIGINAL photos are never moved or deleted.").pack(
            side="left", padx=(8,0))
        self.open_btn = btn(f, "  📂  Open output folder",
                            self._open_out, "secondary", padx=16, pady=9)
        self.open_btn.pack(anchor="w", padx=34, pady=(0,6))
        self.open_btn.configure(state="disabled")
        self.exp_status = tk.Label(f, text="",
                                    font=("Segoe UI",12,"bold"),
                                    bg=AQUA, fg=NAVY)
        self.exp_status.pack(anchor="w", padx=34, pady=4)
        tk.Frame(f, bg=AQUA2, height=1).pack(fill="x", padx=34, pady=13)
        btn(f, "↩  Change settings & run again",
            self._undo, "secondary", padx=14, pady=9).pack(anchor="w", padx=34)
        return f

    def _update_stats(self):
        for w in self.stats_frame.winfo_children(): w.destroy()
        s=self._stats; kept=len(self.selected)-len(self._removed)
        items=[
            ("Folders scanned",    str(s.get("folders",0))),
            ("Total photos found", f"{s.get('total',0):,}"),
            ("Blurry removed",     f"{s.get('removed_blur',0):,}"),
            ("Duplicates removed", f"{s.get('removed_dupe',0):,}"),
            ("Emotion scoring",    "✓ Active" if s.get("emo_used") else "— Not available"),
            ("RAW support",        "✓ Active" if s.get("raw_supported") else "— Install rawpy"),
            ("Final selection",    f"{kept:,}"),
        ]
        g=tk.Frame(self.stats_frame,bg=AQUA); g.pack(fill="x")
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        for i,(label,value) in enumerate(items):
            row=card_frame(g,bg=OFF_WHITE)
            row.grid(row=i//2,column=i%2,sticky="ew",
                     padx=(0,8) if i%2==0 else 0,pady=3)
            tk.Label(row,text=label,font=F_SMALL,
                     bg=OFF_WHITE,fg=TEXT2,anchor="w").pack(side="left",padx=14,pady=9)
            fg=GOLD if label=="Final selection" else NAVY
            tk.Label(row,text=value,font=F_BOLD,
                     bg=OFF_WHITE,fg=fg).pack(side="right",padx=14)

    def _do_export(self):
        out=Path(self.out_dir.get()); out.mkdir(parents=True,exist_ok=True)
        kept=[p for i,p in enumerate(self.selected) if i not in self._removed]
        if not kept:
            messagebox.showwarning("Memora","No photos to export."); return
        self.exp_btn.configure(state="disabled",text="Exporting…",bg=AQUA_DEEP)
        self.exp_status.configure(text="Copying photos…",fg=TEXT2)
        self.update_idletasks()
        for i,photo in enumerate(kept,1):
            src=Path(photo["path"])
            shutil.copy2(str(src),str(out/f"{i:03d}_{src.name}"))
        self.exp_status.configure(text=f"✓  Done!  {len(kept)} photos saved.",fg=NAVY)
        self.exp_btn.configure(state="normal",
                                text="  📋  Copy photos to output folder",bg=GOLD)
        self.open_btn.configure(state="normal")
        self._update_stats()

    def _open_out(self):
        folder=self.out_dir.get()
        if sys.platform=="darwin": os.system(f'open "{folder}"')
        elif sys.platform=="win32": os.startfile(folder)
        else: os.system(f'xdg-open "{folder}"')

# ── Launch ────────────────────────────────────────────────────────────────────

# ── Update checker + license gate ────────────────────────────────────────────

APP_VERSION  = "3.0.0"
CONFIG_URL   = (
    "https://raw.githubusercontent.com/"
    "YOUR_USERNAME/memora/main/config.json"
)

def _parse_version(v):
    """Convert '3.1.0' to (3, 1, 0) for comparison."""
    try:
        return tuple(int(x) for x in str(v).split("."))
    except Exception:
        return (0, 0, 0)

def fetch_config():
    """
    Fetches config.json from GitHub.
    Returns dict or None if offline / unreachable.
    """
    try:
        req = _req.Request(CONFIG_URL, headers={"Cache-Control":"no-cache"})
        with _req.urlopen(req, timeout=6) as resp:
            import json as _json
            return _json.loads(resp.read().decode())
    except Exception:
        return None


class UpdateGate(tk.Tk):
    """
    Shown on launch if:
    - A newer version is available (soft banner — can dismiss)
    - App has been set to paid and user hasn't paid (hard block)
    - Admin has sent a broadcast message
    - User's version is below min_version (forced update)
    """
    def __init__(self, config, on_continue):
        super().__init__()
        self.config_data = config
        self.on_continue = on_continue
        self.title("Memora")
        self.configure(bg=AQUA)
        self.resizable(False, False)
        _set_icon(self)

        latest    = config.get("version", APP_VERSION)
        min_ver   = config.get("min_version", "0.0.0")
        is_free   = config.get("is_free", True)
        dl_win    = config.get("download_win", "")
        dl_mac    = config.get("download_mac", "")
        message   = config.get("message", "").strip()

        # Determine situation
        is_newer     = _parse_version(latest) > _parse_version(APP_VERSION)
        is_too_old   = _parse_version(APP_VERSION) < _parse_version(min_ver)
        is_blocked   = not is_free
        hard_block   = is_too_old or is_blocked

        dl_url = dl_win if sys.platform == "win32" else dl_mac

        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        W = 500; H = 340 if hard_block else 300
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

        self._build(latest, is_newer, is_too_old, is_blocked,
                    hard_block, message, dl_url)

    def _build(self, latest, is_newer, is_too_old,
               is_blocked, hard_block, message, dl_url):

        # Banner colour depends on severity
        banner_col = DANGER if hard_block else NAVY
        strip_col  = GOLD   if hard_block else TEAL

        banner = tk.Frame(self, bg=banner_col, height=100)
        banner.pack(fill="x"); banner.pack_propagate(False)
        tk.Frame(banner, bg=strip_col, height=3).pack(fill="x", side="bottom")

        try:
            pil = _icon_img().resize((40,40), Image.LANCZOS)
            self._gi = ImageTk.PhotoImage(pil)
            top = tk.Frame(banner, bg=banner_col)
            top.pack(expand=True)
            tk.Label(top, image=self._gi, bg=banner_col).pack(
                side="left", padx=(0,12))
            tf = tk.Frame(top, bg=banner_col); tf.pack(side="left")
            tk.Label(tf, text="memora",
                     font=("Segoe UI",17,"bold"),
                     bg=banner_col, fg=WHITE).pack(anchor="w")
            tk.Label(tf, text=f"Your version: {APP_VERSION}   Latest: {latest}",
                     font=("Segoe UI",9),
                     bg=banner_col, fg=AQUA).pack(anchor="w")
        except Exception:
            pass

        body = tk.Frame(self, bg=AQUA)
        body.pack(fill="both", expand=True, padx=36, pady=18)

        # Broadcast message
        if message:
            tk.Label(body, text=f"📢  {message}",
                     font=("Segoe UI",11), bg=AQUA, fg=NAVY,
                     wraplength=420, justify="left").pack(
                     anchor="w", pady=(0,10))

        # Hard block — paid or forced update
        if is_blocked:
            tk.Label(body,
                     text="Memora is now a paid product.",
                     font=("Segoe UI",13,"bold"),
                     bg=AQUA, fg=NAVY).pack(anchor="w")
            tk.Label(body,
                     text="Thank you for being an early user! "
                          "To continue using Memora please purchase a license.",
                     font=("Segoe UI",11), bg=AQUA, fg=TEXT2,
                     wraplength=420, justify="left").pack(
                     anchor="w", pady=(4,14))
            btn(body, "  Purchase license →",
                lambda: self._open_url("https://YOUR_PAYMENT_LINK"),
                "gold", padx=20, pady=10).pack(anchor="w")
            tk.Label(body, text="Already purchased? Contact support@memora.app",
                     font=("Segoe UI",9), bg=AQUA, fg=TEXT3).pack(
                     anchor="w", pady=(8,0))

        elif is_too_old:
            tk.Label(body,
                     text=f"Please update to Memora {latest} to continue.",
                     font=("Segoe UI",13,"bold"),
                     bg=AQUA, fg=NAVY).pack(anchor="w")
            tk.Label(body,
                     text="This version is no longer supported. "
                          "Please download the latest version to continue.",
                     font=("Segoe UI",11), bg=AQUA, fg=TEXT2,
                     wraplength=420, justify="left").pack(
                     anchor="w", pady=(4,14))
            btn(body, f"  Download Memora {latest} →",
                lambda: self._open_url(dl_url),
                "gold", padx=20, pady=10).pack(anchor="w")

        # Soft banner — update available but not forced
        elif is_newer:
            tk.Label(body,
                     text=f"Memora {latest} is available!",
                     font=("Segoe UI",13,"bold"),
                     bg=AQUA, fg=NAVY).pack(anchor="w")
            tk.Label(body,
                     text="A new version with improvements is ready to download.",
                     font=("Segoe UI",11), bg=AQUA, fg=TEXT2,
                     wraplength=420).pack(anchor="w", pady=(3,14))
            btn_row = tk.Frame(body, bg=AQUA)
            btn_row.pack(anchor="w")
            btn(btn_row, f"  Download update →",
                lambda: self._open_url(dl_url),
                "gold", padx=20, pady=10).pack(side="left")
            btn(btn_row, "Skip for now",
                self._continue, "secondary",
                padx=16, pady=10).pack(side="left", padx=(10,0))

        # If only a message (no block, no update)
        else:
            self._continue()
            return

        if hard_block:
            # No continue option — close only quits
            tk.Button(body, text="Exit",
                      font=F_SMALL, bg=AQUA, fg=TEXT3,
                      relief="flat", cursor="hand2",
                      command=self.quit).pack(anchor="w", pady=(10,0))
        else:
            pass  # Skip button already shown above

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def _continue(self):
        self.destroy()
        self.on_continue()


if __name__ == "__main__":
    Splash().run()

    # Registration — first launch only
    if not is_registered():
        reg = Registration()
        reg.mainloop()

    # Check for updates + license gate (non-blocking if offline)
    config = fetch_config()
    if config:
        latest   = config.get("version", APP_VERSION)
        min_ver  = config.get("min_version", "0.0.0")
        is_free  = config.get("is_free", True)
        message  = config.get("message","").strip()
        is_newer = _parse_version(latest) > _parse_version(APP_VERSION)
        too_old  = _parse_version(APP_VERSION) < _parse_version(min_ver)
        blocked  = not is_free

        if is_newer or too_old or blocked or message:
            app_holder = []
            def launch_main():
                app_holder.append(Memora())
                app_holder[0].mainloop()
            gate = UpdateGate(config, launch_main)
            gate.mainloop()
            # If gate was dismissed (soft update), launch_main was called
            if not app_holder:
                pass  # hard blocked — already exited
        else:
            Memora().mainloop()
    else:
        # Offline — launch normally
        Memora().mainloop()

