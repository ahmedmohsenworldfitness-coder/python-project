import streamlit as st
import sqlite3
from datetime import datetime
import os

st.set_page_config(page_title="جنة الهانوفيل", layout="wide")

# ===== قاعدة البيانات =====
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# جدول الشقق
c.execute("""
CREATE TABLE IF NOT EXISTS apartments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    details TEXT,
    price TEXT,
    rooms TEXT,
    image_path TEXT,
    video_path TEXT,
    status TEXT,
    available_from TEXT,
    available_to TEXT
)
""")

# جدول التقييمات
c.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment_id INTEGER,
    name TEXT,
    rating INTEGER,
    comment TEXT,
    date TEXT
)
""")

conn.commit()

# ===== صفحة الإدارة =====
st.sidebar.title("لوحة التحكم (Admin)")
admin_password = st.sidebar.text_input("كلمة المرور (Admin)", type="password")

if admin_password == "admin123":  # غيريها لكلمة سر قوية
    st.sidebar.success("تم تسجيل الدخول كمسؤول ✅")
    st.title("💼 إدارة الشقق")

    # ==== إضافة شقة جديدة ====
    st.subheader("➕ إضافة شقة جديدة")
    with st.form("add_apartment"):
        name = st.text_input("اسم الشقة")
        details = st.text_area("تفاصيل الشقة")
        price = st.text_input("السعر")
        rooms = st.text_input("عدد الغرف")
        status = st.selectbox("الحالة", ["متاح", "محجوز"])
        available_from = st.date_input("متاحة من")
        available_to = st.date_input("متاحة إلى")
        image_file = st.file_uploader("صورة الشقة", type=["jpg", "png"])
        video_file = st.file_uploader("فيديو الشقة", type=["mp4"])
        submit_add = st.form_submit_button("إضافة الشقة")

    if submit_add and name:
        image_path = f"images/{name.replace(' ','_')}.jpg" if image_file else ""
        video_path = f"videos/{name.replace(' ','_')}.mp4" if video_file else ""

        # إنشاء مجلدات لو مش موجودة
        os.makedirs("images", exist_ok=True)
        os.makedirs("videos", exist_ok=True)

        if image_file:
            with open(image_path, "wb") as f:
                f.write(image_file.getbuffer())
        if video_file:
            with open(video_path, "wb") as f:
                f.write(video_file.getbuffer())

        c.execute("""INSERT INTO apartments
            (name, details, price, rooms, image_path, video_path, status, available_from, available_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, details, price, rooms, image_path, video_path, status,
             available_from.strftime("%Y-%m-%d"), available_to.strftime("%Y-%m-%d")))
        conn.commit()
        st.success(f"تم إضافة الشقة {name} بنجاح ✅")

    # ==== تعديل / حذف شقة ====
    st.subheader("✏️ تعديل / حذف الشقق")
    c.execute("SELECT id, name FROM apartments")
    apartments = c.fetchall()
    apt_options = {f"{apt[1]} (ID:{apt[0]})": apt[0] for apt in apartments}

    if apt_options:
        selected_apt_name = st.selectbox("اختر الشقة للتعديل/الحذف", list(apt_options.keys()))
        apt_id = apt_options[selected_apt_name]
        c.execute("SELECT * FROM apartments WHERE id=?", (apt_id,))
        apt_data = c.fetchone()

        name = st.text_input("اسم الشقة", apt_data[1])
        details = st.text_area("تفاصيل الشقة", apt_data[2])
        price = st.text_input("السعر", apt_data[3])
        rooms = st.text_input("عدد الغرف", apt_data[4])
        status = st.selectbox("الحالة", ["متاح", "محجوز"], index=0 if apt_data[7]=="متاح" else 1)
        available_from = st.date_input("متاحة من", datetime.strptime(apt_data[8], "%Y-%m-%d"))
        available_to = st.date_input("متاحة إلى", datetime.strptime(apt_data[9], "%Y-%m-%d"))
        image_file = st.file_uploader("تغيير صورة الشقة", type=["jpg", "png"])
        video_file = st.file_uploader("تغيير فيديو الشقة", type=["mp4"])

        if st.button("حفظ التعديلات"):
            image_path = apt_data[5]
            video_path = apt_data[6]
            if image_file:
                image_path = f"images/{name.replace(' ','_')}.jpg"
                with open(image_path, "wb") as f:
                    f.write(image_file.getbuffer())
            if video_file:
                video_path = f"videos/{name.replace(' ','_')}.mp4"
                with open(video_path, "wb") as f:
                    f.write(video_file.getbuffer())
            c.execute("""UPDATE apartments SET name=?, details=?, price=?, rooms=?,
                        image_path=?, video_path=?, status=?, available_from=?, available_to=? WHERE id=?""",
                        (name, details, price, rooms, image_path, video_path, status,
                         available_from.strftime("%Y-%m-%d"), available_to.strftime("%Y-%m-%d"), apt_id))
            conn.commit()
            st.success("تم حفظ التعديلات ✅")

        if st.button("حذف الشقة"):
            c.execute("DELETE FROM apartments WHERE id=?", (apt_id,))
            conn.commit()
            st.warning("تم حذف الشقة ⚠️")

else:
    st.info("👀 أدخل كلمة المرور في الشريط الجانبي للوصول للوحة الإدارة")

# ===== صفحة الزوار =====
st.header("🌴 جنة الهانوفيل - شقق المصيف")

c.execute("SELECT * FROM apartments")
apartments = c.fetchall()

for apt in apartments:
    apt_id, name, details, price, rooms, image_path, video_path, status, available_from, available_to = apt
    if status == "محجوز":
        st.header(f"🏠 {name} (محجوز) ❌")
    else:
        st.header(f"🏠 {name} ({status})")
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.write("📷 صورة غير متوفرة")
        with col2:
            if os.path.exists(video_path):
                st.video(video_path)
            else:
                st.write("🎥 فيديو غير متوفر")
        st.write(f"{details}\n💰 السعر: {price}\n🛏️ عدد الغرف: {rooms}")
        st.write(f"📍 متاحة من {available_from} إلى {available_to}")
        st.markdown("[📲 احجز الآن على واتساب](https://wa.me/201149493002)")
    st.divider()

# ===== قسم التقييمات =====
st.header("⭐ تقييمات العملاء")

# نموذج إضافة تقييم جديد
with st.form(key="review_form"):
    available_apts = [(apt[0], apt[1]) for apt in apartments]
    apt_dict = {name:id for id,name in available_apts}
    selected_apt_name = st.selectbox("اختر الشقة", [name for id,name in available_apts])
    selected_apt_id = apt_dict[selected_apt_name]
    name = st.text_input("اسمك")
    rating = st.slider("التقييم", 1, 5, 5)
    comment = st.text_area("اكتب رأيك هنا")
    submit_button = st.form_submit_button(label="إرسال التقييم")

if submit_button and name and comment:
    c.execute("INSERT INTO reviews (apartment_id, name, rating, comment, date) VALUES (?, ?, ?, ?, ?)",
              (selected_apt_id, name, rating, comment, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    st.success(f"شكرًا {name}! تم إضافة تقييمك 🌟")

# عرض كل التقييمات
st.subheader("التقييمات السابقة")
c.execute("""SELECT r.name, r.rating, r.comment, r.date, a.name 
             FROM reviews r JOIN apartments a ON r.apartment_id = a.id 
             ORDER BY r.id DESC""")
for row in c.fetchall():
    st.write(f"🏠 {row[4]} — {row[0]}: {row[1]} ⭐ — {row[2]} ({row[3]})")

conn.close()
