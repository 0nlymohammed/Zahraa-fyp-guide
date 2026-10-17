# التجربة 8 (أ): المرسل - الجهاز الموثوق المتصل بالكاميرا
# يقرأ الفريم -> يتتبع الأشخاص بـ YOLO -> يشفّر (الفريم كله أو الوجوه فقط) -> يحفظ/يرسل
import csv
import time
import cv2
from ultralytics import YOLO
import chaos

SOURCE = "test_video.avi"          # أو 0 للكاميرا
MODE = "face"                      # "full" = تشفير الفريم كله  |  "face" = تشفير الوجوه فقط
MASTER_KEY = "zahraa-secret-2026"
DEVICE = "cpu"                     # 0 إذا عندك كرت NVIDIA
MARGIN = 0.2

model = YOLO("yolo26n.pt")
cap = cv2.VideoCapture(SOURCE)
w, h, fps = int(cap.get(3)), int(cap.get(4)), cap.get(cv2.CAP_PROP_FPS) or 24
face_model = "face_detection_yunet_2026may.onnx" if cv2.__version__.startswith("5") else "face_detection_yunet_2023mar.onnx"
faces_det = cv2.FaceDetectorYN.create(face_model, "", (w, h), 0.6, 0.3, 50)

writer = cv2.VideoWriter("stream_encrypted.avi", cv2.VideoWriter_fourcc(*"FFV1"), fps, (w, h))
meta = csv.writer(open("stream_meta.csv", "w", newline=""))
meta.writerow(["frame", "kind", "id", "label", "x1", "y1", "x2", "y2"])
# kind = "track": مربع شخص من YOLO (للعرض فقط)     kind = "face": مربع وجه مشفر (يحتاجه فك التشفير)

i = 0
t0 = time.time()
while True:
    ok, frame = cap.read()
    if not ok:
        break

    # 1) التتبع يعمل على الفريم الأصلي، قبل أي تشفير
    r = model.track(frame, persist=True, tracker="botsort.yaml", conf=0.4,
                    classes=[0], device=DEVICE, verbose=False)[0]      # classes=[0] = أشخاص فقط
    if r.boxes.id is not None:
        for box, tid in zip(r.boxes.xyxy, r.boxes.id):
            x1, y1, x2, y2 = [int(v) for v in box]
            meta.writerow([i, "track", int(tid), "person", x1, y1, x2, y2])

    # 2) التشفير
    if MODE == "full":
        x0, rr = chaos.frame_key(MASTER_KEY, i)
        frame = chaos.encrypt(frame, x0, rr)
    else:
        faces_det.setInputSize((w, h))
        _, faces = faces_det.detect(frame)
        for k, f in enumerate(faces if faces is not None else []):
            x, y, fw, fh = f[:4]
            x1 = max(0, int(x - MARGIN * fw)); y1 = max(0, int(y - MARGIN * fh))
            x2 = min(w, int(x + fw * (1 + MARGIN))); y2 = min(h, int(y + fh * (1 + MARGIN)))
            x0, rr = chaos.frame_key(MASTER_KEY, i, k)
            frame[y1:y2, x1:x2] = chaos.encrypt(frame[y1:y2, x1:x2], x0, rr)
            meta.writerow([i, "face", k, "face", x1, y1, x2, y2])

    # 3) "الإرسال": هنا نحفظ في ملف. في مشروع حقيقي يُرسل عبر الشبكة (socket) بنفس البايتات
    writer.write(frame)
    i += 1

cap.release(); writer.release()
print(f"المرسل: {i} فريم في {time.time() - t0:.1f} ثانية، الوضع = {MODE}")
print("الملفات: stream_encrypted.avi + stream_meta.csv   (أرسلي الاثنين للمستقبل، والمفتاح بطريقة آمنة منفصلة)")
