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
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: #080c14;
        color: #e0e0e0;
    }

    .main-header {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }

    .account-card {
        background: linear-gradient(135deg, #0f1729 0%, #1a1f3a 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .account-card::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 180px; height: 180px;
        background: radial-gradient(circle, rgba(129, 140, 248, 0.15), transparent 70%);
        border-radius: 50%;
    }

    .sidebar-info {
        background: rgba(56, 189, 248, 0.08);
        border-left: 3px solid #38bdf8;
        padding: 0.8rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }

    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-family: 'DM Mono', monospace !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.02em !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.25) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        font-family: 'Syne', sans-serif !important;
    }

    .stDataFrame { border-radius: 12px; overflow: hidden; }

    hr { border-color: rgba(255,255,255,0.07) !important; }

    .confirm-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "bank_data.json"
# ⚠️  Change this before deploying — store as env var in production
ADMIN_PIN_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# ---------------------------
# SESSION STATE INIT
# ---------------------------
for key, default in [
    ("logged_in", False),
    ("current_acc", None),       # Only store account number — always re-fetch from file
    ("admin_logged_in", False),
    ("confirm_delete_admin", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------
# DATA HELPERS
# ---------------------------
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def load_data() -> list:
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data: list):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_index(data: list, acc_no: str) -> int | None:
    """Return index of the user with the given account number, or None."""
    return next((i for i, u in enumerate(data) if u.get("accountNo") == acc_no), None)

def get_current_user(data: list) -> dict | None:
    """Always fetch fresh user object from loaded data using session account number."""
    acc = st.session_state.current_acc
    if acc is None:
        return None
    idx = get_user_index(data, acc)
    return data[idx] if idx is not None else None

def add_transaction(user: dict, tx_type: str, amount: float, note: str = ""):
    user.setdefault("transactions", []).append({
        "type": tx_type,
        "amount": amount,
        "note": note,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    })

def format_currency(amount: float) -> str:
    return f"₹ {amount:,.2f}"

def plotly_dark_layout() -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aaa", family="Syne"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
        margin=dict(l=20, r=20, t=40, b=20),
    )

def safe_parse_date(date_str: str) -> datetime | None:
    """Try multiple datetime formats; return None on failure."""
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

