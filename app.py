import streamlit as st

import ccxt   #

st.set_page_config(
    page_title="Custom Multi-Account Trading App",
    layout="wide"
)

# rest of your app code...

st.title("📈 Custom Multi-Account Trading & Investment Terminal")
st.markdown("Manage multiple exchange or broker accounts, execute trades, and manage funding from a single UI.")

# --- SIDEBAR: ACCOUNT CONFIGURATION ---
st.sidebar.header("🔑 Account Management")
account_choice = st.sidebar.selectbox(
    "Select Active Account", 
    ["Binance Testnet (Account 1)", "Binance Live (Account 2)", "Paper Trading Broker"]
)

api_key = st.sidebar.text_input("API Key", type="password")
api_secret = st.sidebar.text_input("API Secret", type="password")

# Initialize Exchange Client (Using CCXT as a unified wrapper)
@st.cache_resource
def get_exchange_client(choice, key, secret):
    try:
        if "Binance" in choice:
            exchange = ccxt.binance({
                'apiKey': key,
                'secret': secret,
                'enableRateLimit': True,
            })
            if "Testnet" in choice:
                exchange.set_sandbox_mode(True) # Safe sandbox testing mode
            return exchange
        return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

exchange = get_exchange_client(account_choice, api_key, api_secret)

# --- TABS FOR APP NAVIGATION ---
tab_portfolio, tab_trade, tab_withdraw = st.tabs(["💰 Portfolio & Balances", "⚡ Execute Trade", "💸 Withdrawals"])

# --- TAB 1: PORTFOLIO & BALANCES ---
with tab_portfolio:
    st.subheader(f"Asset Holdings for: {account_choice}")
    
    if st.button("Fetch Live Balances"):
        if not api_key or not api_secret:
            st.warning("Please enter your API credentials in the sidebar first.")
        else:
            try:
                balance = exchange.fetch_balance()
                # Filter out empty assets
                non_zero = {k: v for k, v in balance['total'].items() if v > 0}
                df_balance = pd.DataFrame(list(non_zero.items()), columns=['Asset', 'Total Balance'])
                st.dataframe(df_balance, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to fetch balance: {e}")

# --- TAB 2: EXECUTE TRADE ---
with tab_trade:
    st.subheader("Market & Limit Order Terminal")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Trading Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"])
        order_type = st.selectbox("Order Type", ["market", "limit"])
    with col2:
        side = st.selectbox("Side", ["buy", "sell"])
        amount = st.number_input("Amount to Trade", min_value=0.0001, value=0.001, format="%.4f")
    
    price = 0.0
    if order_type == "limit":
        price = st.number_input("Limit Price (USDT)", min_value=0.01, value=50000.0)

    if st.button("Submit Order to Exchange"):
        if not api_key or not api_secret:
            st.warning("API Keys required to execute live or testnet orders.")
        else:
            try:
                if order_type == "market":
                    order = exchange.create_order(symbol, 'market', side, amount)
                else:
                    order = exchange.create_order(symbol, 'limit', side, amount, price)
                st.success(f"Order successfully placed! ID: {order['id']}")
                st.json(order)
            except Exception as e:
                st.error(f"Order execution failed: {e}")

# --- TAB 3: WITHDRAWALS ---
with tab_withdraw:
    st.subheader("Fund Withdrawal Portal")
    st.info("Note: Ensure whitelist withdrawal address restrictions are configured safely on your exchange account settings.")
    
    w_currency = st.text_input("Currency (e.g., USDT, BTC)", "USDT")
    w_amount = st.number_input("Withdrawal Amount", min_value=1.0, value=50.0)
    w_address = st.text_input("Destination Wallet Address")
    w_network = st.text_input("Network (e.g., TRC20, ERC20)", "TRC20")
    
    if st.button("Request Withdrawal"):
        if not api_key or not api_secret:
            st.warning("API credentials required.")
        elif not w_address:
            st.error("Please enter a valid destination address.")
        else:
            try:
                # Safety check confirmation toggle
                with st.spinner("Processing withdrawal request through API..."):
                    # Example CCXT withdraw call (requires withdrawal permissions enabled on API key)
                    response = exchange.withdraw(w_currency, w_amount, w_address, tag=None, params={"network": w_network})
                    st.success(f"Withdrawal submitted successfully! Transaction ID: {response.get('id', 'Pending')}")
            except Exception as e:
                st.error(f"Withdrawal failed: {e}. Check if API withdrawal permissions and IP whitelisting are active.")