import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="ระบบหารค่าใช้จ่าย & แจ้งโอนเงิน",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# Data Management
# -------------------------------------------------------------
DATA_FILE = "expense_data.json"

DEFAULT_DATA = [
    {"id": 1, "name": "ฟอร์ด", "item": "ค่าใช้จ่ายปาร์ตี้รวม (2gether + เสือพุทธบูชา 45)", "amount": 503.53, "status": "โอนแล้ว", "slip_url": "ผู้รับเงิน", "note": "ผู้รับเงิน / เจ้าของบัญชี"},
    {"id": 2, "name": "ใหม่", "item": "ค่าใช้จ่ายปาร์ตี้รวม (ยอดรวมสำรองจ่ายให้ฟลุ๊คและเพื่อนฟุ๊ค)", "amount": 689.67, "status": "ยังไม่โอน", "slip_url": None, "note": "ยอดตนเอง 422.56 บาท + สำรองจ่ายให้ฟลุ๊ค (133.56) และเพื่อนฟุ๊ค (133.56)"},
    {"id": 3, "name": "บอส", "item": "ค่าใช้จ่ายปาร์ตี้รวม (2gether + เสือพุทธบูชา 45)", "amount": 558.53, "status": "ยังไม่โอน", "slip_url": None, "note": ""},
    {"id": 4, "name": "พี่ฟ้า", "item": "ค่าใช้จ่ายปาร์ตี้รวม (2gether + เสือพุทธบูชา 45)", "amount": 488.53, "status": "ยังไม่โอน", "slip_url": None, "note": ""},
    {"id": 5, "name": "คิว", "item": "ค่าใช้จ่ายปาร์ตี้รวม (2gether + เสือพุทธบูชา 45)", "amount": 488.53, "status": "ยังไม่โอน", "slip_url": None, "note": ""},
    {"id": 6, "name": "แบงค์", "item": "ค่าใช้จ่ายปาร์ตี้รวม (2gether + เสือพุทธบูชา 45)", "amount": 399.53, "status": "ยังไม่โอน", "slip_url": None, "note": ""},
    {"id": 7, "name": "นิล", "item": "ค่าใช้จ่ายปาร์ตี้รวม (2gether + เสือพุทธบูชา 45)", "amount": 342.73, "status": "ยังไม่โอน", "slip_url": None, "note": ""},
    {"id": 8, "name": "ฟลุ๊ค", "item": "ค่าใช้จ่ายปาร์ตี้รวม (เสือพุทธบูชา 45)", "amount": 133.56, "status": "โอนแล้ว", "slip_url": "ใหม่จ่ายแทน", "note": "ใหม่จ่ายสำรองให้เรียบร้อยแล้ว"},
    {"id": 9, "name": "เพื่อนฟุ๊ค", "item": "ค่าใช้จ่ายปาร์ตี้รวม (เสือพุทธบูชา 45)", "amount": 133.56, "status": "โอนแล้ว", "slip_url": "ใหม่จ่ายแทน", "note": "ใหม่จ่ายสำรองให้เรียบร้อยแล้ว"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("💸 ระบบหารค่าใช้จ่ายปาร์ตี้ & แนบสลิปออนไลน์")
st.markdown("สรุปยอดบิลร้าน **2gether** และร้าน **เสือ พุทธบูชา 45** (ยอดรวมทั้งหมด 3,471.00 บาท)")

# -------------------------------------------------------------
# Real-time Overview
# -------------------------------------------------------------
df = pd.DataFrame(st.session_state.data)

total = df["amount"].sum()
paid = df[df["status"] == "โอนแล้ว"]["amount"].sum()
unpaid = df[df["status"] == "ยังไม่โอน"]["amount"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 ยอดรวมทั้งหมด", f"฿{total:,.2f}")
col2.metric("✅ ชำระแล้ว/สำรองแล้ว", f"฿{paid:,.2f}", f"{len(df[df['status'] == 'โอนแล้ว'])} คน")
col3.metric("⏳ ยอดค้างโอนเข้าฟอร์ด", f"฿{unpaid:,.2f}", f"{len(df[df['status'] == 'ยังไม่โอน'])} คน", delta_color="inverse")

st.progress(paid / total if total > 0 else 0, text=f"ความคืบหน้าการชำระเงิน: {paid/total*100:.1f}%")

st.divider()

# -------------------------------------------------------------
# Check QR Code Image Filename
# -------------------------------------------------------------
qr_filename = None
possible_qrs = ["IMG_7733.jpeg", "IMG_7733.jpg", "IMG_7733.png", "IMG_7733.JPEG", "IMG_7733.JPG", "qr_code.png"]

for filename in possible_qrs:
    if os.path.exists(filename):
        qr_filename = filename
        break

# -------------------------------------------------------------
# User Section
# -------------------------------------------------------------
st.header("📲 ช่องทางสำหรับเพื่อน: สแกนจ่าย & แนบสลิปโอนเงิน")

all_members = [item["name"] for item in st.session_state.data]
selected_name = st.selectbox("1. เลือกชื่อของคุณจากรายการ:", options=["-- เลือกชื่อของคุณ --"] + all_members)

if selected_name != "-- เลือกชื่อของคุณ --":
    user_items = [item for item in st.session_state.data if item["name"] == selected_name]
    
    st.info(f"👤 ข้อมูลการโอนเงินของ **{selected_name}**")
    
    for u_item in user_items:
        st.write(f"- รายการ: **{u_item['item']}**")
        st.write(f"- ยอดที่ต้องโอน: **฿{u_item['amount']:,.2f}**")
        if u_item.get("note"):
            st.caption(f"ℹ️ หมายเหตุ: {u_item['note']}")
        st.write(f"- สถานะปัจจุบัน: **{u_item['status']}**")
        
        if u_item["status"] == "ยังไม่โอน":
            st.subheader("💳 สแกน QR Code ชำระเงิน")
            
            col_qr, col_upload = st.columns([1, 1])
            
            with col_qr:
                if qr_filename:
                    st.image(qr_filename, caption="QR Code สแกนจ่ายเงิน (ฟอร์ด)", use_container_width=True)
                else:
                    st.warning("⚠️ ยังไม่พบรูป QR Code บนระบบ ให้คุณอัปโหลดไฟล์ IMG_7733.jpeg ขึ้น GitHub ได้เลยครับ")
            
            with col_upload:
                uploaded_file = st.file_uploader(f"2. อัปโหลดสลิปสำหรับ {selected_name}", type=["png", "jpg", "jpeg"], key=f"file_{u_item['id']}")
                
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="ตัวอย่างสลิปที่จะแนบ", width=250)
                    if st.button("🚀 ยืนยันการส่งสลิปโอนเงิน", type="primary", key=f"btn_{u_item['id']}"):
                        u_item["status"] = "โอนแล้ว"
                        u_item["slip_url"] = uploaded_file.name
                        save_data(st.session_state.data)
                        st.success("✅ บันทึกสลิปเรียบร้อยแล้ว! สถานะเปลี่ยนเป็น 'โอนแล้ว'")
                        st.rerun()
        else:
            st.success(f"🎉 รายการของ {selected_name} ชำระเงินเรียบร้อยแล้ว ขอบคุณครับ!")

st.divider()

# -------------------------------------------------------------
# Bill Details
# -------------------------------------------------------------
st.header("🧾 รายละเอียดใบเสร็จแยกตามร้าน")
tab1, tab2 = st.tabs(["🍻 ร้าน 2gether (1,740.00 บาท)", "🐯 ร้าน เสือ พุทธบูชา 45 (1,731.00 บาท)"])

with tab1:
    st.write("**วันทำการ:** 03/10/2026 | **ยอดรวม:** 1,740.00 บาท")
    data_2gether = [
        {"รายการ": "ข้าวหมูกระเทียม", "ราคา (บาท)": 104.00, "ผู้หาร/ผู้ทาน": "ฟอร์ด"},
        {"รายการ": "ข้าวไข่ดาว", "ราคา (บาท)": 60.00, "ผู้หาร/ผู้ทาน": "บอส"},
        {"รายการ": "ข้าวผัด (3 จาน)", "ราคา (บาท)": 267.00, "ผู้หาร/ผู้ทาน": "พี่ฟ้า, คิว, นิล"},
        {"รายการ": "Sangsom", "ราคา (บาท)": 480.00, "ผู้หาร/ผู้ทาน": "บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า"},
        {"รายการ": "มิกเซอร์ + น้ำแข็ง + น้ำเปล่า", "ราคา (บาท)": 435.00, "ผู้หาร/ผู้ทาน": "กลุ่มเหล้า 6 คน"},
        {"รายการ": "เอ็นข้อไก่", "ราคา (บาท)": 99.00, "ผู้หาร/ผู้ทาน": "กลุ่มเหล้า 6 คน (ฟอร์ดจ่ายแทน)"},
        {"รายการ": "เบียร์ช้าง 3 ขวด", "ราคา (บาท)": 270.00, "ผู้หาร/ผู้ทาน": "บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า"},
    ]
    st.table(pd.DataFrame(data_2gether))

with tab2:
    st.write("**วันทำการ:** 04/10/2026 | **ยอดรวม:** 1,731.00 บาท")
    data_sueak = [
        {"รายการ": "น้ำแข็ง (4) + น้ำดื่ม (4)", "ราคา (บาท)": 320.00, "ผู้หาร/ผู้ทาน": "หาร 9 คน"},
        {"รายการ": "Sangsom + มิกเซอร์ + ชเวปส์ + เลม่อน", "ราคา (บาท)": 729.00, "ผู้หาร/ผู้ทาน": "ฟอร์ด, ฟ้า, แบงค์, คิว, บอส"},
        {"รายการ": "Soju ลิ้นจี่ (2) + ข้าวไข่เจียว", "ราคา (บาท)": 387.00, "ผู้หาร/ผู้ทาน": "ใหม่"},
        {"รายการ": "Chang คลาสสิค (2)", "ราคา (บาท)": 196.00, "ผู้หาร/ผู้ทาน": "ฟลุ๊ค, เพื่อนฟุ๊ค"},
        {"รายการ": "Singha", "ราคา (บาท)": 99.00, "ผู้หาร/ผู้ทาน": "บอส"},
    ]
    st.table(pd.DataFrame(data_sueak))

st.divider()

# -------------------------------------------------------------
# Summary Table
# -------------------------------------------------------------
st.header("📋 ตารางสรุปสถานะทั้งหมด")

styled_df = df[["name", "amount", "status", "note"]].copy()
styled_df.columns = ["ชื่อ-นามสกุล", "จำนวนเงิน (บาท)", "สถานะการชำระเงิน", "หมายเหตุ"]

def highlight_status(val):
    color = "#d4edda" if val == "โอนแล้ว" else "#f8d7da"
    text_color = "#155724" if val == "โอนแล้ว" else "#721c24"
    return f"background-color: {color}; color: {text_color}; font-weight: bold;"

try:
    st.dataframe(styled_df.style.map(highlight_status, subset=["สถานะการชำระเงิน"]), use_container_width=True)
except AttributeError:
    st.dataframe(styled_df.style.applymap(highlight_status, subset=["สถานะการชำระเงิน"]), use_container_width=True)

with st.expander("⚙️ ตั้งค่าและจัดการรายการ (สำหรับผู้จัดทริป/เจ้าของบิล)"):
    st.subheader("➕ เพิ่มรายการใหม่")
    add_name = st.text_input("ชื่อเพื่อน")
    add_item = st.text_input("รายละเอียดค่าใช้จ่าย")
    add_amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0)
    
    if st.button("เพิ่มรายการ"):
        if add_name and add_item and add_amount > 0:
            new_id = max([item["id"] for item in st.session_state.data], default=0) + 1
            st.session_state.data.append({
                "id": new_id,
                "name": add_name,
                "item": add_item,
                "amount": float(add_amount),
                "status": "ยังไม่โอน",
                "slip_url": None,
                "note": ""
            })
            save_data(st.session_state.data)
            st.success(f"เพิ่มรายการให้ {add_name} สำเร็จ")
            st.rerun()