# ---------------------------
# SEED DEMO DATA IF EMPTY
# ---------------------------
_data = load_data()
if not _data:
    demo_names = ["Arjun Mehta", "Priya Sharma", "Rohan Das"]
    for i, name in enumerate(demo_names):
        deposit_amt = random.randint(5000, 15000)
        withdraw_amt = random.randint(500, 2000)
        balance = deposit_amt - withdraw_amt
        txs = [
            {"type": "Deposit", "amount": deposit_amt, "note": "Initial deposit",
             "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")},
            {"type": "Withdraw", "amount": withdraw_amt, "note": "ATM withdrawal",
             "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")},
        ]
        _data.append({
            "accountNo": str(1001 + i),
            "name": name,
            "pin": hash_pin("1234"),
            "balance": balance,
            "transactions": txs,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        })
    save_data(_data)

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.markdown("## 🏦 NeoBank X")
    st.markdown("---")

    if st.session_state.logged_in:
        data = load_data()
        user = get_current_user(data)

        if user is None:
            # Account was deleted while logged in
            st.session_state.logged_in = False
            st.session_state.current_acc = None
            st.rerun()

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
            st.session_state.current_acc = None
            st.rerun()
    else:
        menu = st.radio("Navigation", ["Home", "Login", "Create Account", "Admin"])

    st.markdown("---")
    st.markdown("<small style='color:#555'>NeoBank X v2.1 • Secure Banking</small>", unsafe_allow_html=True)

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
    all_txs = [t for u in data for t in u.get("transactions", [])]
    total_deps = sum(t["amount"] for t in all_txs if t["type"] == "Deposit")
    total_wds = sum(t["amount"] for t in all_txs if t["type"] in ("Withdraw", "Transfer"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Users", total_users)
    col2.metric("💰 Total Deposits", format_currency(total_deps))
    col3.metric("📤 Total Withdrawals", format_currency(total_wds))
    col4.metric("🏦 Assets Under Management", format_currency(total_balance))

    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("💸 Deposits vs Withdrawals")
        fig = go.Figure(go.Bar(
            x=["Deposits", "Withdrawals"],
            y=[total_deps, total_wds],
            marker_color=["#38bdf8", "#f87171"],
            text=[format_currency(total_deps), format_currency(total_wds)],
            textposition="outside",
        ))
        fig.update_layout(**plotly_dark_layout())  # FIX: unpack dict with **
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("👤 Balance by Account")
        names = [u["name"] for u in data]
        bals = [u["balance"] for u in data]
        fig2 = go.Figure(go.Bar(
            x=names, y=bals,
            marker_color="#818cf8",
            text=[format_currency(b) for b in bals],
            textposition="outside",
        ))
        fig2.update_layout(**plotly_dark_layout())  # FIX: unpack dict with **
        st.plotly_chart(fig2, use_container_width=True)

    # Transaction timeline
    st.subheader("📈 Transaction Timeline")
    rows = []
    for u in data:
        for t in u.get("transactions", []):
            parsed = safe_parse_date(t["date"])  # FIX: robust date parsing
            if parsed:
                rows.append({
                    "date": parsed,
                    "amount": t["amount"] if t["type"] == "Deposit" else -t["amount"],
                    "user": u["name"],
                    "type": t["type"],
                })
    if rows:
        df = pd.DataFrame(rows).sort_values("date")
        fig3 = px.line(df, x="date", y="amount", color="user",
                       color_discrete_sequence=["#38bdf8", "#818cf8", "#fb923c"])
        fig3.update_layout(**plotly_dark_layout())  # FIX: unpack dict with **
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No transaction data to display yet.")

# ======================================================
# 🔐 LOGIN
# ======================================================
elif menu == "Login" and not st.session_state.logged_in:
    st.markdown('<div class="main-header">User Login</div>', unsafe_allow_html=True)
    st.markdown("##### Access your account securely.")

    col, _ = st.columns([1, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        acc_input = st.text_input("🔢 Account Number", placeholder="e.g. 1001")
        pin_input = st.text_input("🔑 PIN", type="password", placeholder="4-digit PIN")

        if st.button("Login →", use_container_width=True, type="primary"):
            if not acc_input or not pin_input:
                st.error("Please enter both account number and PIN.")
            else:
                data = load_data()
                idx = get_user_index(data, acc_input.strip())
                if idx is not None and data[idx].get("pin") == hash_pin(pin_input):
                    st.session_state.logged_in = True
                    st.session_state.current_acc = data[idx]["accountNo"]  # FIX: store only acc no
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
            name = name.strip()
            if not name or not pin:
                st.error("Please fill all fields.")
            elif len(pin) != 4 or not pin.isdigit():
                st.error("PIN must be exactly 4 digits.")
            elif pin != pin2:
                st.error("PINs do not match.")
            else:
                data = load_data()
                # Generate unique 5-digit account number
                existing = {u["accountNo"] for u in data}
                acc_no = str(random.randint(10000, 99999))
                while acc_no in existing:
                    acc_no = str(random.randint(10000, 99999))

                new_user = {
                    "accountNo": acc_no,
                    "name": name,
                    "pin": hash_pin(pin),
                    "balance": 0,
                    "transactions": [],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
                data.append(new_user)
                save_data(data)
                st.success("✅ Account created successfully!")
                st.info(f"🔢 Your Account Number: **{acc_no}**")
                st.warning("Save your account number safely — you'll need it to login.")

        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 📊 USER DASHBOARD
# ======================================================
elif menu == "Dashboard" and st.session_state.logged_in:
    data = load_data()
    user = get_current_user(data)  # FIX: always fresh from file, no stale session dict

    if user is None:
        st.error("Session error. Please log in again.")
        st.session_state.logged_in = False
        st.session_state.current_acc = None
        st.rerun()

    st.markdown(f'<div class="main-header">Welcome, {user["name"].split()[0]}!</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="account-card">
        <div style="font-size:0.8rem; color:#666; text-transform:uppercase; letter-spacing:0.12em;">Account Number</div>
        <div style="font-family:'DM Mono',monospace; font-size:1.4rem; color:#38bdf8; margin:0.3rem 0 1.2rem;">{user['accountNo']}</div>
        <div style="font-size:0.8rem; color:#666; text-transform:uppercase; letter-spacing:0.12em;">Current Balance</div>
        <div style="font-family:'DM Mono',monospace; font-size:2.4rem; font-weight:700; color:#fff;">{format_currency(user['balance'])}</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("⚡ Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📥 Deposit")
        dep_amount = st.number_input("Amount to Deposit (₹)", min_value=1, step=100, key="dep")
        dep_note = st.text_input("Note (optional)", key="dep_note", placeholder="e.g. Salary")
        if st.button("Deposit Now", use_container_width=True, type="primary", key="dep_btn"):
            data = load_data()
            idx = get_user_index(data, st.session_state.current_acc)
            if idx is None:
                st.error("Account not found.")
            else:
                data[idx]["balance"] += dep_amount
                add_transaction(data[idx], "Deposit", dep_amount, dep_note or "Deposit")
                save_data(data)
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
            idx = get_user_index(data, st.session_state.current_acc)
            if idx is None:
                st.error("Account not found.")
            elif wd_amount > data[idx]["balance"]:
                st.error("❌ Insufficient balance.")
            else:
                data[idx]["balance"] -= wd_amount
                add_transaction(data[idx], "Withdraw", wd_amount, wd_note or "Withdrawal")
                save_data(data)
                st.success(f"✅ Withdrawn {format_currency(wd_amount)} successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent transactions
    txs = user.get("transactions", [])
    if txs:
        st.subheader("📜 Recent Transactions")
        df = pd.DataFrame(txs[::-1][:10])
        df["Amount"] = df.apply(
            lambda r: f"+{format_currency(r['amount'])}" if r["type"] == "Deposit"
            else f"-{format_currency(r['amount'])}", axis=1
        )
        df["Date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y, %H:%M")
        st.dataframe(
            df[["Date", "type", "Amount", "note"]].rename(columns={"type": "Type", "note": "Note"}),
            use_container_width=True,
            hide_index=True,
        )

# ======================================================
# 📜 TRANSACTIONS PAGE
# ======================================================
elif menu == "Transactions" and st.session_state.logged_in:
    data = load_data()
    user = get_current_user(data)  # FIX: always fresh

    if user is None:
        st.error("Session error. Please log in again.")
        st.stop()

    st.markdown('<div class="main-header">Transaction History</div>', unsafe_allow_html=True)

    txs = user.get("transactions", [])
    if not txs:
        st.info("No transactions yet.")
    else:
        df = pd.DataFrame(txs[::-1])
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
        df["Date"] = df["date_parsed"].dt.strftime("%d %b %Y, %H:%M")
        df["signed_amount"] = df.apply(
            lambda r: r["amount"] if r["type"] == "Deposit" else -r["amount"], axis=1
        )

        deps = sum(t["amount"] for t in txs if t["type"] == "Deposit")
        wds = sum(t["amount"] for t in txs if t["type"] in ("Withdraw", "Transfer"))
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Deposits", format_currency(deps))
        col2.metric("Total Withdrawals", format_currency(wds))
        col3.metric("Net Flow", format_currency(deps - wds))

        fig = px.bar(
            df, x="Date", y="signed_amount",
            color=df["signed_amount"].apply(lambda x: "Deposit" if x > 0 else "Withdrawal"),
            color_discrete_map={"Deposit": "#38bdf8", "Withdrawal": "#f87171"},
            labels={"signed_amount": "Amount (₹)", "Date": "Date"},
        )
        fig.update_layout(**plotly_dark_layout(), showlegend=False)  # FIX: unpack **
        st.plotly_chart(fig, use_container_width=True)

        tx_filter = st.selectbox("Filter by Type", ["All", "Deposit", "Withdraw", "Transfer"])
        display_df = df if tx_filter == "All" else df[df["type"] == tx_filter]
        st.dataframe(
            display_df[["Date", "type", "amount", "note"]].rename(columns={
                "type": "Type", "amount": "Amount (₹)", "note": "Note"
            }),
            use_container_width=True,
            hide_index=True,
        )

# ======================================================
# 💸 TRANSFER PAGE
# ======================================================
elif menu == "Transfer" and st.session_state.logged_in:
    data = load_data()
    user = get_current_user(data)  # FIX: always fresh, no stale sender balance

    if user is None:
        st.error("Session error. Please log in again.")
        st.stop()

    st.markdown('<div class="main-header">Transfer Funds</div>', unsafe_allow_html=True)
    st.metric("Your Balance", format_currency(user["balance"]))

    col, _ = st.columns([1, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        to_acc = st.text_input("🔢 Recipient Account Number")
        amount = st.number_input("💸 Amount to Transfer (₹)", min_value=1, step=100)
        note = st.text_input("📝 Note", placeholder="e.g. Rent payment")

        if st.button("Transfer Now →", use_container_width=True, type="primary"):
            to_acc = to_acc.strip()
            data = load_data()
            sender_idx = get_user_index(data, st.session_state.current_acc)
            receiver_idx = get_user_index(data, to_acc)

            if not to_acc:
                st.error("Please enter a recipient account number.")
            elif to_acc == st.session_state.current_acc:  # FIX: compare against session acc, not stale user dict
                st.error("❌ Cannot transfer to your own account.")
            elif receiver_idx is None:
                st.error("❌ Recipient account not found.")
            elif sender_idx is None:
                st.error("❌ Sender account error. Please log in again.")
            elif amount > data[sender_idx]["balance"]:
                st.error("❌ Insufficient balance.")
            else:
                receiver_name = data[receiver_idx]["name"]
                data[sender_idx]["balance"] -= amount
                add_transaction(
                    data[sender_idx], "Transfer", amount,
                    f"To {receiver_name} ({to_acc}) — {note or 'Transfer'}"
                )
                data[receiver_idx]["balance"] += amount
                add_transaction(
                    data[receiver_idx], "Deposit", amount,
                    f"From {data[sender_idx]['name']} ({st.session_state.current_acc}) — {note or 'Transfer'}"
                )
                save_data(data)
                st.success(f"✅ Transferred {format_currency(amount)} to **{receiver_name}** successfully!")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 👨‍💼 ADMIN PANEL
# ======================================================
elif menu == "Admin":
    st.markdown('<div class="main-header">Admin Panel</div>', unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        col, _ = st.columns([1, 1])
        with col:
            admin_pass = st.text_input("🔑 Admin Password", type="password")
            if st.button("Access Admin →", use_container_width=True, type="primary"):
                if hashlib.sha256(admin_pass.encode()).hexdigest() == ADMIN_PIN_HASH:
                    st.session_state.admin_logged_in = True
                    st.session_state.confirm_delete_admin = None
                    st.rerun()
                else:
                    st.error("❌ Invalid admin password.")
        st.info("Default admin password: **admin123**  *(change before deploying)*")

    else:
        if st.button("🚪 Admin Logout"):
            st.session_state.admin_logged_in = False
            st.session_state.confirm_delete_admin = None
            st.rerun()

        data = load_data()
        total_bal = sum(u["balance"] for u in data)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Users", len(data))
        col2.metric("💰 Total Balance", format_currency(total_bal))
        col3.metric("📊 Avg Balance", format_currency(total_bal / len(data) if data else 0))

        st.markdown("---")
        st.subheader("👥 All Accounts")

        display_data = [{
            "Account No": u["accountNo"],
            "Name": u["name"],
            "Balance (₹)": u["balance"],
            "Transactions": len(u.get("transactions", [])),
            "Joined": u.get("created_at", "N/A")[:10],
        } for u in data]

        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🗑️ Delete Account")

        if not data:
            st.info("No accounts to delete.")
        else:
            acc_options = [f"{u['accountNo']} — {u['name']}" for u in data]
            acc_to_delete = st.selectbox("Select Account", acc_options)
            acc_no = acc_to_delete.split(" — ")[0]

            # FIX: Two-step confirmation — no accidental one-click delete
            if st.session_state.confirm_delete_admin != acc_no:
                if st.button("⚠️ Request Delete", type="secondary"):
                    st.session_state.confirm_delete_admin = acc_no
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="confirm-box">
                    ⚠️ Are you sure you want to permanently delete account <b>{acc_no}</b>?
                    This cannot be undone.
                </div>
                """, unsafe_allow_html=True)
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                        data = [u for u in data if u["accountNo"] != acc_no]
                        save_data(data)
                        st.session_state.confirm_delete_admin = None
                        st.success(f"Account {acc_no} deleted.")
                        st.rerun()
                with col_no:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.confirm_delete_admin = None
                        st.rerun()

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#333; font-size:0.8rem;'>"
    "🏦 NeoBank X v2.1 • Secure Digital Banking • Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
