# chaos.py  -  التشفير الفوضوي للصور (خريطة logistic + بعثرة + انتشار)
# هذا الملف تستخدمه كل التجارب من 4 إلى 8. لا تغيّري فيه شيئاً، فقط استدعيه.

import hashlib
import numpy as np

# تسريع اختياري: إذا كانت مكتبة numba منصّبة تُستخدم تلقائياً (أسرع 50 مرة تقريباً)،
# وإذا لم تكن منصّبة يعمل الكود بشكل طبيعي لكن أبطأ. التجربة 5 تشرح الفرق.
try:
    from numba import njit
except ImportError:
    def njit(f):
        return f


@njit
def logistic_sequence(x0, r, n, skip=1000):
    """تولّد n عدداً بين 0 و1 من معادلة logistic:  x(n+1) = r * x(n) * (1 - x(n))
    نرمي أول skip عدداً حتى تبتعد السلسلة عن نقطة البداية."""
    x = x0
    for _ in range(skip):
        x = r * x * (1.0 - x)
    out = np.empty(n)
    for i in range(n):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


@njit
def diffuse(p, k):
    """الانتشار: كل بايت مشفر يعتمد على مفتاحه وعلى البايت المشفر الذي قبله.
    c[i] = k[i] XOR ((p[i] + c[i-1]) mod 256)"""
    n = p.shape[0]
    c = np.empty(n, dtype=np.uint8)
    prev = 0
    for i in range(n):
        v = (int(p[i]) + prev) % 256
        c[i] = v ^ int(k[i])
        prev = int(c[i])
    return c


@njit
def undiffuse(c, k):
    """عكس الانتشار:  p[i] = ((c[i] XOR k[i]) - c[i-1]) mod 256"""
    n = c.shape[0]
    p = np.empty(n, dtype=np.uint8)
    prev = 0
    for i in range(n):
        v = int(c[i]) ^ int(k[i])
        p[i] = (v - prev) % 256
        prev = int(c[i])
    return p


@njit
def diffuse_backward(p, k):
    """نفس الانتشار لكن من آخر بايت إلى أوله.
    لماذا جولتان؟ في الجولة الأمامية تغيير بكسل يؤثر فقط على ما بعده. بالجولة الخلفية
    يصبح كل بكسل مشفر معتمداً على كل بكسلات الصورة (هذا ما يرفع NPCR إلى 99.6%)."""
    n = p.shape[0]
    c = np.empty(n, dtype=np.uint8)
    prev = 0
    for i in range(n - 1, -1, -1):
        v = (int(p[i]) + prev) % 256
        c[i] = v ^ int(k[i])
        prev = int(c[i])
    return c


@njit
def undiffuse_backward(c, k):
    n = c.shape[0]
    p = np.empty(n, dtype=np.uint8)
    prev = 0
    for i in range(n - 1, -1, -1):
        v = int(c[i]) ^ int(k[i])
        p[i] = (v - prev) % 256
        prev = int(c[i])
    return p


def frame_key(master_key, frame_index, extra=0):
    """تشتق مفتاحاً مختلفاً (x0, r) لكل فريم من كلمة السر الرئيسية باستخدام SHA-256.
    extra: رقم إضافي (مثل رقم الوجه داخل الفريم) حتى يكون لكل وجه مفتاحه."""
    text = f"{master_key}|{frame_index}|{extra}".encode()
    h = hashlib.sha256(text).digest()               # 32 بايت ثابتة لنفس النص
    a = int.from_bytes(h[:8], "big") / 2 ** 64      # عدد بين 0 و1
    b = int.from_bytes(h[8:16], "big") / 2 ** 64
    x0 = 0.1 + 0.8 * a                              # نبقيه بين 0.1 و0.9
    r = 3.99 + 0.01 * b                             # نبقيه بين 3.99 و4.0 (منطقة فوضوية)
    return x0, r


def _streams(x0, r, n):
    """سلسلة واحدة طويلة بطول 3n: الثلث الأول لترتيب المواقع، والثلثان الآخران مفتاحا بايتات."""
    seq = logistic_sequence(x0, r, 3 * n)
    perm = np.argsort(seq[:n])                              # ترتيب جديد "عشوائي" للمواقع
    k = (np.floor(seq[n:] * 1e8).astype(np.int64) % 256).astype(np.uint8)
    return perm, k[:n], k[n:]


def encrypt(img, x0, r):
    """تشفّر صورة (أو أي مصفوفة uint8) وترجع مصفوفة بنفس الحجم."""
    shape = img.shape
    flat = np.ascontiguousarray(img).reshape(-1)    # صف واحد طويل من البايتات
    perm, k1, k2 = _streams(x0, r, flat.size)
    shuffled = flat[perm]                           # 1) بعثرة المواقع
    cipher = diffuse(shuffled, k1)                  # 2) انتشار أمامي
    cipher = diffuse_backward(cipher, k2)           # 3) انتشار خلفي
    return cipher.reshape(shape)


def decrypt(cipher, x0, r):
    """تعكس الخطوات الثلاث بالترتيب المعاكس."""
    shape = cipher.shape
    flat = np.ascontiguousarray(cipher).reshape(-1)
    perm, k1, k2 = _streams(x0, r, flat.size)
    shuffled = undiffuse_backward(flat, k2)         # 3) عكس الانتشار الخلفي
    shuffled = undiffuse(shuffled, k1)              # 2) عكس الانتشار الأمامي
    plain = np.empty_like(shuffled)
    plain[perm] = shuffled                          # 1) إرجاع المواقع
    return plain.reshape(shape)
