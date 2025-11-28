
# Google Apps Script Timesheet Creator

Easily automate the creation and sharing of monthly timesheets for your team using Google Apps Script and Google Sheets. 
---


## 🚀 Quick Start


### 1. Create Your Apps Script Project

1. Go to [Google Apps Script](https://script.google.com)
2. Click **New project**
3. Delete the default `function myFunction() {}` code
4. Copy ALL the code from `CreateTimesheet.gs` and paste it
5. Click the save icon (💾) or Ctrl+S
6. Name your project: "Timesheet Creator"

### Step 2: Configure Settings

In the script, find this line (around line 35):
```javascript
const DESTINATION_FOLDER_ID = "DESTINATION_FOLDER_ID";
```

**Option A:** Keep your folder ID as-is  
**Option B:** Change it to `""` (empty) to create in root Drive

### Step 3: Run the Script

1. Select the function: `testCreateCurrentMonth` from the dropdown at the top
2. Click **Run** (▶️ button)
3. **First time only:** Google will ask for permissions:
   - Click **Review Permissions**
   - Choose your Google account
   - Click **Advanced** → **Go to Timesheet Creator (unsafe)**
   - Click **Allow**
4. Check the **Execution log** (View → Logs) to see the URL


### 4. Find Your Timesheet

- Check your Google Drive (or the folder you specified)
- Look for: `IZ_work_report_November`

---


## 📋 How to Use


**Create for current month:**
```javascript
testCreateCurrentMonth();
```

**Create for a specific month:**
```javascript
createMonthlyTimesheet("December", 2025);
```

**Create for next month:**
```javascript
testCreateNextMonth();
```

---


## 🤖 Automation Options


### Option 1: Add a Custom Menu Button

1. Open any Google Sheet
2. Go to **Extensions** → **Apps Script**
3. Paste the code
4. Save and refresh the sheet
5. You'll see a new menu: **Timesheet Tools** → **Create Monthly Timesheet**


### Option 2: Time-Based Trigger (Auto-create monthly)

1. In Apps Script editor, click the clock icon (⏰ **Triggers**)
2. Click **Add Trigger**
3. Settings:
   - Function: `testCreateCurrentMonth`
   - Event source: **Time-driven**
   - Type: **Month timer**
   - Day of month: **1** (first day)
   - Time of day: **12am-1am**
4. Click **Save**

Now timesheets will be created automatically on the 1st of every month!


### Option 3: Add to Your Dashboard Sheet

Add this to your personal "Dashboard" sheet:
1. Create a Google Sheet
2. Tools → Script editor
3. Paste the code
4. Save and close
5. Refresh the sheet
6. Use menu: **Timesheet Tools** → **Create Monthly Timesheet**

---


## 🎨 Customization



**Change Employee List (Sheet Tabs Only):**
Edit the `EMPLOYEES` array in the script to update the names for the sheet tabs. This does not affect sharing permissions, which are controlled by the `EMPLOYEE_EMAILS` Script Property.


**Change Dropdown Options:**
Edit `STATUS_OPTIONS` or `ACTIVITY_OPTIONS` in the script.


**Change Colors:**
Edit these constants in the script:
```javascript
const HEADER_BG = "#FFF2CC";  // Light yellow
const WEEKEND_BG = "#FFC7CE";  // Pink
```

---



## 🌟 Why Use This Project?

✅ No service account or OAuth setup needed  
✅ No authentication headaches  
✅ Uses your Google Drive storage  
✅ Can automate with time-based triggers  
✅ Add a custom menu to any sheet  
✅ Runs in Google's cloud (no local setup)  
✅ Works on any device (even mobile)  
✅ Secure, non-hardcoded email sharing via Script Properties

---



## 📧 Email Sharing & Notifications

When a timesheet is created, the script reads the `EMPLOYEE_EMAILS` Script Property and shares the file with those addresses as editors. Google Drive will automatically send an email notification to each employee.

If you do not want notifications, you must use the advanced Drive API (not covered here).


## 🛠 Troubleshooting

### "Script needs authorization"
- This is normal on first run
- Follow Step 3 above to grant permissions

### "Cannot find folder"
- Check `DESTINATION_FOLDER_ID` is correct
- Or set it to `""` to use root Drive

### "Invalid month name"
- Use full names: "January", "February", etc.
- Or short: "Jan", "Feb", etc.

---


## 🚦 Next Steps

1. Copy the code to Apps Script
2. Run `testCreateCurrentMonth()`
3. Check your Drive for the timesheet
4. (Optional) Set up monthly trigger for automation
