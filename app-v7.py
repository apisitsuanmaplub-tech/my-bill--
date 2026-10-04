import streamlit as st
import pandas as pd
from PIL import Image
import os
import json

st.set_page_config(
    page_title="ระบบหารค่าใช้จ่าย ปาร์ตี้",
    page_icon="🍻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# ข้อมูลการจ่ายเงินและสมาชิก
# -------------------------------------------------------------
DATA_FILE = "party_data_v7.json"

def get_initial_data():
    return [
        {"id": 1, "name": "บอส", "item": "ค่าอาหาร/เครื่องดื่ม (2ร้าน)", "amount": 558.53, "status": "ยังไม่โอน", "note": "รวม Singha + หารเหล้า/อาหาร", "slip": None},
        {"id": 2, "name": "ฟอร์ด", "item": "ค่าอาหาร/เครื่องดื่ม (ผู้รับเงิน)", "amount": 503.53, "status": "โอนแล้ว", "note": "ผู้รับเงินโอนเข้าบัญชี", "slip": None},
        {"id": 3, "name": "พี่ฟ้า", "item": "ค่าอาหาร/เครื่องดื่ม (2ร้าน)", "amount": 488.53, "status": "ยังไม่โอน", "note": "หารเหล้า/โซดา/น้ำแข็ง/ข้าวผัด", "slip": None},
        {"id": 4, "name": "คิว", "item": "ค่าอาหาร/เครื่องดื่ม (2ร้าน)", "amount": 488.53, "status": "ยังไม่โอน", "note": "หารเหล้า/โซดา/น้ำแข็ง/ข้าวผัด", "slip": None},
        {"id": 5, "name": "ใหม่", "item": "ค่าอาหาร/เครื่องดื่ม (ร้านเสือ/2gether)", "amount": 422.56, "status": "ยังไม่โอน", "note": "Soju + ข้าวไข่เจียว + หารน้ำ/น้ำแข็ง 9 คน", "slip": None},
        {"id": 6, "name": "แบงค์", "item": "ค่าอาหาร/เครื่องดื่ม (2ร้าน)", "amount": 399.53, "status": "ยังไม่โอน", "note": "หารเหล้า/โซดา/น้ำแข็ง", "slip": None},
        {"id": 7, "name": "นิล", "item": "ค่าอาหาร/เครื่องดื่ม (ร้าน 2gether)", "amount": 342.73, "status": "ยังไม่โอน", "note": "หาร Sangsom/ข้าวผัด/เบียร์ช้าง", "slip": None},
        {"id": 8, "name": "ฟลุ๊ค", "item": "ค่าเครื่องดื่ม (Chang คลาสสิค)", "amount": 133.56, "status": "ยังไม่โอน", "note": "Chang คลาสสิค + หารน้ำ/น้ำแข็ง 9 คน", "slip": None},
        {"id": 9, "name": "เพื่อนฟลุ๊ค", "item": "ค่าเครื่องดื่ม (Chang คลาสสิค)", "amount": 133.56, "status": "ยังไม่โอน", "note": "Chang คลาสสิค + หารน้ำ/น้ำแข็ง 9 คน", "slip": None},
    ]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return get_initial_data()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "party_data" not in st.session_state:
    st.session_state.party_data = load_data()

data = st.session_state.party_data

# -------------------------------------------------------------
# หน้าหลัก
# -------------------------------------------------------------
st.title("🎉 สรุปยอดหารค่าใช้จ่ายปาร์ตี้ & แนบสลิป")
st.markdown("ยอดรวมทั้งหมด **3,471.00 บาท** (ร้าน 2gether + ร้านเสือ พุทธบูชา 45)")

# คำนวณสรุป
df = pd.DataFrame(data)
total_amt = df["amount"].sum()
paid_amt = df[df["status"] == "โอนแล้ว"]["amount"].sum()
unpaid_amt = df[df["status"] == "ยังไม่โอน"]["amount"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("💰 ยอดรวมทั้งทริป", f"฿{total_amt:,.2f}")
c2.metric("✅ โอนแล้ว", f"฿{paid_amt:,.2f}", f"{len(df[df['status']=='โอนแล้ว'])} คน")
c3.metric("⏳ ยังไม่โอน", f"฿{unpaid_amt:,.2f}", f"{len(df[df['status']=='ยังไม่โอน'])} คน", delta_color="inverse")

st.progress(paid_amt / total_amt if total_amt > 0 else 0, text=f"ความคืบหน้า: {paid_amt/total_amt*100:.1f}%")

st.divider()

# -------------------------------------------------------------
# ส่วนเลือกชื่อและแนบสลิป
# -------------------------------------------------------------
st.header("📲 เลือกชื่อของคุณเพื่อดูยอด & สแกนชำระเงิน")

names_list = [item["name"] for item in data]
selected_person = st.selectbox("1. เลือกชื่อของคุณจากรายการ:", ["-- เลือกชื่อของคุณ --"] + names_list)

if selected_person != "-- เลือกชื่อของคุณ --":
    person_info = next((item for item in data if item["name"] == selected_person), None)
    if person_info:
        st.info(f"👤 ข้อมูลการชำระเงินของ: **{person_info['name']}**")
        
        col_info, col_qr = st.columns([2, 1])
        
        with col_info:
            st.write(f"📌 รายการ: **{person_info['item']}**")
            st.write(f"💵 ยอดที่ต้องโอน: **฿{person_info['amount']:,.2f} บาท**")
            st.write(f"📝 หมายเหตุ: {person_info['note']}")
            
            # สีสถานะ
            if person_info["status"] == "โอนแล้ว":
                st.success("🟢 สถานะ: **โอนแล้ว เรียบร้อยแล้ว ขอบคุณครับ!**")
            else:
                st.error("🔴 สถานะ: **ยังไม่โอน**")
                
        with col_qr:
            st.markdown("### 📱 QR Code สำหรับสแกนจ่าย")
            # ค้นหาไฟล์ QR Code ที่อาจมีในโฟลเดอร์
            qr_files = ["IMG_7733.jpeg", "IMG_7733.JPG", "IMG_7733.jpg", "IMG_7733.JPEG", "qr_code.png", "qr.png", "qr.jpg"]
            found_qr = None
            for qf in qr_files:
                if os.path.exists(qf):
                    found_qr = qf
                    break
            
            if found_qr:
                st.image(found_qr, caption="สแกนโอนเงินเข้าบัญชีฟอร์ด", use_container_width=True)
            else:
                st.warning("⚠️ หากรูป QR Code ยังไม่แสดง โปรดตรวจสอบว่าได้อัปโหลดไฟล์ `IMG_7733.jpeg` ขึ้น GitHub แล้วหรือไม่")

        st.divider()
        
        if person_info["status"] == "ยังไม่โอน":
            uploaded_file = st.file_uploader(f"2. อัปโหลดสลิปโอนเงินสำหรับ {person_info['name']}", type=["png", "jpg", "jpeg"], key=f"file_{person_info['id']}")
            if uploaded_file is not None:
                st.image(uploaded_file, caption="ตัวอย่างสลิปที่จะส่ง", width=250)
                if st.button("🚀 ยืนยันการส่งสลิปโอนเงิน", type="primary", key=f"btn_{person_info['id']}"):
                    person_info["status"] = "โอนแล้ว"
                    person_info["slip"] = uploaded_file.name
                    save_data(data)
                    st.success("✅ บันทึกสลิปเรียบร้อยแล้ว! สถานะเปลี่ยนเป็น 'โอนแล้ว'")
                    st.rerun()

st.divider()

# -------------------------------------------------------------
# ตารางสรุปทุกคน
# -------------------------------------------------------------
st.header("📋 ตารางสรุปสถานะการชำระเงินของทุกคน")

styled_df = df[["name", "amount", "status", "note"]].copy()
styled_df.columns = ["ชื่อ", "ยอดเงิน (บาท)", "สถานะ", "รายละเอียด/หมายเหตุ"]

def highlight_status(val):
    if val == "โอนแล้ว":
        return "background-color: #d4edda; color: #155724; font-weight: bold;"
    return "background-color: #f8d7da; color: #721c24; font-weight: bold;"

try:
    st.dataframe(styled_df.style.map(highlight_status, subset=["สถานะ"]), use_container_width=True)
except AttributeError:
    st.dataframe(styled_df.style.applymap(highlight_status, subset=["สถานะ"]), use_container_width=True)

# -------------------------------------------------------------
# รายละเอียดใบเสร็จ 2 ร้าน
# -------------------------------------------------------------
with st.expander("🧾 คลิกเพื่อดูรายละเอียดใบเสร็จค่าใช้จ่ายทั้ง 2 ร้าน"):
    st.subheader("1. ร้าน 2gether (ยอดรวม 1,740.00 บาท)")
    st.markdown("""
    - ข้าวหมูกระเทียม (104.-) -> ฟอร์ด
    - ข้าวไข่ดาว (60.-) -> บอส
    - ข้าวผัด 3 จาน (267.-) -> พี่ฟ้า, คิว, นิล
    - Sangsom (480.-) -> บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า
    - มิกเซอร์ (สไปร์ท/โค้ก/โซดา/น้ำแข็ง/น้ำเปล่า) (435.-) -> กลุ่มเหล้า 6 คน
    - เอ็นข้อไก่ (99.-) -> กลุ่มเหล้า
    - เบียร์ช้าง 3 ขวด (270.-) -> บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า
    """)
    
    st.subheader("2. ร้าน SUEAK PHUTTHABUCHA 45 (ยอดรวม 1,731.00 บาท)")
    st.markdown("""
    - น้ำแข็ง 4 ถัง + น้ำดื่ม 4 ขวด (320.-) -> หารเท่า 9 คน (คนละ 35.56.-)
    - Sangsom + มิกเซอร์ (โค้ก/ชเวปส์/โซดา/เลม่อน) (729.-) -> ฟอร์ด, พี่ฟ้า, แบงค์, คิว, บอส
    - Soju ลิ้นจี่ 2 ขวด + ข้าวไข่เจียว (387.-) -> ใหม่
    - Chang คลาสสิค 2 ขวด (196.-) -> ฟลุ๊ค, เพื่อนฟลุ๊ค
    - Singha (99.-) -> บอส
    """)
