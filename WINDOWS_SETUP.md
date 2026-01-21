# 🪟 Windows Setup Guide

Complete guide to run the Advanced Stock Scanner on Windows.

## **Prerequisites**

### **1. Python 3.8+**
- Download from: https://www.python.org/downloads/
- ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
- Verify installation:
  ```cmd
  python --version
  pip --version
  ```

### **2. Node.js 18+**
- Download from: https://nodejs.org/
- Choose LTS version
- Verify installation:
  ```cmd
  node --version
  npm --version
  ```

### **3. Git (Optional)**
- Download from: https://git-scm.com/download/win
- Needed only if cloning from GitHub

---

## **Quick Start (Windows)**

### **Method 1: Using Batch File (Easiest)**

1. **Open Command Prompt or PowerShell** in the project folder
2. **Double-click** `start-scanner.bat`
   - Or run: `start-scanner.bat` from command prompt
3. **Two windows will open:**
   - Backend server (Python Flask)
   - Frontend server (Vite)
4. **Open browser:** http://localhost:3000

### **Method 2: Manual Start**

#### **Terminal 1 - Backend:**
```cmd
cd backend
python -m pip install -r requirements.txt
python app.py
```

#### **Terminal 2 - Frontend:**
```cmd
cd frontend
npm install
npm run dev
```

---

## **Installation Steps**

### **Step 1: Install Backend Dependencies**

```cmd
cd advanced-stock-scanner\backend
python -m pip install -r requirements.txt
```

**If you get permission errors:**
```cmd
python -m pip install --user -r requirements.txt
```

**If pip is not found:**
```cmd
python -m ensurepip --upgrade
python -m pip install -r requirements.txt
```

### **Step 2: Install Frontend Dependencies**

```cmd
cd advanced-stock-scanner\frontend
npm install
```

**If npm is slow or fails:**
```cmd
npm install --legacy-peer-deps
```

### **Step 3: Start the Application**

**Option A: Use Batch File**
```cmd
start-scanner.bat
```

**Option B: Manual Start**
- Open **2 separate Command Prompt windows**
- Window 1: `cd backend && python app.py`
- Window 2: `cd frontend && npm run dev`

---

## **Windows-Specific Notes**

### **Port Conflicts**

If port 5000 or 3000 is already in use:

**Backend (change port 5000):**
```python
# In backend/app.py, change:
app.run(host='0.0.0.0', port=5000)
# To:
app.run(host='0.0.0.0', port=5001)  # Or any available port
```

**Frontend (change port 3000):**
```json
// In frontend/vite.config.ts, add:
export default defineConfig({
  server: {
    port: 3001  // Or any available port
  }
})
```

### **Python Path Issues**

If `python` command doesn't work:
- Try `py` instead: `py app.py`
- Or `python3`: `python3 app.py`
- Check PATH: `where python`

### **Firewall Warnings**

Windows Firewall may ask for permission:
- ✅ **Allow** Python and Node.js through firewall
- This is needed for localhost connections

### **PowerShell Execution Policy**

If batch files don't run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## **Troubleshooting**

### **Error: "python is not recognized"**
- Python not in PATH
- **Fix:** Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python39\python.exe app.py`

### **Error: "npm is not recognized"**
- Node.js not installed or not in PATH
- **Fix:** Reinstall Node.js
- Restart Command Prompt after installation

### **Error: "ModuleNotFoundError"**
- Missing Python packages
- **Fix:** `python -m pip install -r requirements.txt`

### **Error: "Port already in use"**
- Another app is using port 5000 or 3000
- **Fix:** 
  - Close other apps using those ports
  - Or change ports (see above)

### **Error: "Cannot find module" (Node.js)**
- Missing npm packages
- **Fix:** `npm install` in frontend folder

### **Backend starts but frontend doesn't**
- Check if Node.js is installed: `node --version`
- Check if npm packages are installed: `npm list`
- Try: `npm install` again

### **CORS Errors**
- Backend not running
- **Fix:** Make sure backend is on http://localhost:5000
- Check backend terminal for errors

---

## **File Paths (Windows)**

All paths in the code use forward slashes (`/`) which work on Windows.
If you see any backslash issues, they're automatically handled by Python/Node.js.

---

## **Running as Administrator**

**Not required** for normal operation. Only needed if:
- Ports are restricted
- File permissions are denied

---

## **Development vs Production**

### **Development (Current Setup):**
- Backend: `python app.py` (Flask dev server)
- Frontend: `npm run dev` (Vite dev server)
- Hot reload enabled
- Debug mode on

### **Production (Future):**
- Use `gunicorn` for backend (Windows: `waitress`)
- Build frontend: `npm run build`
- Serve static files with nginx or similar

---

## **Windows Services (Optional)**

To run as Windows service (advanced):
- Use `NSSM` (Non-Sucking Service Manager)
- Or `pywin32` for Python services

---

## **Quick Commands Reference**

```cmd
# Check Python
python --version

# Check Node.js
node --version
npm --version

# Install backend deps
cd backend
python -m pip install -r requirements.txt

# Install frontend deps
cd frontend
npm install

# Start backend
cd backend
python app.py

# Start frontend
cd frontend
npm run dev

# Quick start (both)
start-scanner.bat
```

---

## **System Requirements**

- **OS:** Windows 10/11 (64-bit recommended)
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 500MB free space
- **Internet:** Required for API calls

---

## **Support**

If you encounter issues:
1. Check this guide
2. Verify all prerequisites are installed
3. Check error messages in terminal windows
4. Ensure ports 5000 and 3000 are available

---

**✅ The app is fully Windows-compatible!** All code uses cross-platform paths and commands.
