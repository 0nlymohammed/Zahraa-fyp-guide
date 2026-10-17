# التجربة 7: الأرقام التي يطلبها التقرير - NPCR, UACI, Entropy, Correlation, حساسية المفتاح, السرعة
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt
import chaos

IMAGE = "photo.jpg"
MASTER_KEY = "zahraa-secret-2026"

img = cv2.imread(IMAGE)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)         # القياسات تُحسب عادة على صورة رمادية
x0, r = chaos.frame_key(MASTER_KEY, 0)
enc = chaos.encrypt(gray, x0, r)


def entropy(a):
    """كم بت من المعلومات في كل بكسل. الأعلى 8 = لا يمكن التنبؤ بأي شيء."""
    hist = np.bincount(a.ravel(), minlength=256) / a.size
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))


def correlation(a, direction, n=5000):
    """علاقة كل بكسل بجاره (أفقي/عمودي/قطري). قرب 1 = صورة طبيعية، قرب 0 = مشفرة جيداً."""
    rng = np.random.default_rng(0)
    H, W = a.shape
    ys = rng.integers(0, H - 1, n); xs = rng.integers(0, W - 1, n)
    dy, dx = {"horizontal": (0, 1), "vertical": (1, 0), "diagonal": (1, 1)}[direction]
    p = a[ys, xs].astype(float); q = a[ys + dy, xs + dx].astype(float)
    return float(np.corrcoef(p, q)[0, 1])


def npcr_uaci(c1, c2):
    """NPCR: نسبة البكسلات التي تغيرت. UACI: متوسط حجم التغير. المرجع النظري 99.61% و33.46%."""
    npcr = 100 * np.mean(c1 != c2)
    uaci = 100 * np.mean(np.abs(c1.astype(int) - c2.astype(int)) / 255)
    return npcr, uaci


# 1) تغيير بكسل واحد في الأصل -> كم يتغير المشفر؟ (مقاومة الهجوم التفاضلي)
gray2 = gray.copy()
gray2[10, 10] ^= 1                                    # نقلب أصغر بت في بكسل واحد
enc2 = chaos.encrypt(gray2, x0, r)
npcr, uaci = npcr_uaci(enc, enc2)

# 2) حساسية المفتاح: فك بمفتاح يختلف بمقدار 10^-10 فقط
wrong = chaos.decrypt(enc, x0 + 1e-10, r)
key_sens = 100 * np.mean(wrong != gray)

# 3) السرعة على فريم ملون 640x480 (مثل الكاميرا)
frame = cv2.resize(img, (640, 480))
chaos.encrypt(frame, x0, r)                           # أول نداء يجمّع numba، لا نحسبه
t = time.time()
for k in range(30):
    chaos.encrypt(frame, *chaos.frame_key(MASTER_KEY, k))
fps = 30 / (time.time() - t)

print("=" * 60)
print(f"{'Metric':34}{'Original':>12}{'Encrypted':>14}")
print("-" * 60)
print(f"{'Entropy (max 8)':34}{entropy(gray):>12.4f}{entropy(enc):>14.4f}")
for d in ("horizontal", "vertical", "diagonal"):
    print(f"{'Correlation ' + d:34}{correlation(gray, d):>12.4f}{correlation(enc, d):>14.4f}")
print("-" * 60)
print(f"{'NPCR (one-pixel change)':34}{npcr:>26.4f} %   (ideal 99.6094)")
print(f"{'UACI (one-pixel change)':34}{uaci:>26.4f} %   (ideal 33.4635)")
print(f"{'Key sensitivity (x0 + 1e-10)':34}{key_sens:>26.4f} %   (pixels different)")
print(f"{'Encryption speed 640x480 color':34}{fps:>26.1f} FPS")
print("=" * 60)

# رسم الهستوغرام والارتباط للتقرير
fig, ax = plt.subplots(2, 2, figsize=(10, 7))
ax[0, 0].hist(gray.ravel(), bins=256, color="gray"); ax[0, 0].set_title("Histogram - original")
ax[0, 1].hist(enc.ravel(), bins=256, color="gray");  ax[0, 1].set_title("Histogram - encrypted")
rng = np.random.default_rng(1); ys = rng.integers(0, gray.shape[0] - 1, 3000); xs = rng.integers(0, gray.shape[1] - 1, 3000)
ax[1, 0].scatter(gray[ys, xs], gray[ys, xs + 1], s=2); ax[1, 0].set_title("Adjacent pixels - original")
ax[1, 1].scatter(enc[ys, xs], enc[ys, xs + 1], s=2);   ax[1, 1].set_title("Adjacent pixels - encrypted")
plt.tight_layout(); plt.savefig("lab7_metrics.png", dpi=110); plt.show()
print("الرسم محفوظ باسم lab7_metrics.png")
