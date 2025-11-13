

// Configuration
const EMPLOYEES = [
  "Jinu T J",
  "Bismillakhan S",
  "Midhun",
  "Aravind",
  "Akhil Mohan",
  "Akash T K",
  "Shinoj"
];

const STATUS_OPTIONS = ["In progress", "Completed", "On hold"];

const ACTIVITY_OPTIONS = [
  "Development",
  "System design",
  "Unit testing",
  "Testing",
  "Bug fix(QA)",
  "Bug fix(Customer)",
  "Verification testing(Customer)",
  "Release",
  "Maintenance Tasks",
  "Meeting"
];

// Colors
const HEADER_BG = "#FEF2CB";  // Light yellow
const WEEKEND_BG = "#FF9999";  // Light Red 1

// Destination folder ID (optional - leave empty for root Drive)
const DESTINATION_FOLDER_ID = PropertiesService.getScriptProperties().getProperty('DESTINATION_FOLDER_ID');


/**
 * Main function - Creates the monthly timesheet
 * You can customize the month and year parameters
 */
function createMonthlyTimesheet(monthName = null, year = null) {
  // Use current month/year if not specified
  if (typeof monthName !== 'string' || !monthName) {
    monthName = null;
  }
  if (typeof year !== 'number' || !year) {
    year = null;
  }
  const now = new Date();
  if (!monthName) {
    monthName = Utilities.formatDate(now, Session.getScriptTimeZone(), "MMMM");
  }
  if (!year) {
    year = now.getFullYear();
  }
  
  Logger.log("Creating timesheet for " + monthName + " " + year);
  
  // Create the workbook
  const workbookName = "IZ_work_report_" + monthName;
  const ss = SpreadsheetApp.create(workbookName);
  
  // Move to destination folder if specified
  const file = DriveApp.getFileById(ss.getId());
  if (DESTINATION_FOLDER_ID) {
    const folder = DriveApp.getFolderById(DESTINATION_FOLDER_ID);
    file.moveTo(folder);
    Logger.log("Moved to folder: " + folder.getName());
  }

  // Share the file with employee emails from Script Properties
  const emailProp = PropertiesService.getScriptProperties().getProperty('EMPLOYEE_EMAILS');
  if (emailProp) {
    const emailList = emailProp.split(',').map(function(e) { return e.trim(); }).filter(function(e) { return e.length > 0; });
    emailList.forEach(function(email) {
      try {
        file.addEditor(email);
        Logger.log('Shared with: ' + email);
      } catch (err) {
        Logger.log('Failed to share with ' + email + ': ' + err);
      }
    });
  } else {
    Logger.log('No EMPLOYEE_EMAILS property set in Script Properties.');
  }
  
  // Get dates for the month
  const dates = getDatesForMonth(monthName, year);
  Logger.log("Generated " + dates.length + " dates");
  
  // Delete default "Sheet1"
  const defaultSheet = ss.getSheets()[0];
  
  // Create employee sheets
  EMPLOYEES.forEach(function(empName) {
    Logger.log("Creating sheet: " + empName);
    setupEmployeeSheet(ss, empName, dates);
  });
  
  // Delete the default sheet
  ss.deleteSheet(defaultSheet);
  
  // Open the spreadsheet
  const url = ss.getUrl();
  Logger.log("====================================");
  Logger.log("✓ Timesheet created successfully!");
  Logger.log("====================================");
  Logger.log("Workbook: " + workbookName);
  Logger.log("Sheets: " + EMPLOYEES.length + " employee tabs");
  Logger.log("URL: " + url);
  Logger.log("====================================");
  
  // Update the config JSON file with new spreadsheet ID
  updateConfigJson(ss.getId(), monthName, year);
  
  // Return URL for programmatic use
  return url;
}


/**
 * Updates or creates a JSON config file with the current spreadsheet ID
 * This allows Python scripts to read the latest timesheet ID
 */
function updateConfigJson(spreadsheetId, monthName, year) {
  const configFileName = "timesheet_config.json";
  
  // Create config object
  const config = {
    current_spreadsheet_id: spreadsheetId,
    month: monthName,
    year: year,
    updated_at: new Date().toISOString(),
    spreadsheet_url: "https://docs.google.com/spreadsheets/d/" + spreadsheetId
  };
  
  const configContent = JSON.stringify(config, null, 2);
  
  try {
    // Check if config file already exists in the destination folder
    let configFile = null;
    let folder = DESTINATION_FOLDER_ID ? DriveApp.getFolderById(DESTINATION_FOLDER_ID) : DriveApp.getRootFolder();
    
    const existingFiles = folder.getFilesByName(configFileName);
    if (existingFiles.hasNext()) {
      // Update existing file
      configFile = existingFiles.next();
      configFile.setContent(configContent);
      Logger.log("✓ Updated existing config file: " + configFile.getId());
    } else {
      // Create new file
      configFile = folder.createFile(configFileName, configContent, MimeType.PLAIN_TEXT);
      Logger.log("✓ Created new config file: " + configFile.getId());
    }
    
    // Make the config file readable by anyone with the link (or keep it private)
    // configFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    
    Logger.log("Config file URL: " + configFile.getUrl());
    Logger.log("Config file ID: " + configFile.getId());
    
    // Store the config file ID in Script Properties for easy access
    PropertiesService.getScriptProperties().setProperty('CONFIG_FILE_ID', configFile.getId());
    
  } catch (err) {
    Logger.log("ERROR updating config file: " + err);
  }
}


