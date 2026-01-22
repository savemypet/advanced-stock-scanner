# IB Gateway API Settings

## Required Settings for Stock Scanner

### Step 1: Open IB Gateway Settings
1. Open **IB Gateway** (make sure it's running and logged in)
2. Click **Configure** → **API** → **Settings**

### Step 2: Enable API Access
Check these boxes:
- ✅ **Enable ActiveX and Socket Clients**
- ✅ **Read-Only API** (optional - check if you only want to read data, uncheck if you want to trade)

### Step 3: Set Socket Port
**Important:** Choose ONE port based on your account type:

#### Option A: Paper Trading Account (Recommended for Testing)
- **Socket port:** `7497`
- This is for paper trading (practice account)
- No real money at risk

#### Option B: Live Trading Account
- **Socket port:** `7496`
- This is for real trading account
- **WARNING:** Only use if you want to trade with real money

#### Option C: Default Port (If others don't work)
- **Socket port:** `4001`
- This is the default IB Gateway port
- Works for most setups

### Step 4: Trusted IPs (Optional)
- Leave **Trusted IPs** blank (empty) for localhost connections
- OR add: `127.0.0.1` if you want to be explicit

### Step 5: Save and Restart
1. Click **OK** to save settings
2. **Restart IB Gateway** (close and reopen)
3. Make sure IB Gateway shows **all green** (no yellow/red indicators)

## Current Scanner Configuration

The scanner is currently configured to use:
- **Port:** `4001` (default)
- **Host:** `127.0.0.1` (localhost)
- **Client ID:** `1`

## Verify Connection

After setting up, the scanner will automatically connect when you:
1. Start the backend server
2. Click "📡 Live Scanner" in the web interface
3. Click "Start" or "Refresh" to scan

## Troubleshooting

If connection fails:
1. Make sure IB Gateway is **fully logged in** (not just open)
2. Check that the **Socket port** matches what you set (7497, 7496, or 4001)
3. Verify **Enable ActiveX and Socket Clients** is checked
4. Restart IB Gateway after changing settings
5. Check that no firewall is blocking the port

## Port Reference

| Port | Account Type | Use Case |
|------|-------------|----------|
| 7497 | Paper Trading | Testing, practice |
| 7496 | Live Trading | Real money trading |
| 4001 | Default | Works for most setups |
