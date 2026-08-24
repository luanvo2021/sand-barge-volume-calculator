// ==============================================================================
// MÃ NGUỒN GOOGLE APPS SCRIPT CHUYÊN NGHIỆP - TỰ ĐỘNG KẺ BẢNG & ĐỊNH DẠNG ĐẸP
// ==============================================================================

function doPost(e) {
  try {
    var data = {};
    if (e.postData && e.postData.contents) {
      try {
        data = JSON.parse(e.postData.contents);
      } catch (parseErr) {
        data = e.parameter || {};
      }
    } else {
      data = e.parameter || {};
    }

    var sheet = getTargetSheet();
    formatSheetHeader(sheet);

    var fileUrl = "";
    var imageFormula = "Không có ảnh";

    // Lưu ảnh vào Google Drive nếu có
    if (data.image_base64 && data.image_base64.length > 50) {
      var folderName = "Anh_Nghiem_Thu_Xa_Lan";
      var folders = DriveApp.getFoldersByName(folderName);
      var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder(folderName);

      var base64Data = data.image_base64.replace(/^data:image\/(png|jpeg|jpg);base64,/, "");
      var decoded = Utilities.base64Decode(base64Data);
      var fileName = (data.barge_id || "XALAN") + "_" + Utilities.formatDate(new Date(), "GMT+7", "yyyyMMdd_HHmmss") + ".jpg";
      var blob = Utilities.newBlob(decoded, "image/jpeg", fileName);
      var file = folder.createFile(blob);
      
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      fileUrl = file.getUrl();
      
      var directImgUrl = "https://drive.google.com/thumbnail?sz=w400&id=" + file.getId();
      imageFormula = '=IMAGE("' + directImgUrl + '")';
    }

    // Ghi dòng dữ liệu
    var timeStr = data.timestamp || Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss");
    var rowData = [
      timeStr,
      data.barge_id || "Chưa đặt tên",
      data.volume || 0,
      data.mass || 0,
      data.note || "",
      fileUrl ? '=HYPERLINK("' + fileUrl + '"; "📁 Xem ảnh gốc")' : "Không có",
      imageFormula
    ];

    sheet.appendRow(rowData);
    var newRow = sheet.getLastRow();
    
    // Tự động định dạng hàng mới
    formatDataRow(sheet, newRow);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      message: "Đã lưu thành công vào Google Sheet!",
      row: newRow,
      fileUrl: fileUrl
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ------------------------------------------------------------------------------
// HÀM TÌM SHEET & ĐỊNH DẠNG TỰ ĐỘNG
// ------------------------------------------------------------------------------
function getTargetSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (ss) return ss.getActiveSheet();

  var files = DriveApp.getFilesByName("Nhật Ký Nghiệm Thu Cát Xà Lan");
  if (files.hasNext()) {
    return SpreadsheetApp.open(files.next()).getActiveSheet();
  }
  var newSS = SpreadsheetApp.create("Nhật Ký Nghiệm Thu Cát Xà Lan");
  return newSS.getActiveSheet();
}

function formatSheetHeader(sheet) {
  if (sheet.getLastRow() === 0) {
    var headers = [
      "Thời Gian Nghiệm Thu", 
      "Mã Số Xà Lan", 
      "Thể Tích (m³)", 
      "Khối Lượng (tấn)", 
      "Ghi Chú Nghiệm Thu", 
      "Link Drive Ảnh Gốc", 
      "Hình Ảnh Hiện Trường"
    ];
    sheet.appendRow(headers);
    sheet.setFrozenRows(1); // Cố định dòng tiêu đề
  }

  // Chỉnh chiều rộng các cột chuẩn kỹ thuật
  sheet.setColumnWidth(1, 180); // Thời gian
  sheet.setColumnWidth(2, 140); // Mã tàu
  sheet.setColumnWidth(3, 130); // Thể tích
  sheet.setColumnWidth(4, 140); // Khối lượng
  sheet.setColumnWidth(5, 230); // Ghi chú
  sheet.setColumnWidth(6, 150); // Link Drive
  sheet.setColumnWidth(7, 180); // Ảnh thu nhỏ

  // Định dạng dòng tiêu đề
  var headerRange = sheet.getRange(1, 1, 1, 7);
  headerRange.setBackground("#0f172a") // Màu nền xanh đen Navy
             .setFontColor("#ffffff")  // Chữ trắng
             .setFontWeight("bold")
             .setFontSize(11)
             .setHorizontalAlignment("center")
             .setVerticalAlignment("middle");
  sheet.setRowHeight(1, 40);
}

function formatDataRow(sheet, rowIdx) {
  sheet.setRowHeight(rowIdx, 75); // Chiều cao hàng để thấy ảnh to rõ

  var rowRange = sheet.getRange(rowIdx, 1, 1, 7);
  
  // Kẻ khung viền mảnh màu xám đẹp
  rowRange.setBorder(true, true, true, true, true, true, "#cbd5e1", SpreadsheetApp.BorderStyle.SOLID);
  rowRange.setVerticalAlignment("middle");
  rowRange.setFontSize(10);

  // Nền xen kẽ (Zebra striping)
  if (rowIdx % 2 === 0) {
    rowRange.setBackground("#f8fafc"); // Dòng chẵn xám nhạt
  } else {
    rowRange.setBackground("#ffffff"); // Dòng lẻ trắng
  }

  // Căn lề từng cột
  sheet.getRange(rowIdx, 1).setHorizontalAlignment("center"); // Thời gian
  sheet.getRange(rowIdx, 2).setHorizontalAlignment("center").setFontWeight("bold").setFontColor("#1e40af"); // Mã tàu xanh đậm
  
  // Số thể tích & khối lượng
  sheet.getRange(rowIdx, 3).setHorizontalAlignment("right").setNumberFormat("#,##0.000").setFontWeight("bold").setFontColor("#b45309");
  sheet.getRange(rowIdx, 4).setHorizontalAlignment("right").setNumberFormat("#,##0.000").setFontWeight("bold").setFontColor("#15803d");
  
  sheet.getRange(rowIdx, 5).setHorizontalAlignment("left");   // Ghi chú
  sheet.getRange(rowIdx, 6).setHorizontalAlignment("center"); // Link Drive
  sheet.getRange(rowIdx, 7).setHorizontalAlignment("center"); // Ảnh thu nhỏ
}

// ------------------------------------------------------------------------------
// HÀM CHẠY THỬ ĐỂ KIỂM TRA ĐỊNH DẠNG NGAY TRONG APPS SCRIPT
// ------------------------------------------------------------------------------
function testChayThu() {
  var sheet = getTargetSheet();
  formatSheetHeader(sheet);
  
  var now = new Date();
  var timeStr = Utilities.formatDate(now, "GMT+7", "dd/MM/yyyy HH:mm:ss");
  
  sheet.appendRow([
    timeStr,
    "SG-8899",
    1406.990,
    2321.533,
    "Cát vàng san lấp - Bến Cát Lái",
    '=HYPERLINK("https://drive.google.com"; "📁 Xem ảnh gốc")',
    "Đang chờ ảnh"
  ]);
  
  var lastRow = sheet.getLastRow();
  formatDataRow(sheet, lastRow);
  Logger.log("ĐÃ GHI VÀ ĐỊNH DẠNG BẢNG TÍNH HOÀN HẢO!");
}
