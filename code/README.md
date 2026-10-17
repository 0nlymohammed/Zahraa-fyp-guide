# كود الدليل العملي

الشرح الكامل خطوة بخطوة: https://0nlymohammed.github.io/Zahraa-fyp-guide/

التنصيب (مرة واحدة، داخل هذا المجلد):

    py -3.13 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

الترتيب:

| الملف | التجربة |
|---|---|
| lab1_video.py | قراءة فيديو/كاميرا بـ OpenCV |
| lab2_track.py | كشف وتتبع بـ YOLO |
| lab3_logistic.py | رسم معادلة logistic وحساسيتها |
| chaos.py | خوارزمية التشفير (يستخدمها الباقي) |
| lab4_encrypt_image.py | تشفير صورة وفكها |
| lab5_encrypt_video.py | تشفير فيديو كامل بترميز بدون فقد |
| lab6_face_mode.py | وضع خصوصية الوجوه |
| lab7_metrics.py | NPCR / UACI / Entropy / Correlation / FPS |
| sender.py + receiver.py | النظام كاملاً: مرسل ومستقبل |

ملفات مساعدة: test_video.avi (فيديو اختبار)، photo.jpg (صورة اختبار، صورة عامة من ناسا)،
face_detection_yunet_*.onnx (كاشف الوجوه YuNet من opencv_zoo، ترخيص MIT).
موديل yolo26n.pt يُنزَّل تلقائياً عند أول تشغيل.
