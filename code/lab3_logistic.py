# التجربة 3: شوفي الفوضى بعينك - معادلة logistic وحساسيتها للمفتاح
import numpy as np
import matplotlib.pyplot as plt


def logistic(x0, r, n):
    """ترجع قائمة بـ n قيمة من المعادلة x(n+1) = r * x(n) * (1 - x(n))"""
    xs = [x0]
    for _ in range(n - 1):
        xs.append(r * xs[-1] * (1 - xs[-1]))
    return xs


N = 60
fig, ax = plt.subplots(3, 1, figsize=(9, 10))

# (أ) نفس البداية x0 = 0.3 مع ثلاث قيم لـ r: ثابت، دوري، فوضوي
for r, label in [(2.8, "r = 2.8  (settles to one value)"),
                 (3.2, "r = 3.2  (repeats two values)"),
                 (3.99, "r = 3.99 (chaos: never repeats)")]:
    ax[0].plot(logistic(0.3, r, N), marker=".", label=label)
ax[0].set_title("(a) Same start x0 = 0.3, different r")
ax[0].legend(); ax[0].set_ylim(0, 1)

# (ب) نفس r لكن فرق صغير جداً في البداية: 0.3 و 0.3000001
a = logistic(0.3, 3.99, N)
b = logistic(0.3000001, 3.99, N)
ax[1].plot(a, marker=".", label="x0 = 0.3")
ax[1].plot(b, marker=".", label="x0 = 0.3000001")
ax[1].set_title("(b) r = 3.99, start differs by 0.0000001")
ax[1].legend(); ax[1].set_ylim(0, 1)
diverge = next(i for i in range(N) if abs(a[i] - b[i]) > 0.1)
print(f"السلسلتان تفترقان (فرق > 0.1) عند التكرار رقم {diverge}")

# (ج) توزيع 100 ألف قيمة: الأرقام نفسها غير متساوية التوزيع، لكن البايتات المشتقة منها متساوية
xs = np.array(logistic(0.3, 3.99, 100_000))
bytes_ = (np.floor(xs * 1e8).astype(np.int64) % 256)
ax[2].hist(bytes_, bins=256, color="gray")
ax[2].set_title("(c) Histogram of the 100,000 key bytes  floor(x*1e8) mod 256  -> almost flat")
ax[2].set_xlim(0, 255)

plt.tight_layout()
plt.savefig("lab3_logistic.png", dpi=120)
plt.show()
print("الرسم محفوظ باسم lab3_logistic.png")