/**
 * Generate list of dates for the given month
 */
function getDatesForMonth(monthName, year) {
  // Parse month name to month number
  const monthMap = {
    "January": 0, "February": 1, "March": 2, "April": 3,
    "May": 4, "June": 5, "July": 6, "August": 7,
    "September": 8, "October": 9, "November": 10, "December": 11,
    "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3,
    "Jun": 5, "Jul": 6, "Aug": 7, "Sep": 8,
    "Oct": 9, "Nov": 10, "Dec": 11
  };
  
  const monthNum = monthMap[monthName];
  if (monthNum === undefined) {
    throw new Error("Invalid month name: " + monthName);
  }
  
  // Get number of days in month
  const lastDay = new Date(year, monthNum + 1, 0).getDate();
  
  // Get month abbreviation
  const monthAbbr = Utilities.formatDate(new Date(year, monthNum, 1), Session.getScriptTimeZone(), "MMM");
  
  const dates = [];
  for (let day = 1; day <= lastDay; day++) {
    const date = new Date(year, monthNum, day);
    const dayOfWeek = date.getDay(); // 0=Sunday, 6=Saturday
    const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);
    const dateStr = day + "-" + monthAbbr;
    
    dates.push({
      date: dateStr,
      isWeekend: isWeekend
    });
  }
  
  return dates;
}


/**
 * Create and format an individual employee timesheet
 */
