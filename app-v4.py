import streamlit as st
import pandas as pd
import json
import os

# ตั้งค่าหน้าเว็บให้รองรับทั้ง Mobile และ Desktop
st.set_page_config(
    page_title="สรุปบิลปาร์ตี้ & แนบสลิปโอนเงิน",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "party_data.json"

# ข้อมูลจาก JSON
INITIAL_PARTY_DATA = {
    "total_amount": 3471.00,
    "stores": [
        {
            "store_name": "2gether",
            "date": "03/10/2026",
            "total": 1740.00,
            "items": [
                {"name": "ข้าวหมูกระเทียม", "price": 104.00, "consumer": "ฟอร์ด"},
                {"name": "ข้าวไข่ดาว", "price": 60.00, "consumer": "บอส"},
                {"name": "ข้าวผัด (3 จาน)", "price": 267.00, "consumer": "พี่ฟ้า, คิว, นิล"},
                {"name": "Sangsom", "price": 480.00, "consumer": "บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า"},
                {"name": "สไปรท์ (6)", "price": 150.00, "consumer": "กลุ่มเหล้า 6 คน"},
                {"name": "โค้ก (4)", "price": 100.00, "consumer": "กลุ่มเหล้า 6 คน"},
                {"name": "โซดา (1)", "price": 25.00, "consumer": "กลุ่มเหล้า 6 คน"},
                {"name": "น้ำแข็งถังใหญ่ (2)", "price": 120.00, "consumer": "กลุ่มเหล้า 6 คน"},
                {"name": "น้ำแข็งถังเล็ก (1)", "price": 40.00, "consumer": "กลุ่มเหล้า 6 คน"},
                {"name": "น้ำเปล่า (1)", "price": 25.00, "consumer": "กลุ่มเหล้า 6 คน"},
                {"name": "เอ็นข้อไก่", "price": 99.00, "consumer": "กลุ่มเหล้า 6 คน (ฟอร์ดจ่ายแทน)"},
                {"name": "เบียร์ช้าง 3 ขวด", "price": 270.00, "consumer": "บอส, ฟอร์ด, นิล, คิว, แบงค์, พี่ฟ้า"}
            ]
        },
        {
            "store_name": "SUEAK PHUTTHABUCHA 45",
            "date": "04/10/2026",
            "total": 1731.00,
            "items": [
                {"name": "น้ำแข็ง (4)", "price": 200.00, "consumer": "หาร 9 คน"},
                {"name": "น้ำดื่ม (4)", "price": 120.00, "consumer": "หาร 9 คน"},
                {"name": "Sangsom", "price": 459.00, "consumer": "ฟอร์ด, ฟ้า, แบงค์, คิว, บอส"},
                {"name": "โซดา", "price": 30.00, "consumer": "ฟอร์ด, ฟ้า, แบงค์, คิว, บอส"},
                {"name": "โค้ก (4)", "price": 120.00, "consumer": "ฟอร์ด, ฟ้า, แบงค์, คิว, บอส"},
                {"name": "ชเวปส์ (3)", "price": 90.00, "consumer": "ฟอร์ด, ฟ้า, แบงค์, คิว, บอส"},
                {"name": "PINK เลม่อน", "price": 30.00, "consumer": "ฟอร์ด, ฟ้า, แบงค์, คิว, บอส"},
                {"name": "Soju ลิ้นจี่ (2)", "price": 318.00, "consumer": "ใหม่"},
                {"name": "ข้าวไข่เจียว", "price": 69.00, "consumer": "ใหม่"},
                {"name": "Chang คลาสสิค (2)", "price": 196.00, "consumer": "ฟลุ๊ค, เพื่อนฟุ๊ค"},
                {"name": "Singha", "price": 99.00, "consumer": "บอส"}
            ]
        }
    ],
    "members": [
        {"id": 1, "name": "ใหม่", "amount": 689.67, "status": "ยังไม่โอน", "note": "ยอดตนเอง 422.56 + สำรองจ่ายแทนฟลุ๊คและเพื่อนฟุ๊ค 267.12 บาท", "slip": None},
        {"id": 2, "name": "นิล", "amount": 342.73, "status": "ยังไม่โอน", "note": "", "slip": None},
        {"id": 3, "name": "แบงค์", "amount": 399.53, "status": "ยังไม่โอน", "note": "", "slip": None},
        {"id": 4, "name": "พี่ฟ้า", "amount": 488.53, "status": "ยังไม่โอน", "note": "", "slip": None},
        {"id": 5, "name": "คิว", "amount": 488.53, "status": "ยังไม่โอน", "note": "", "slip": None},
        {"id": 6, "name": "บอส", "amount": 558.53, "status": "ยังไม่โอน", "note": "", "slip": None},
        {"id": 7, "name": "ฟลุ๊ค", "amount": 133.56, "status": "โอนแล้ว (ใหม่สำรอง)", "note": "ใหม่จ่ายสำรองให้แล้ว (โอนคืนใหม่)", "slip": None},
        {"id": 8, "name": "เพื่อนฟุ๊ค", "amount": 133.56, "status": "โอนแล้ว (ใหม่สำรอง)", "note": "ใหม่จ่ายสำรองให้แล้ว (โอนคืนใหม่)", "slip": None},
        {"id": 9, "name": "ฟอร์ด", "amount": 503.53, "status": "ผู้รับเงิน (ไม่ต้องโอน)", "note": "เจ้าของบัญชีผู้รับเงิน", "slip": None}
    ]
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return INITIAL_PARTY_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "party" not in st.session_state:
    st.session_state.party = load_data()

party_data = st.session_state.party

# -------------------------------------------------------------
# Header
# -------------------------------------------------------------
st.title("🍺 ระบบสรุปบิลหารค่าใช้จ่าย & แนบสลิปโอนเงิน")
st.markdown("สรุปรายการค่าใช้จ่าย 2 ร้าน **(2gether & SUEAK PHUTTHABUCHA 45)** ยอดรวม **3,471.00 บาท**")

# Metrics Overview
members_df = pd.DataFrame(party_data["members"])
total_amount = party_data["total_amount"]

# บัญชีที่ต้องโอนหลักคือ ฟอร์ด
payable_members = members_df[~members_df["status"].isin(["ผู้รับเงิน (ไม่ต้องโอน)", "โอนแล้ว (ใหม่สำรอง)"])]
paid_df = members_df[members_df["status"] == "โอนแล้ว"]
paid_sum = paid_df["amount"].sum() if not paid_df.empty else 0.0
unpaid_count = len(payable_members[payable_members["status"] == "ยังไม่โอน"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 ยอดรวมปาร์ตี้ทั้งหมด", f"฿{total_amount:,.2f}")
c2.metric("💳 ยอดต้องเก็บเข้าฟอร์ด", f"฿2,967.47")
c3.metric("✅ โอนเรียบร้อยแล้ว", f"฿{paid_sum:,.2f}")
c4.metric("⏳ ยังรอโอน", f"{unpaid_count} คน")

progress_val = min(1.0, max(0.0, paid_sum / 2967.47)) if 2967.47 > 0 else 0.0
st.progress(progress_val, text=f"ความคืบหน้าการโอนเข้าฟอร์ด: {progress_val*100:.1f}%")

st.divider()

# -------------------------------------------------------------
# 1. ส่วนสำหรับเพื่อนแนบสลิป
# -------------------------------------------------------------
st.header("📲 เลือกชื่อของคุณเพื่อดูยอด และแนบสลิปโอนเงิน")

member_names = members_df["name"].tolist()
selected_user = st.selectbox("1. เลือกชื่อของคุณ:", options=["-- เลือกชื่อ --"] + member_names)

if selected_user != "-- เลือกชื่อ --":
    user_info = members_df[members_df["name"] == selected_user].iloc[0]
    
    st.subheader(f"👤 ข้อมูลการโอนของ: {user_info['name']}")
    col_u1, col_u2 = st.columns([1, 2])
    
    with col_u1:
        st.metric("ยอดที่ต้องโอน", f"฿{user_info['amount']:,.2f}")
        st.write(f"**สถานะ:** {user_info['status']}")
        if user_info['note']:
            st.info(f"💡 **หมายเหตุ:** {user_info['note']}")
            
    with col_u2:
        if user_info["status"] == "ยังไม่โอน":
            st.write("📥 **แนบรูปสลิปโอนเงิน:**")
            uploaded_file = st.file_uploader("เลือกไฟล์รูปสลิป (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key=f"file_{user_info['id']}")
            
            if uploaded_file is not None:
                st.image(uploaded_file, caption="ตัวอย่างสลิปโอนเงิน", width=250)
                if st.button("🚀 ยืนยันการอัปโหลดและเปลี่ยนสถานะเป็น 'โอนแล้ว'", type="primary"):
                    # อัปเดตข้อมูล
                    for m in st.session_state.party["members"]:
                        if m["name"] == selected_user:
                            m["status"] = "โอนแล้ว"
                            m["slip"] = uploaded_file.name
                    save_data(st.session_state.party)
                    st.success("✅ บันทึกสลิปเรียบร้อยแล้ว! ขอบคุณครับ")
                    st.rerun()
        elif user_info["status"] == "โอนแล้ว":
            st.success("🎉 คุณได้อัปโหลดสลิปเรียบร้อยแล้ว ขอบคุณครับ!")
        else:
            st.info(f"ℹ️ {user_info['note']}")

st.divider()

# -------------------------------------------------------------
# 2. ตารางสรุปยอดรายบุคคล
# -------------------------------------------------------------
st.header("📋 ตารางสรุปยอดเงินและสถานะรายบุคคล")

styled_members = members_df[["name", "amount", "status", "note"]].copy()
styled_members.columns = ["ชื่อเพื่อน", "ยอดเงินที่ต้องโอน (บาท)", "สถานะการชำระเงิน", "หมายเหตุเพิ่มเติม"]

def highlight(val):
    if val == "โอนแล้ว":
        return "background-color: #d4edda; color: #155724; font-weight: bold;"
    elif val == "ยังไม่โอน":
        return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
    else:
        return "background-color: #e2e3e5; color: #383d41; font-style: italic;"

try:
    st.dataframe(styled_members.style.map(highlight, subset=["สถานะการชำระเงิน"]), use_container_width=True)
except AttributeError:
    st.dataframe(styled_members.style.applymap(highlight, subset=["สถานะการชำระเงิน"]), use_container_width=True)

st.divider()

# -------------------------------------------------------------
# 3. รายละเอียดใบเสร็จแยกตามร้าน
# -------------------------------------------------------------
st.header("🧾 รายละเอียดรายการอาหาร/เครื่องดื่ม 2 ร้าน")

tab1, tab2 = st.tabs(["ร้าน 1: 2gether (1,740.00 บาท)", "ร้าน 2: SUEAK PHUTTHABUCHA 45 (1,731.00 บาท)"])

with tab1:
    st.subheader("📍 ร้าน 2gether (วันที่ 03/10/2026)")
    df_store1 = pd.DataFrame(party_data["stores"][0]["items"])
    df_store1.columns = ["รายการอาหาร/เครื่องดื่ม", "ราคา (บาท)", "ผู้หาร / ผู้ทาน"]
    st.table(df_store1)

with tab2:
    st.subheader("📍 ร้าน SUEAK PHUTTHABUCHA 45 (วันที่ 04/10/2026)")
    df_store2 = pd.DataFrame(party_data["stores"][1]["items"])
    df_store2.columns = ["รายการอาหาร/เครื่องดื่ม", "ราคา (บาท)", "ผู้หาร / ผู้ทาน"]
    st.table(df_store2)

# Reset option
with st.expander("⚙️ รีเซ็ตข้อมูล"):
    if st.button("รีเซ็ตสถานะเป็นค่าเริ่มต้น"):
        st.session_state.party = INITIAL_PARTY_DATA
        save_data(INITIAL_PARTY_DATA)
        st.success("รีเซ็ตเรียบร้อยแล้ว")
        st.rerun()
