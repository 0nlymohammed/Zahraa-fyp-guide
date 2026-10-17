# التجربة 6: وضع خصوصية الوجوه - اكشفي الوجوه وشفّري مربع الوجه فقط
import csv
import cv2
import numpy as np
import chaos

SOURCE = "test_video.avi"
MASTER_KEY = "zahraa-secret-2026"
MARGIN = 0.2                 # نكبّر مربع الوجه 20% من كل جهة (الشعر والذقن يكشفان الهوية أيضاً)

# ملفا الموديل موجودان في مجلد الكود (مصدرهما opencv_zoo على GitHub، الرابط في الدليل)
# OpenCV 5 -> face_detection_yunet_2026may.onnx   |   OpenCV 4 -> face_detection_yunet_2023mar.onnx
MODEL = "face_detection_yunet_2026may.onnx" if cv2.__version__.startswith("5") else "face_detection_yunet_2023mar.onnx"

cap = cv2.VideoCapture(SOURCE)
w, h, fps = int(cap.get(3)), int(cap.get(4)), cap.get(cv2.CAP_PROP_FPS) or 24
detector = cv2.FaceDetectorYN.create(MODEL, "", (w, h), score_threshold=0.6, nms_threshold=0.3, top_k=50)

writer = cv2.VideoWriter("faces_encrypted.avi", cv2.VideoWriter_fourcc(*"FFV1"), fps, (w, h))
meta = open("faces_meta.csv", "w", newline="")
csv_out = csv.writer(meta)
csv_out.writerow(["frame", "face", "x1", "y1", "x2", "y2"])   # المستقبل يحتاج المواقع حتى يفك

frames_with_face = 0
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    detector.setInputSize((w, h))
    _, faces = detector.detect(frame)            # كل صف: x, y, عرض, ارتفاع, 10 أرقام للملامح, الثقة
    if faces is not None:
        frames_with_face += 1
        for k, f in enumerate(faces):
            x, y, fw, fh = f[:4]
            # تكبير المربع ثم قصّه حتى لا يخرج عن حدود الصورة
            x1 = max(0, int(x - MARGIN * fw)); y1 = max(0, int(y - MARGIN * fh))
            x2 = min(w, int(x + fw * (1 + MARGIN))); y2 = min(h, int(y + fh * (1 + MARGIN)))
            roi = frame[y1:y2, x1:x2]                           # قص منطقة الوجه
            kx0, kr = chaos.frame_key(MASTER_KEY, i, k)         # مفتاح لكل وجه في كل فريم
            frame[y1:y2, x1:x2] = chaos.encrypt(roi, kx0, kr)   # إرجاع المنطقة مشفرة
            csv_out.writerow([i, k, x1, y1, x2, y2])
    writer.write(frame)
    if i == 60:
        cv2.imwrite("lab6_face_mode.png", frame)
    cv2.imshow("Lab 6 - faces encrypted (q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    i += 1

cap.release(); writer.release(); meta.close(); cv2.destroyAllWindows()
print(f"فريمات فيها وجه مكشوف: {frames_with_face} / {i}")
print("الفيديو: faces_encrypted.avi   |   مواقع الوجوه: faces_meta.csv")

# ---- فك وجه واحد كتجربة (نفس ما سيفعله الطرف المخوّل) ----
rows = [r for r in csv.DictReader(open("faces_meta.csv")) if r["frame"] == "60"]
cap = cv2.VideoCapture("faces_encrypted.avi"); cap.set(cv2.CAP_PROP_POS_FRAMES, 60); _, f60 = cap.read()
for r in rows:
    x1, y1, x2, y2 = int(r["x1"]), int(r["y1"]), int(r["x2"]), int(r["y2"])
    kx0, kr = chaos.frame_key(MASTER_KEY, 60, int(r["face"]))
    f60[y1:y2, x1:x2] = chaos.decrypt(f60[y1:y2, x1:x2], kx0, kr)
cv2.imwrite("lab6_face_decrypted.png", f60)
print("الفريم 60 بعد فك الوجوه محفوظ باسم lab6_face_decrypted.png")
