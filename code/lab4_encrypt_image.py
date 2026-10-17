# التجربة 4: شفّري صورة واحدة، فكّيها، وتأكدي أنها رجعت بالضبط
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt
import chaos                                  # ملف chaos.py بجانب هذا الملف

IMAGE = "photo.jpg"                           # أي صورة عندك (jpg أو png)
MASTER_KEY = "zahraa-secret-2026"             # كلمة السر الرئيسية

img = cv2.imread(IMAGE)
if img is None:
    raise SystemExit("لم أجد الصورة، ضعي صورة باسم photo.jpg بجانب هذا الملف")
print("حجم الصورة:", img.shape, "=", img.size, "بايت")

x0, r = chaos.frame_key(MASTER_KEY, 0)        # مفتاح الفريم رقم 0
print(f"المفتاح المشتق: x0 = {x0:.15f}, r = {r:.15f}")

t = time.time()
enc = chaos.encrypt(img, x0, r)
print(f"زمن التشفير: {time.time() - t:.3f} ثانية")

t = time.time()
dec = chaos.decrypt(enc, x0, r)
print(f"زمن فك التشفير: {time.time() - t:.3f} ثانية")
print("هل الصورة رجعت بالضبط؟", np.array_equal(img, dec))

# مفتاح خاطئ (فريم رقم 1 بدل 0): يجب أن تطلع ضوضاء
x_wrong, r_wrong = chaos.frame_key(MASTER_KEY, 1)
wrong = chaos.decrypt(enc, x_wrong, r_wrong)
print(f"بمفتاح خاطئ: نسبة البكسلات الصحيحة = {100 * np.mean(wrong == img):.2f}% (المفروض قرب 0.39%)")

# أهم درس عملي: احفظي المشفر بصيغة بدون فقد (PNG) وليس JPG
cv2.imwrite("encrypted.png", enc)
cv2.imwrite("encrypted.jpg", enc)
from_png = chaos.decrypt(cv2.imread("encrypted.png"), x0, r)
from_jpg = chaos.decrypt(cv2.imread("encrypted.jpg"), x0, r)
print("فك من PNG صحيح؟", np.array_equal(img, from_png))
print(f"فك من JPG صحيح؟ {np.array_equal(img, from_jpg)}  (نسبة البكسلات الصحيحة {100 * np.mean(from_jpg == img):.2f}%)")

# الرسم: الأصل، المشفر، المفكوك، المفكوك من JPG، وهستوغرام الأصل والمشفر
rgb = lambda a: cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
fig, ax = plt.subplots(2, 3, figsize=(12, 7))
ax[0, 0].imshow(rgb(img));      ax[0, 0].set_title("original")
ax[0, 1].imshow(rgb(enc));      ax[0, 1].set_title("encrypted")
ax[0, 2].imshow(rgb(dec));      ax[0, 2].set_title("decrypted (identical)")
ax[1, 0].imshow(rgb(from_jpg)); ax[1, 0].set_title("decrypted from JPG (broken)")
ax[1, 1].hist(img.ravel(), bins=256, color="gray"); ax[1, 1].set_title("histogram: original")
ax[1, 2].hist(enc.ravel(), bins=256, color="gray"); ax[1, 2].set_title("histogram: encrypted (flat)")
for a in ax.ravel()[:4]:
    a.axis("off")
plt.tight_layout()
plt.savefig("lab4_result.png", dpi=110)
plt.show()
print("الرسم محفوظ باسم lab4_result.png")
