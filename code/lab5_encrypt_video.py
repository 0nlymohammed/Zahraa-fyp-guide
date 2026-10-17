# التجربة 5: شفّري فيديو كاملاً (مفتاح مختلف لكل فريم)، احفظيه بدون فقد، ثم فكّيه وقارني
import os
import time
import numpy as np
import cv2
import chaos

SOURCE = "test_video.avi"
MASTER_KEY = "zahraa-secret-2026"

cap = cv2.VideoCapture(SOURCE)
w, h, fps = int(cap.get(3)), int(cap.get(4)), cap.get(cv2.CAP_PROP_FPS) or 24

# FFV1 = ترميز بدون فقد: كل بايت يُحفظ كما هو. لو استخدمنا mp4v أو XVID لانكسر فك التشفير
writer = cv2.VideoWriter("encrypted.avi", cv2.VideoWriter_fourcc(*"FFV1"), fps, (w, h))
if not writer.isOpened():
    raise SystemExit("لم يُفتح الملف للكتابة بترميز FFV1. البديل: احفظي كل فريم كـ PNG في مجلد.")

originals = []
t0 = time.time()
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    originals.append(frame)
    x0, r = chaos.frame_key(MASTER_KEY, i)      # مفتاح جديد لكل فريم من نفس كلمة السر
    writer.write(chaos.encrypt(frame, x0, r))
    i += 1
cap.release()
writer.release()
enc_time = time.time() - t0
print(f"شُفّر {i} فريم بحجم {w}x{h} في {enc_time:.1f} ثانية  =  {i / enc_time:.1f} FPS")

# ---- الآن نلعب دور المستقبل: نقرأ الملف المشفر ونفكه ----
cap = cv2.VideoCapture("encrypted.avi")
identical = 0
j = 0
while True:
    ok, enc_frame = cap.read()
    if not ok:
        break
    x0, r = chaos.frame_key(MASTER_KEY, j)
    dec = chaos.decrypt(enc_frame, x0, r)
    if np.array_equal(dec, originals[j]):
        identical += 1
    if j == 60:                                  # نحفظ صورة للمقارنة
        side = np.hstack([originals[j], enc_frame, dec])
        cv2.imwrite("lab5_frames.png", side)
    j += 1
cap.release()
print(f"فريمات رجعت مطابقة تماماً: {identical} / {j}")

mb = lambda p: os.path.getsize(p) / 1e6
print(f"حجم الأصل {SOURCE}: {mb(SOURCE):.1f} MB  |  حجم المشفر encrypted.avi: {mb('encrypted.avi'):.1f} MB")
print("المشفر أكبر لأن الضوضاء لا تنضغط. هذا طبيعي واذكريه في التقرير.")
