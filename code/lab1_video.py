# التجربة 1: افتحي فيديو (أو الكاميرا) واعرضي فريماته واحداً واحداً
import cv2

SOURCE = "test_video.avi"   # اسم ملف فيديو بجانب هذا الملف، أو اكتبي 0 لكاميرا اللابتوب

cap = cv2.VideoCapture(SOURCE)
if not cap.isOpened():
    raise SystemExit("لم أستطع فتح المصدر. تأكدي من اسم الملف أو جربي 1 بدل 0 للكاميرا.")

print("العرض :", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("الارتفاع:", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("FPS    :", cap.get(cv2.CAP_PROP_FPS))

count = 0
last = None
while True:
    ok, frame = cap.read()          # frame = مصفوفة أرقام بحجم (ارتفاع، عرض، 3)
    if not ok:                      # انتهى الفيديو أو انقطعت الكاميرا
        break
    count += 1
    last = frame
    cv2.putText(frame, f"frame {count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Lab 1 - press q to quit", frame)
    if cv2.waitKey(30) & 0xFF == ord("q"):   # 30 ملي ثانية انتظار بين الفريمات
        break

cap.release()
cv2.destroyAllWindows()

print("عدد الفريمات التي قرأتها:", count)
if last is not None:
    print("شكل الفريم (ارتفاع، عرض، قنوات):", last.shape)
    print("قيمة أول بكسل (أزرق، أخضر، أحمر):", last[0, 0])
