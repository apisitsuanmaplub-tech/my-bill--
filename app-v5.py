import streamlit as st
import pandas as pd
import json
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบหารค่าใช้จ่ายปาร์ตี้ & แนบสลิป",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 1. ข้อมูลบิลหลัก (Party Expense Data)
# -------------------------------------------------------------
DATA_FILE = "party_expense_v2.json"

DEFAULT_DATA = [
    {"id": 1, "name": "ฟอร์ด", "amount": 503.53, "status": "โอนแล้ว", "note": "ผู้รับเงิน / เจ้าของบัญชี", "slip_url": None},
    {"id": 2, "name": "ใหม่", "amount": 689.67, "status": "ยังไม่โอน", "note": "ยอดตนเอง 422.56 + สำรองจ่ายแทนฟลุ๊คและเพื่อนฟุ๊ค 267.12", "slip_url": None},
    {"id": 3, "name": "บอส", "amount": 558.53, "status": "ยังไม่โอน", "note": "", "slip_url": None},
    {"id": 4, "name": "พี่ฟ้า", "amount": 488.53, "status": "ยังไม่โอน", "note": "", "slip_url": None},
    {"id": 5, "name": "คิว", "amount": 488.53, "status": "ยังไม่โอน", "note": "", "slip_url": None},
    {"id": 6, "name": "แบงค์", "amount": 399.53, "status": "ยังไม่โอน", "note": "", "slip_url": None},
    {"id": 7, "name": "นิล", "amount": 342.73, "status": "ยังไม่โอน", "note": "", "slip_url": None},
    {"id": 8, "name": "ฟลุ๊ค", "amount": 133.56, "status": "โอนแล้ว", "note": "ใหม่จ่ายสำรองให้เรียบร้อยแล้ว", "slip_url": None},
    {"id": 9, "name": "เพื่อนฟุ๊ค", "amount": 133.56, "status": "โอนแล้ว", "note": "ใหม่จ่ายสำรองให้เรียบร้อยแล้ว", "slip_url": None},
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

# -------------------------------------------------------------
# 2. หัวข้อหลัก
# -------------------------------------------------------------
st.title("💸 ระบบสรุปบิลปาร์ตี้ & แนบสลิปโอนเงิน")
st.markdown("ส่งลิงก์นี้ให้เพื่อนๆ เพื่อเช็กยอดโอน สแกน QR Code ชำระเงิน และแนบสลิปโอนเงินเข้าบัญชี **ฟอร์ด**")

# -------------------------------------------------------------
# 3. สรุปภาพรวมการชำระเงิน
# -------------------------------------------------------------
df = pd.DataFrame(st.session_state.data)
total = df["amount"].sum()
paid = df[df["status"] == "โอนแล้ว"]["amount"].sum()
unpaid = df[df["status"] == "ยังไม่โอน"]["amount"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 ยอดรวมปาร์ตี้ทั้งหมด", f"฿{total:,.2f}")
col2.metric("✅ ชำระแล้ว", f"฿{paid:,.2f}", f"{len(df[df['status'] == 'โอนแล้ว'])} คน")
col3.metric("⏳ รอยอดโอน", f"฿{unpaid:,.2f}", f"{len(df[df['status'] == 'ยังไม่โอน'])} คน", delta_color="inverse")

st.progress(paid / total if total > 0 else 0, text=f"ความคืบหน้าการรับชำระเงิน: {paid/total*100:.1f}%")

# แสดงรายละเอียดใบเสร็จ
with st.expander("🧾 คลิกเพื่อดูรายละเอียดใบเสร็จค่าใช้จ่ายทั้ง 2 ร้าน (2gether & เสือ พุทธบูชา 45)"):
    tab1, tab2 = st.tabs(["ร้าน 2gether (1,740 บาท)", "ร้าน SUEAK PHUTTHABUCHA 45 (1,731 บาท)"])
    with tab1:
        st.write("""
        - ข้าวหมูกระเทียม (104.00) ➔ ฟอร์ด
        - ข้าวไข่ดาว (60.00) ➔ บอส
        - ข้าวผัด 3 จาน (267.00) ➔ พี่ฟ้า, คิว, นิล
        - Sangsom (480.00) ➔ บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า
        - มิกเซอร์ + เครื่องดื่มรวม (540.00) ➔ กลุ่มเหล้า 6 คน
        - เอ็นข้อไก่ (99.00) ➔ กลุ่มเหล้า (ฟอร์ดจ่ายแทน)
        - เบียร์ช้าง 3 ขวด (270.00) ➔ บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า
        """)
    with tab2:
        st.write("""
        - น้ำแข็ง + น้ำดื่ม (320.00) ➔ หาร 9 คน
        - Sangsom + โซดา + โค้ก + ชเวปส์ + PINK เลม่อน (729.00) ➔ ฟอร์ด, ฟ้า, แบงค์, คิว, บอส
        - Soju ลิ้นจี่ (2) + ข้าวไข่เจียว (387.00) ➔ ใหม่
        - Chang คลาสสิค 2 ขวด (196.00) ➔ ฟลุ๊ค, เพื่อนฟุ๊ค
        - Singha (99.00) ➔ บอส
        """)

st.divider()

# -------------------------------------------------------------
# 4. ส่วนสำหรับเพื่อน: เลือกชื่อ -> สแกน QR Code / บัญชี -> อัปโหลดสลิป
# -------------------------------------------------------------
st.header("📲 เลือกชื่อของคุณเพื่อโอนเงิน & แนบสลิป")

all_members = [item["name"] for item in st.session_state.data]
selected_name = st.selectbox("1. เลือกชื่อของคุณจากรายชื่อ:", options=["-- กรุณาเลือกชื่อของคุณ --"] + all_members)

if selected_name != "-- กรุณาเลือกชื่อของคุณ --":
    user_items = [item for item in st.session_state.data if item["name"] == selected_name]
    
    for u_item in user_items:
        st.subheader(f"👤 ข้อมูลการโอนเงินของ: **{selected_name}**")
        
        col_info, col_qr = st.columns([1, 1])
        
        with col_info:
            st.write(f"💵 ยอดเงินที่ต้องโอน: **฿{u_item['amount']:,.2f} บาท**")
            st.write(f"📌 สถานะปัจจุบัน: **{u_item['status']}**")
            if u_item["note"]:
                st.info(f"💡 หมายเหตุ: {u_item['note']}")
        
        with col_qr:
            st.markdown("### 💳 ช่องทางชำระเงิน (ฟอร์ด)")
            
            # ตรวจสอบว่ามีไฟล์รูป QR Code ในระบบหรือไม่
            qr_files = ["qr_code.png", "qr_code.jpg", "qr.png", "qr.jpg", "promptpay.png"]
            found_qr = None
            for qr_f in qr_files:
                if os.path.exists(qr_f):
                    found_qr = qr_f
                    break
            
            if found_qr:
                st.image(found_qr, caption="สแกน QR Code เพื่อโอนเงินให้ ฟอร์ด", width=250)
            else:
                st.warning("📷 หากต้องการแสดงรูป QR Code: เพียงอัปโหลดไฟล์รูป QR Code ชื่อ `qr_code.png` ขึ้น GitHub ในแฟ้มเดียวกับแอป")
                st.info("🏦 **โอนผ่านบัญชี/พร้อมเพย์:**\n\n- **ชื่อบัญชี:** ฟอร์ด\n- **ธนาคาร/พร้อมเพย์:** สามารถระบุเลขบัญชีที่นี่ได้")

        st.divider()

        if u_item["status"] == "ยังไม่โอน":
            uploaded_file = st.file_uploader(f"2. แนบสลิปโอนเงินสำหรับ {selected_name} (ยอด ฿{u_item['amount']:,.2f})", type=["png", "jpg", "jpeg"], key=f"file_{u_item['id']}")
            
            if uploaded_file is not None:
                st.image(uploaded_file, caption="ตัวอย่างสลิปที่เลือก", width=260)
                if st.button("🚀 ยืนยันการส่งสลิปโอนเงิน", type="primary", key=f"btn_{u_item['id']}"):
                    u_item["status"] = "โอนแล้ว"
                    u_item["slip_url"] = uploaded_file.name
                    save_data(st.session_state.data)
                    st.success("✅ บันทึกสลิปเรียบร้อยแล้ว! สถานะเปลี่ยนเป็น 'โอนแล้ว'")
                    st.rerun()
        else:
            st.success("🎉 รายการนี้ชำระเงินเรียบร้อยแล้ว ขอบคุณครับ!")

st.divider()

# -------------------------------------------------------------
# 5. ตารางสรุปสถานะการชำระเงินทั้งหมด
# -------------------------------------------------------------
st.header("📋 ตารางสรุปสถานะการชำระเงินของทุกคน")

styled_df = df[["name", "amount", "status", "note"]].copy()
styled_df.columns = ["ชื่อ-นามสกุล", "จำนวนเงิน (บาท)", "สถานะ", "หมายเหตุ"]

def highlight_status(val):
    color = "#d4edda" if val == "โอนแล้ว" else "#f8d7da"
    text_color = "#155724" if val == "โอนแล้ว" else "#721c24"
    return f"background-color: {color}; color: {text_color}; font-weight: bold;"

try:
    st.dataframe(
        styled_df.style.map(highlight_status, subset=["สถานะ"]),
        use_container_width=True
    )
except AttributeError:
    st.dataframe(
        styled_df.style.applymap(highlight_status, subset=["สถานะ"]),
        use_container_width=True
    )

# -------------------------------------------------------------
# 6. ส่วนผู้ดูแลระบบ
# -------------------------------------------------------------
with st.expander("⚙️ จัดการข้อมูล (สำหรับผู้จัดทริป/ฟอร์ด)"):
    st.subheader("เพิ่ม/แก้ไขรายการ")
    add_name = st.text_input("ชื่อเพื่อน")
    add_amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0)
    add_note = st.text_input("หมายเหตุเพิ่มเติม")
    
    if st.button("เพิ่มรายการใหม่"):
        if add_name and add_amount > 0:
            new_id = max([item["id"] for item in st.session_state.data], default=0) + 1
            st.session_state.data.append({
                "id": new_id,
                "name": add_name,
                "amount": float(add_amount),
                "status": "ยังไม่โอน",
                "note": add_note,
                "slip_url": None
            })
            save_data(st.session_state.data)
            st.success(f"เพิ่มรายการให้ {add_name} สำเร็จ")
            st.rerun()
            
    if st.button("🔄 รีเซ็ตข้อมูลกลับเป็นค่าเริ่มต้น"):
        st.session_state.data = DEFAULT_DATA
        save_data(st.session_state.data)
        st.success("รีเซ็ตข้อมูลเรียบร้อยแล้ว")
        st.rerun()
