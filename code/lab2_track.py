# التجربة 2: كشف الأجسام وتتبعها بـ YOLO (كل شخص يأخذ رقماً ثابتاً ID)
import time
import cv2
from ultralytics import YOLO

SOURCE = "test_video.avi"      # أو 0 للكاميرا
MODEL = "yolo26n.pt"           # n = nano، أصغر وأسرع نسخة. تُنزَّل تلقائياً أول مرة (5 ميغابايت)
DEVICE = "cpu"                 # اكتبي 0 إذا عندك كرت شاشة NVIDIA وثبّتِ torch بنسخة CUDA

model = YOLO(MODEL)
cap = cv2.VideoCapture(SOURCE)
if not cap.isOpened():
    raise SystemExit("لم أستطع فتح المصدر. تأكدي من اسم الملف أو رقم الكاميرا.")
w, h = int(cap.get(3)), int(cap.get(4))
out = cv2.VideoWriter("tracked.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 24, (w, h))

ids_seen = set()
count = 0
t0 = time.time()
while True:
    ok, frame = cap.read()
    if not ok:
        break
    # persist=True يعني: تذكّر الأجسام من الفريم السابق (بدونها تضيع الأرقام)
    results = model.track(frame, persist=True, tracker="botsort.yaml",
                          conf=0.4, device=DEVICE, verbose=False)
    r = results[0]
    if r.boxes.id is not None:                      # قد لا يوجد أي جسم في الفريم
        for box, tid, cls, conf in zip(r.boxes.xyxy, r.boxes.id, r.boxes.cls, r.boxes.conf):
            x1, y1, x2, y2 = [int(v) for v in box]   # إحداثيات المربع
            ids_seen.add(int(tid))
            # هنا تقدرين تعملين أي شيء بالمربع، مثلاً طباعته:
            # print(count, model.names[int(cls)], int(tid), x1, y1, x2, y2)
    annotated = r.plot()                            # يرسم المربعات والأرقام جاهزة
    out.write(annotated)
    cv2.imshow("Lab 2 - press q to quit", annotated)
    count += 1
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
seconds = time.time() - t0
print(f"فريمات: {count}  |  السرعة: {count / seconds:.1f} FPS على {DEVICE}")
print("أرقام التتبع التي ظهرت:", sorted(ids_seen))
print("الفيديو المرسوم محفوظ باسم tracked.mp4")
