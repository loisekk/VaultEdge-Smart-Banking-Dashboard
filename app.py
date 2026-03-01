import streamlit as st
import json
import os
import random
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="NeoBank X",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e0e0e0;
    }

    .main-header {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 47, 247, 0.1));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }

    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 600;
        color: #00d4ff;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .account-card {
        background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
        border: 1px solid rgba(123, 47, 247, 0.4);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .badge-success {
        background: rgba(0, 200, 100, 0.2);
        color: #00c864;
        border: 1px solid rgba(0, 200, 100, 0.3);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
    }

    .badge-danger {
        background: rgba(255, 70, 70, 0.2);
        color: #ff4646;
        border: 1px solid rgba(255, 70, 70, 0.3);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
    }

    .sidebar-info {
        background: rgba(0, 212, 255, 0.1);
        border-left: 3px solid #00d4ff;
        padding: 0.8rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }

    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
    }

    .tx-deposit { color: #00c864; font-weight: 600; }
    .tx-withdraw { color: #ff4646; font-weight: 600; }
    .tx-transfer { color: #ffaa00; font-weight: 600; }

    hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "bank_data.json"
ADMIN_PIN = hashlib.sha256("admin123".encode()).hexdigest()  # Change this!

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------------------------
# HELPERS
# ---------------------------
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_index(data, acc_no):
    return next((i for i, u in enumerate(data) if u.get("accountNo") == acc_no), None)

def add_transaction(user, tx_type, amount, note=""):
    user["transactions"].append({
        "type": tx_type,
        "amount": amount,
        "note": note,
        "date": str(datetime.now())
    })

def format_currency(amount):
    return f"₹ {amount:,.2f}"

def plotly_dark_layout():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#aaa', family='Space Grotesk'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)'),
        margin=dict(l=20, r=20, t=40, b=20)
    )

# ---------------------------
# AUTO DEMO DATA IF EMPTY
# ---------------------------
data = load_data()
if len(data) == 0:
    demo_names = ["Arjun Mehta", "Priya Sharma", "Rohan Das"]
    for i, name in enumerate(demo_names):
        txs = [
            {"type": "Deposit", "amount": random.randint(3000, 8000), "note": "Initial deposit", "date": str(datetime.now())},
            {"type": "Withdraw", "amount": random.randint(500, 2000), "note": "ATM withdrawal", "date": str(datetime.now())}
        ]
        data.append({
            "accountNo": str(1001 + i),
            "name": name,
            "pin": hash_pin("1234"),
            "balance": random.randint(5000, 20000),
            "transactions": txs,
            "created_at": str(datetime.now())
        })
    save_data(data)

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.markdown("## 🏦 NeoBank X")
    st.markdown("---")

    if st.session_state.logged_in:
        user = st.session_state.current_user
        st.markdown(f"""
        <div class="sidebar-info">
            <b>👤 {user['name']}</b><br>
            Acc: <code>{user['accountNo']}</code>
        </div>
        """, unsafe_allow_html=True)
        menu = st.radio("Navigation", ["Dashboard", "Transactions", "Transfer"])
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    else:
        menu = st.radio("Navigation", ["Home", "Login", "Create Account", "Admin"])

    st.markdown("---")
    st.markdown("<small style='color:#555'>NeoBank X v2.0 • Secure Banking</small>", unsafe_allow_html=True)

# ======================================================
# 🏠 HOME
# ======================================================
if menu == "Home" and not st.session_state.logged_in:
    st.markdown('<div class="main-header">Welcome to NeoBank X</div>', unsafe_allow_html=True)
    st.markdown("##### Modern, secure digital banking — built for everyone.")
    st.markdown("")

    data = load_data()
    total_users = len(data)
    total_balance = sum(u["balance"] for u in data)

    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("👥 Total Users", total_users, ""),
        ("💰 Total Deposits", format_currency(sum(t["amount"] for u in data for t in u["transactions"] if t["type"] == "Deposit")), ""),
        ("📤 Total Withdrawals", format_currency(sum(t["amount"] for u in data for t in u["transactions"] if t["type"] in ["Withdraw", "Transfer"])), ""),
        ("🏦 Assets Under Management", format_currency(total_balance), ""),
    ]
    for col, (label, value, delta) in zip([col1, col2, col3, col4], stats):
        col.metric(label, value)

    st.markdown("---")

    # Charts
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("💸 Deposits vs Withdrawals")
        deps = sum(t["amount"] for u in data for t in u["transactions"] if t["type"] == "Deposit")
        wds = sum(t["amount"] for u in data for t in u["transactions"] if t["type"] in ["Withdraw", "Transfer"])
        fig = go.Figure(go.Bar(
            x=["Deposits", "Withdrawals"],
            y=[deps, wds],
            marker_color=["#00d4ff", "#ff4646"],
            text=[format_currency(deps), format_currency(wds)],
            textposition='outside'
        ))
        fig.update_layout(plotly_dark_layout())
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("👤 Balance Distribution")
        names = [u["name"] for u in data]
        bals = [u["balance"] for u in data]
        fig2 = go.Figure(go.Bar(
            x=names, y=bals,
            marker_color="#7b2ff7",
            text=[format_currency(b) for b in bals],
            textposition='outside'
        ))
        fig2.update_layout(plotly_dark_layout())
        st.plotly_chart(fig2, use_container_width=True)

    # Transaction timeline
    st.subheader("📈 Transaction Timeline")
    rows = []
    for u in data:
        for t in u.get("transactions", []):
            try:
                rows.append({
                    "date": datetime.strptime(t["date"], "%Y-%m-%d %H:%M:%S.%f"),
                    "amount": t["amount"] if t["type"] == "Deposit" else -t["amount"],
                    "user": u["name"],
                    "type": t["type"]
                })
            except:
                pass
    if rows:
        df = pd.DataFrame(rows).sort_values("date")
        fig3 = px.line(df, x="date", y="amount", color="user",
                       color_discrete_sequence=["#00d4ff", "#7b2ff7", "#ff6b35"])
        fig3.update_layout(plotly_dark_layout())
        st.plotly_chart(fig3, use_container_width=True)

# ======================================================
# 🔐 LOGIN
# ======================================================
elif menu == "Login" and not st.session_state.logged_in:
    st.markdown('<div class="main-header">User Login</div>', unsafe_allow_html=True)
    st.markdown("##### Access your account securely.")

    col, _ = st.columns([1, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        acc = st.text_input("🔢 Account Number", placeholder="e.g. 1001")
        pin = st.text_input("🔑 PIN", type="password", placeholder="4-digit PIN")

        if st.button("Login →", use_container_width=True, type="primary"):
            data = load_data()
            idx = get_user_index(data, acc)
            if idx is not None and data[idx].get("pin") == hash_pin(pin):
                st.session_state.logged_in = True
                st.session_state.current_user = data[idx]
                st.session_state.current_user_idx = idx
                st.success(f"Welcome back, {data[idx]['name']}! 👋")
                st.rerun()
            else:
                st.error("❌ Invalid account number or PIN.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.info("💡 **Demo Accounts**: Account No: 1001 / 1002 / 1003 | PIN: 1234")

# ======================================================
# 🆕 CREATE ACCOUNT
# ======================================================
elif menu == "Create Account" and not st.session_state.logged_in:
    st.markdown('<div class="main-header">Create Account</div>', unsafe_allow_html=True)

    col, _ = st.columns([1, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        name = st.text_input("👤 Full Name")
        pin = st.text_input("🔑 Set 4-digit PIN", type="password")
        pin2 = st.text_input("🔑 Confirm PIN", type="password")

        if st.button("Create Account →", use_container_width=True, type="primary"):
            if not name or not pin:
                st.error("Please fill all fields.")
            elif len(pin) != 4 or not pin.isdigit():
                st.error("PIN must be exactly 4 digits.")
            elif pin != pin2:
                st.error("PINs do not match.")
            else:
                data = load_data()
                acc_no = str(random.randint(10000, 99999))
                # Ensure uniqueness
                while any(u["accountNo"] == acc_no for u in data):
                    acc_no = str(random.randint(10000, 99999))
                new_user = {
                    "accountNo": acc_no,
                    "name": name,
                    "pin": hash_pin(pin),
                    "balance": 0,
                    "transactions": [],
                    "created_at": str(datetime.now())
                }
                data.append(new_user)
                save_data(data)
                st.success(f"✅ Account created successfully!")
                st.info(f"🔢 Your Account Number: **{acc_no}**")
                st.warning("Save your account number safely. You'll need it to login.")

        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 📊 USER DASHBOARD (Logged In)
# ======================================================
elif menu == "Dashboard" and st.session_state.logged_in:
    data = load_data()
    idx = get_user_index(data, st.session_state.current_user["accountNo"])
    user = data[idx]
    st.session_state.current_user = user  # Refresh

    st.markdown(f'<div class="main-header">Welcome, {user["name"].split()[0]}!</div>', unsafe_allow_html=True)

    # Account card
    st.markdown(f"""
    <div class="account-card">
        <div style="font-size:0.85rem; color:#888; text-transform:uppercase; letter-spacing:0.1em;">Account Number</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:1.5rem; color:#00d4ff; margin:0.3rem 0 1rem;">{user['accountNo']}</div>
        <div style="font-size:0.85rem; color:#888; text-transform:uppercase; letter-spacing:0.1em;">Current Balance</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:2.5rem; font-weight:700; color:#fff;">{format_currency(user['balance'])}</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📥 Deposit")
        dep_amount = st.number_input("Amount to Deposit (₹)", min_value=1, step=100, key="dep")
        dep_note = st.text_input("Note (optional)", key="dep_note", placeholder="e.g. Salary")
        if st.button("Deposit Now", use_container_width=True, type="primary", key="dep_btn"):
            data = load_data()
            idx = get_user_index(data, user["accountNo"])
            data[idx]["balance"] += dep_amount
            add_transaction(data[idx], "Deposit", dep_amount, dep_note or "Deposit")
            save_data(data)
            st.session_state.current_user = data[idx]
            st.success(f"✅ Deposited {format_currency(dep_amount)} successfully!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📤 Withdraw")
        wd_amount = st.number_input("Amount to Withdraw (₹)", min_value=1, step=100, key="wd")
        wd_note = st.text_input("Note (optional)", key="wd_note", placeholder="e.g. ATM")
        if st.button("Withdraw Now", use_container_width=True, key="wd_btn"):
            data = load_data()
            idx = get_user_index(data, user["accountNo"])
            if wd_amount > data[idx]["balance"]:
                st.error("❌ Insufficient balance.")
            else:
                data[idx]["balance"] -= wd_amount
                add_transaction(data[idx], "Withdraw", wd_amount, wd_note or "Withdrawal")
                save_data(data)
                st.session_state.current_user = data[idx]
                st.success(f"✅ Withdrawn {format_currency(wd_amount)} successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent transactions
    if user["transactions"]:
        st.subheader("📜 Recent Transactions")
        df = pd.DataFrame(user["transactions"][::-1][:10])
        df["amount_display"] = df.apply(
            lambda r: f"+{format_currency(r['amount'])}" if r["type"] == "Deposit" else f"-{format_currency(r['amount'])}", axis=1
        )
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y, %H:%M")
        st.dataframe(
            df[["date", "type", "amount_display", "note"]].rename(columns={
                "date": "Date", "type": "Type", "amount_display": "Amount", "note": "Note"
            }),
            use_container_width=True,
            hide_index=True
        )

# ======================================================
# 📜 TRANSACTIONS PAGE
# ======================================================
elif menu == "Transactions" and st.session_state.logged_in:
    data = load_data()
    idx = get_user_index(data, st.session_state.current_user["accountNo"])
    user = data[idx]

    st.markdown('<div class="main-header">Transaction History</div>', unsafe_allow_html=True)

    txs = user.get("transactions", [])
    if not txs:
        st.info("No transactions yet.")
    else:
        df = pd.DataFrame(txs[::-1])
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y, %H:%M")
        df["signed_amount"] = df.apply(
            lambda r: r["amount"] if r["type"] == "Deposit" else -r["amount"], axis=1
        )

        # Summary
        deps = sum(t["amount"] for t in txs if t["type"] == "Deposit")
        wds = sum(t["amount"] for t in txs if t["type"] in ["Withdraw", "Transfer"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Deposits", format_currency(deps))
        col2.metric("Total Withdrawals", format_currency(wds))
        col3.metric("Net Flow", format_currency(deps - wds))

        # Chart
        fig = px.bar(df, x="date", y="signed_amount",
                     color=df["signed_amount"].apply(lambda x: "Deposit" if x > 0 else "Withdrawal"),
                     color_discrete_map={"Deposit": "#00d4ff", "Withdrawal": "#ff4646"},
                     labels={"signed_amount": "Amount (₹)", "date": "Date"})
        fig.update_layout(plotly_dark_layout(), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Filter
        tx_filter = st.selectbox("Filter by Type", ["All", "Deposit", "Withdraw", "Transfer"])
        display_df = df if tx_filter == "All" else df[df["type"] == tx_filter]
        st.dataframe(
            display_df[["date", "type", "amount", "note"]].rename(columns={
                "date": "Date", "type": "Type", "amount": "Amount (₹)", "note": "Note"
            }),
            use_container_width=True,
            hide_index=True
        )

# ======================================================
# 💸 TRANSFER PAGE
# ======================================================
elif menu == "Transfer" and st.session_state.logged_in:
    data = load_data()
    idx = get_user_index(data, st.session_state.current_user["accountNo"])
    user = data[idx]

    st.markdown('<div class="main-header">Transfer Funds</div>', unsafe_allow_html=True)
    st.metric("Your Balance", format_currency(user["balance"]))

    col, _ = st.columns([1, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        to_acc = st.text_input("🔢 Recipient Account Number")
        amount = st.number_input("💸 Amount to Transfer (₹)", min_value=1, step=100)
        note = st.text_input("📝 Note", placeholder="e.g. Rent payment")

        if st.button("Transfer Now →", use_container_width=True, type="primary"):
            data = load_data()
            sender_idx = get_user_index(data, user["accountNo"])
            receiver_idx = get_user_index(data, to_acc)

            if to_acc == user["accountNo"]:
                st.error("❌ Cannot transfer to your own account.")
            elif receiver_idx is None:
                st.error("❌ Recipient account not found.")
            elif amount > data[sender_idx]["balance"]:
                st.error("❌ Insufficient balance.")
            else:
                receiver = data[receiver_idx]
                # Debit sender
                data[sender_idx]["balance"] -= amount
                add_transaction(data[sender_idx], "Transfer",
                                amount, f"To {receiver['name']} ({to_acc}) — {note or 'Transfer'}")
                # Credit receiver
                data[receiver_idx]["balance"] += amount
                add_transaction(data[receiver_idx], "Deposit",
                                amount, f"From {user['name']} ({user['accountNo']}) — {note or 'Transfer'}")
                save_data(data)
                st.session_state.current_user = data[sender_idx]
                st.success(f"✅ Transferred {format_currency(amount)} to **{receiver['name']}** successfully!")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 👨‍💼 ADMIN
# ======================================================
elif menu == "Admin":
    st.markdown('<div class="main-header">Admin Panel</div>', unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        col, _ = st.columns([1, 1])
        with col:
            admin_pass = st.text_input("🔑 Admin Password", type="password")
            if st.button("Access Admin →", use_container_width=True, type="primary"):
                if hashlib.sha256(admin_pass.encode()).hexdigest() == ADMIN_PIN:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Invalid admin password.")
        st.info("Default admin password: **admin123**")
    else:
        if st.button("🚪 Admin Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        data = load_data()

        # Summary
        total_bal = sum(u["balance"] for u in data)
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Users", len(data))
        col2.metric("💰 Total Balance", format_currency(total_bal))
        col3.metric("📊 Avg Balance", format_currency(total_bal / len(data) if data else 0))

        st.markdown("---")
        st.subheader("👥 All Accounts")

        # Safe display — no raw PINs
        display_data = [{
            "Account No": u["accountNo"],
            "Name": u["name"],
            "Balance (₹)": u["balance"],
            "Transactions": len(u.get("transactions", [])),
            "Joined": u.get("created_at", "N/A")[:10] if u.get("created_at") else "N/A"
        } for u in data]

        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🗑️ Delete Account")
        acc_to_delete = st.selectbox("Select Account to Delete",
                                     [f"{u['accountNo']} - {u['name']}" for u in data])
        if st.button("Delete Account", type="secondary"):
            acc_no = acc_to_delete.split(" - ")[0]
            data = [u for u in data if u["accountNo"] != acc_no]
            save_data(data)
            st.success(f"Account {acc_no} deleted.")
            st.rerun()

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#444; font-size:0.8rem;'>🏦 NeoBank X v2.0 • Secure Digital Banking • Built with Streamlit</div>",
    unsafe_allow_html=True
)