function setupEmployeeSheet(ss, empName, dates) {
  // Create new sheet
  const sheet = ss.insertSheet(empName);
  
  // Set column widths
  sheet.setColumnWidth(1, 30);   // A
  sheet.setColumnWidth(2, 80);   // B - Date
  sheet.setColumnWidth(3, 400);  // C - Module/Area
  sheet.setColumnWidth(4, 400);  // D - Task details
  sheet.setColumnWidth(5, 100);  // E - Status
  sheet.setColumnWidth(6, 150);  // F - Activity Type
  sheet.setColumnWidth(7, 70);   // G - Start
  sheet.setColumnWidth(8, 70);   // H - End
  sheet.setColumnWidth(9, 70);   // I - Task
  sheet.setColumnWidth(10, 70);  // J - Total
  sheet.setColumnWidth(11, 420); // K - Remarks
  
  // Set Calibri font for the whole sheet
  sheet.getRange(1, 1, sheet.getMaxRows(), sheet.getMaxColumns()).setFontFamily("Calibri");
  

  // Row 2: Title
  sheet.getRange("B2:J2").merge();
  sheet.getRange("B2").setValue("Interview Zero- " + empName)
    .setFontWeight("bold")
    .setHorizontalAlignment("center")
    .setFontSize(12);
  
  // Row 4: Headers with proper structure
  // Main headers row
  const mainHeaders = ["", "Date", "Module/Area", "Task details/Ticket number", 
                       "Status", "Activity Type", "", "", "", "", "Remarks"];
  sheet.getRange(4, 1, 1, mainHeaders.length).setValues([mainHeaders])
    .setBackground(HEADER_BG)
    .setFontWeight("bold")
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle")
    .setFontSize(12);
  
  // Merge cells for "Time" header (columns G-H)
  sheet.getRange(4, 7, 1, 2).merge();
  sheet.getRange(4, 7).setValue("Time");
  
  // Merge cells for "Duration" header (columns I-J)
  sheet.getRange(4, 9, 1, 2).merge();
  sheet.getRange(4, 9).setValue("Duration");
  
  // Row 5: Sub-headers for Time and Duration
  const subHeaders = ["", "", "", "", "", "", "Start", "End", "Task", "Total", ""];
  sheet.getRange(5, 1, 1, subHeaders.length).setValues([subHeaders])
    .setBackground(HEADER_BG)
    .setFontWeight("bold")
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle")
    .setFontSize(12);
  
  // Merge Date, Module/Area, Task details, Status, Activity Type, and Remarks vertically (rows 4-5)
  sheet.getRange(4, 2, 2, 1).merge(); // Date
  sheet.getRange(4, 3, 2, 1).merge(); // Module/Area
  sheet.getRange(4, 4, 2, 1).merge(); // Task details
  sheet.getRange(4, 5, 2, 1).merge(); // Status
  sheet.getRange(4, 6, 2, 1).merge(); // Activity Type
  sheet.getRange(4, 11, 2, 1).merge(); // Remarks
  
  // Data rows: 2 rows per date starting from row 6 (after headers)
  let currentRow = 6;
  
  dates.forEach(function(dateInfo) {
    const dateStr = dateInfo.date;
    const isWeekend = dateInfo.isWeekend;
    
    // Merge date cells vertically (2 rows) and center align
    const dateRange = sheet.getRange(currentRow, 2, 2, 1);
    dateRange.merge();
    dateRange.setValue(dateStr)
      .setHorizontalAlignment("center")
      .setVerticalAlignment("middle");
    
    // Add task duration formulas for both rows
    for (let offset = 0; offset < 2; offset++) {
      const row = currentRow + offset;
      const taskFormula = '=IF(AND(G' + row + '<TIME(12,30,0),H' + row + '>TIME(13,0,0)),H' + row + '-G' + row + '-TIME(0,30,0),H' + row + '-G' + row + ')';
      sheet.getRange(row, 9).setFormula(taskFormula);
    }
    
    // Add total formula in first row only (sums both task rows) and merge vertically
    const totalFormula = '=SUM(I' + currentRow + ':I' + (currentRow + 1) + ')';
    const totalRange = sheet.getRange(currentRow, 10, 2, 1);
    totalRange.merge();
    totalRange.setFormula(totalFormula)
      .setHorizontalAlignment("center")
      .setVerticalAlignment("middle")
      .setFontWeight("bold")
      .setFontSize(11);
    
    // Format Start and End as clock time 
    sheet.getRange(currentRow, 7, 2, 2).setNumberFormat("hh:mm");

    // Format Task and Total as duration hh:mm
    sheet.getRange(currentRow, 9, 2, 2).setNumberFormat("hh:mm");

    // Color weekend rows
    if (isWeekend) {
      sheet.getRange(currentRow, 1, 2, 11).setBackground(WEEKEND_BG);
    }
    
    // Add data validation for Status (column E)
    const statusRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(STATUS_OPTIONS, true)
      .setAllowInvalid(false)
      .build();
    sheet.getRange(currentRow, 5, 2, 1).setDataValidation(statusRule);
    
    // Add data validation for Activity Type (column F)
    const activityRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(ACTIVITY_OPTIONS, true)
      .setAllowInvalid(false)
      .build();
    sheet.getRange(currentRow, 6, 2, 1).setDataValidation(activityRule);
    
    currentRow += 2;
  });
  
  const lastDataRow = currentRow - 1;
  
  // Add "Monthly hours spend" row
  const monthlyRow = currentRow + 1;
  sheet.getRange(monthlyRow, 2, 1, 8).merge();
  sheet.getRange(monthlyRow, 2).setValue("Monthly hours spend")
    .setFontWeight("bold")
    .setHorizontalAlignment("right");
  
  // Monthly total formula
  const monthlyFormula = 
    '=TEXT(INT(SUM(J5:J' + lastDataRow + ')),"0")&":"&' +
    'TEXT(HOUR(SUM(J5:J' + lastDataRow + ')),"00")&":"&' +
    'TEXT(MINUTE(SUM(J5:J' + lastDataRow + ')),"00")';
  sheet.getRange(monthlyRow, 10).setFormula(monthlyFormula)
    .setFontWeight("bold");
  
  // Add borders to all cells
  const allDataRange = sheet.getRange(4, 1, monthlyRow - 3, 11);
  allDataRange.setBorder(true, true, true, true, true, true);
  
  // Set font size 11 for all data rows (from row 6 to last data row)
  sheet.getRange(6, 1, sheet.getMaxRows() - 5, sheet.getMaxColumns()).setFontSize(11);
  // Center-align text in column I (Task column)
  sheet.getRange(6, 7, sheet.getMaxRows() - 5, 3)
  .setHorizontalAlignment("center")
  .setVerticalAlignment("middle");

  
  Logger.log("✓ " + empName + " completed (" + dates.length + " dates)");
}


/**
 * Create a custom menu when opening a spreadsheet
 * (Optional - only works if this script is bound to a spreadsheet)
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Timesheet Tools')
    .addItem('Create Monthly Timesheet', 'createMonthlyTimesheet')
    .addToUi();
}


/**
 * Test function - creates timesheet for current month
 */
function testCreateCurrentMonth() {
  createMonthlyTimesheet();
}


/**
 * Test function - creates timesheet for next month
 */
function testCreateNextMonth() {
  const now = new Date();
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const monthName = Utilities.formatDate(nextMonth, Session.getScriptTimeZone(), "MMMM");
  const year = nextMonth.getFullYear();
  
  createMonthlyTimesheet(monthName, year);
}
