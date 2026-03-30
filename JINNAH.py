import streamlit as st
import sqlite3
from datetime import datetime
import os

# ===== إعداد الصفحة =====
st.set_page_config(page_title="جنة الهانوفيل", layout="wide")

# ===== مجلد البيانات =====
DATA_DIR = "data"
IMAGE_DIR = os.path.join(DATA_DIR, "images")
VIDEO_DIR = os.path.join(DATA_DIR, "videos")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "database.db")

# ===== إنشاء قاعدة البيانات والجداول =====
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

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

# ===== لوحة الإدارة =====
st.sidebar.title("لوحة التحكم (Admin)")
admin_password_input = st.sidebar.text_input("كلمة المرور (Admin)", type="password")
admin_submit = st.sidebar.button("تسجيل الدخول")

if admin_submit:
    if admin_password_input == "admin123":  # غيرها لكلمة سر قوية
        st.sidebar.success("تم تسجيل الدخول ✅")
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
            image_path = os.path.join(IMAGE_DIR, f"{name.replace(' ','_')}.jpg") if image_file else ""
            video_path = os.path.join(VIDEO_DIR, f"{name.replace(' ','_')}.mp4") if video_file else ""
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
        apartments_list = c.fetchall()
        apt_options = {f"{apt[1]} (ID:{apt[0]})": apt[0] for apt in apartments_list}

        if apt_options:
            selected_apt_name = st.selectbox("اختر الشقة للتعديل/الحذف", list(apt_options.keys()))
            apt_id = apt_options[selected_apt_name]
            c.execute("SELECT * FROM apartments WHERE id=?", (apt_id,))
            apt_data = c.fetchone()

            with st.form("edit_apartment"):
                name_edit = st.text_input("اسم الشقة", apt_data[1])
                details_edit = st.text_area("تفاصيل الشقة", apt_data[2])
                price_edit = st.text_input("السعر", apt_data[3])
                rooms_edit = st.text_input("عدد الغرف", apt_data[4])
                status_edit = st.selectbox("الحالة", ["متاح", "محجوز"], index=0 if apt_data[7]=="متاح" else 1)
                available_from_edit = st.date_input("متاحة من", datetime.strptime(apt_data[8], "%Y-%m-%d"))
                available_to_edit = st.date_input("متاحة إلى", datetime.strptime(apt_data[9], "%Y-%m-%d"))
                image_file_edit = st.file_uploader("تغيير صورة الشقة", type=["jpg", "png"])
                video_file_edit = st.file_uploader("تغيير فيديو الشقة", type=["mp4"])
                submit_edit = st.form_submit_button("حفظ التعديلات")
                submit_delete = st.form_submit_button("حذف الشقة")

            if submit_edit:
                image_path_edit = apt_data[5]
                video_path_edit = apt_data[6]
                if image_file_edit:
                    image_path_edit = os.path.join(IMAGE_DIR, f"{name_edit.replace(' ','_')}.jpg")
                    with open(image_path_edit, "wb") as f:
                        f.write(image_file_edit.getbuffer())
                if video_file_edit:
                    video_path_edit = os.path.join(VIDEO_DIR, f"{name_edit.replace(' ','_')}.mp4")
                    with open(video_path_edit, "wb") as f:
                        f.write(video_file_edit.getbuffer())
                c.execute("""UPDATE apartments SET name=?, details=?, price=?, rooms=?,
                            image_path=?, video_path=?, status=?, available_from=?, available_to=? WHERE id=?""",
                            (name_edit, details_edit, price_edit, rooms_edit,
                             image_path_edit, video_path_edit, status_edit,
                             available_from_edit.strftime("%Y-%m-%d"), available_to_edit.strftime("%Y-%m-%d"), apt_id))
                conn.commit()
                st.success("تم حفظ التعديلات ✅")

            if submit_delete:
                c.execute("DELETE FROM apartments WHERE id=?", (apt_id,))
                conn.commit()
                st.warning("تم حذف الشقة ⚠️")

    else:
        st.sidebar.error("كلمة المرور خاطئة ❌")

# ===== واجهة الزوار =====
st.header("🌴 جنة الهانوفيل - شقق المصيف")

c.execute("SELECT * FROM apartments WHERE status='متاح'")
apartments = c.fetchall()

if apartments:
    for i in range(0, len(apartments), 3):
        cols = st.columns(3)
        for j, apt in enumerate(apartments[i:i+3]):
            apt_id, name, details, price, rooms, image_path, video_path, status, available_from, available_to = apt
            with cols[j]:
                if image_path and os.path.exists(image_path):
                    st.image(image_path, use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200.png?text=No+Image", use_column_width=True)
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:8px; box-shadow:2px 2px 5px rgba(0,0,0,0.1)">
                <h4>🏠 {name}</h4>
                <p>{details}</p>
                <p>💰 السعر: {price}</p>
                <p>🛏️ عدد الغرف: {rooms}</p>
                <p>📍 متاحة من {available_from} إلى {available_to}</p>
                <a href='https://wa.me/201149493002' target='_blank'>📲 احجز الآن على واتساب</a>
                </div>
                """, unsafe_allow_html=True)
else:
    st.warning("لا توجد شقق متاحة حالياً.")

# ===== قسم التقييمات =====
st.header("⭐ تقييمات العملاء")
with st.form(key="review_form"):
    available_apts = [(apt[0], apt[1]) for apt in apartments]
    if available_apts:
        apt_dict = {name:id for id,name in available_apts}
        selected_apt_name = st.selectbox("اختر الشقة", [name for id,name in available_apts])
        selected_apt_id = apt_dict[selected_apt_name]
    else:
        selected_apt_id = None
        st.warning("لا توجد شقق متاحة لإضافة تقييم.")

    name_input = st.text_input("اسمك")
    rating = st.slider("التقييم", 1, 5, 5)
    comment = st.text_area("اكتب رأيك هنا")
    submit_review = st.form_submit_button(label="إرسال التقييم")

if submit_review and name_input and comment and selected_apt_id:
    c.execute("INSERT INTO reviews (apartment_id, name, rating, comment, date) VALUES (?, ?, ?, ?, ?)",
              (selected_apt_id, name_input, rating, comment, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    st.success(f"شكرًا {name_input}! تم إضافة تقييمك 🌟")

# عرض كل التقييمات
st.subheader("التقييمات السابقة")
c.execute("""SELECT r.name, r.rating, r.comment, r.date, a.name 
             FROM reviews r JOIN apartments a ON r.apartment_id = a.id 
             ORDER BY r.id DESC""")
for row in c.fetchall():
    st.write(f"🏠 {row[4]} — {row[0]}: {row[1]} ⭐ — {row[2]} ({row[3]})")

conn.close()
