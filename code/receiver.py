# التجربة 8 (ب): المستقبل - شاشة المراقبة
# بدون مفتاح: يرى مربعات التتبع لكن الوجوه (أو الفريم كله) تبقى ضوضاء
# مع المفتاح الصحيح: يفك التشفير ويرى كل شيء
import csv
from collections import defaultdict
import cv2
import chaos

MASTER_KEY = ""                  # اتركيها فارغة = مراقب غير مخوّل  |  "zahraa-secret-2026" = مخوّل
MODE = "face"                    # نفس وضع المرسل

boxes = defaultdict(list)        # رقم الفريم -> قائمة المربعات
for row in csv.DictReader(open("stream_meta.csv")):
    boxes[int(row["frame"])].append(row)

cap = cv2.VideoCapture("stream_encrypted.avi")
w, h, fps = int(cap.get(3)), int(cap.get(4)), cap.get(cv2.CAP_PROP_FPS) or 24
out = cv2.VideoWriter("receiver_view.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

status = "AUTHORIZED (decrypted)" if MASTER_KEY else "MONITOR (no key)"
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break

    if MASTER_KEY:                                           # 1) فك التشفير إن وُجد المفتاح
        if MODE == "full":
            x0, r = chaos.frame_key(MASTER_KEY, i)
            frame = chaos.decrypt(frame, x0, r)
        else:
            for b in reversed(boxes[i]):                     # عكس ترتيب التشفير (مهم عند تداخل وجهين)
                if b["kind"] == "face":
                    x1, y1, x2, y2 = int(b["x1"]), int(b["y1"]), int(b["x2"]), int(b["y2"])
                    x0, r = chaos.frame_key(MASTER_KEY, i, int(b["id"]))
                    frame[y1:y2, x1:x2] = chaos.decrypt(frame[y1:y2, x1:x2], x0, r)

    for b in boxes[i]:                                       # 2) رسم مربعات التتبع فوق الصورة
        if b["kind"] == "track":
            x1, y1, x2, y2 = int(b["x1"]), int(b["y1"]), int(b["x2"]), int(b["y2"])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 120, 0), 2)
            cv2.putText(frame, f"id {b['id']}", (x1, max(20, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 120, 0), 2)

    cv2.rectangle(frame, (0, 0), (330, 34), (30, 30, 30), -1)          # خلفية داكنة لنص الحالة
    cv2.putText(frame, status, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    out.write(frame)
    if i == 60:
        cv2.imwrite("lab8_receiver_" + ("key" if MASTER_KEY else "nokey") + ".png", frame)
    cv2.imshow("Receiver - q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    i += 1

cap.release(); out.release(); cv2.destroyAllWindows()
print(f"المستقبل عرض {i} فريم كـ {status}. الفيديو: receiver_view.mp4")
