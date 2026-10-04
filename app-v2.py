import streamlit as st
import pandas as pd
from PIL import Image
import io
import json
import os

# ตั้งค่าหน้าเว็บให้รองรับการใช้งานบนมือถือและคอมพิวเตอร์
st.set_page_config(
    page_title="ระบบหารค่าใช้จ่าย & แจ้งโอนเงิน",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 1. การจัดการข้อมูล (Data Persistence)
# -------------------------------------------------------------
# ไฟล์เก็บข้อมูลแบบป้อนกลับเรียลไทม์ (เมื่อนำไปปรับใช้กับ Cloud Database เช่น Google Sheets หรือ Supabase จะซิงค์ข้ามเครื่องทันที)
DATA_FILE = "expense_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # ข้อมูลตัวอย่างเริ่มต้น (สามารถแก้ไขเป็นรายชื่อจริงได้)
    return [
        {"id": 1, "name": "เพื่อน A", "item": "ค่าอาหารเย็น", "amount": 350.0, "status": "ยังไม่โอน", "slip_url": None},
        {"id": 2, "name": "เพื่อน B", "item": "ค่าอาหารเย็น", "amount": 350.0, "status": "โอนแล้ว", "slip_url": "https://via.placeholder.com/150"},
        {"id": 3, "name": "เพื่อน C", "item": "ค่าที่พัก", "amount": 500.0, "status": "ยังไม่โอน", "slip_url": None},
        {"id": 4, "name": "เพื่อน D", "item": "ค่าที่พัก", "amount": 500.0, "status": "ยังไม่โอน", "slip_url": None},
    ]

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# -------------------------------------------------------------
# 2. หัวข้อหลักของเว็บ
# -------------------------------------------------------------
st.title("💸 ระบบหารค่าใช้จ่าย & แนบสลิปออนไลน์")
st.markdown("ส่งลิงก์นี้ให้เพื่อนๆ เพื่อตรวจสอบยอดที่ต้องชำระ แนบสลิปโอนเงิน และดูสถานะได้แบบเรียลไทม์")

# -------------------------------------------------------------
# 3. สรุปภาพรวมการชำระเงิน (Real-time Overview)
# -------------------------------------------------------------
df = pd.DataFrame(st.session_state.data)

total = df["amount"].sum()
paid = df[df["status"] == "โอนแล้ว"]["amount"].sum()
unpaid = df[df["status"] == "ยังไม่โอน"]["amount"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 ยอดรวมทั้งหมด", f"฿{total:,.2f}")
col2.metric("✅ โอนแล้ว", f"฿{paid:,.2f}", f"{len(df[df['status'] == 'โอนแล้ว'])} คน")
col3.metric("⏳ ยังไม่โอน", f"฿{unpaid:,.2f}", f"{len(df[df['status'] == 'ยังไม่โอน'])} คน", delta_color="inverse")

st.progress(paid / total if total > 0 else 0, text=f"ความคืบหน้าการชำระเงิน: {paid/total*100:.1f}%")

st.divider()

# -------------------------------------------------------------
# 4. ส่วนสำหรับเพื่อน: เลือกชื่อตนเอง -> ดูยอด -> อัปโหลดสลิป
# -------------------------------------------------------------
st.header("📲 ช่องทางสำหรับเพื่อน: แนบสลิปโอนเงิน")

unpaid_members = [item["name"] for item in st.session_state.data if item["status"] == "ยังไม่โอน"]
all_members = [item["name"] for item in st.session_state.data]

selected_name = st.selectbox("1. เลือกชื่อของคุณจากรายการ:", options=["-- เลือกชื่อของคุณ --"] + all_members)

if selected_name != "-- เลือกชื่อของคุณ --":
    user_items = [item for item in st.session_state.data if item["name"] == selected_name]
    
    st.info(f"👤 ข้อมูลของ **{selected_name}**")
    for u_item in user_items:
        st.write(f"- รายการ: **{u_item['item']}** | ยอดที่ต้องโอน: **฿{u_item['amount']:,.2f}** | สถานะปัจจุบัน: **{u_item['status']}**")
        
        if u_item["status"] == "ยังไม่โอน":
            uploaded_file = st.file_uploader(f"2. อัปโหลดสลิปสำหรับรายการ '{u_item['item']}'", type=["png", "jpg", "jpeg"], key=f"file_{u_item['id']}")
            
            if uploaded_file is not None:
                st.image(uploaded_file, caption="ตัวอย่างสลิปที่จะแนบ", width=250)
                if st.button("🚀 ยืนยันการส่งสลิปโอนเงิน", type="primary", key=f"btn_{u_item['id']}"):
                    # อัปเดตสถานะ
                    u_item["status"] = "โอนแล้ว"
                    u_item["slip_url"] = uploaded_file.name
                    save_data(st.session_state.data)
                    st.success("✅ บันทึกสลิปเรียบร้อยแล้ว! สถานะเปลี่ยนเป็น 'โอนแล้ว'")
                    st.rerun()
        else:
            st.success("🎉 รายการนี้คุณโอนเงินเรียบร้อยแล้ว ขอบคุณครับ!")

st.divider()

# -------------------------------------------------------------
# 5. ตารางสรุปสถานะการชำระเงินทั้งหมด
# -------------------------------------------------------------
st.header("📋 ตารางสรุปสถานะทั้งหมด")

# ปรับแต่งตารางเพื่อความสวยงาม
styled_df = df[["name", "item", "amount", "status"]].copy()
styled_df.columns = ["ชื่อ-นามสกุล", "รายการค่าใช้จ่าย", "จำนวนเงิน (บาท)", "สถานะการชำระเงิน"]

def highlight_status(val):
    color = "#d4edda" if val == "โอนแล้ว" else "#f8d7da"
    text_color = "#155724" if val == "โอนแล้ว" else "#721c24"
    return f"background-color: {color}; color: {text_color}; font-weight: bold;"

st.dataframe(
    styled_df.style.applymap(highlight_status, subset=["สถานะการชำระเงิน"]),
    use_container_width=True
)

# -------------------------------------------------------------
# 6. ส่วนสำหรับผู้ดูแลระบบ (Admin)
# -------------------------------------------------------------
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
                "slip_url": None
            })
            save_data(st.session_state.data)
            st.success(f"เพิ่มรายการให้ {add_name} สำเร็จ")
            st.rerun()
