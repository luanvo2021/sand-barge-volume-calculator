// ==============================================================================
// MÃ NGUỒN GOOGLE APPS SCRIPT - LƯU CHÍNH XÁC VÀO FOLDER DRIVE & MỞ TRỰC TIẾP ẢNH
// ==============================================================================

// ID Folder Google Drive của bạn
var FOLDER_ID = "1Cv8U-pgFcVYSPfG3Qtu2neoIV2jXfpI0";

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

    var directFileUrl = "";
    var imageFormula = "Không có ảnh";

    // 1. Lưu ảnh trực tiếp vào Folder chỉ định
    if (data.image_base64 && data.image_base64.length > 50) {
      var folder = DriveApp.getFolderById(FOLDER_ID);

      var base64Data = data.image_base64.replace(/^data:image\/(png|jpeg|jpg);base64,/, "");
      var decoded = Utilities.base64Decode(base64Data);
      var timeStampName = Utilities.formatDate(new Date(), "GMT+7", "yyyyMMdd_HHmmss");
      var fileName = (data.barge_id || "XALAN") + "_" + timeStampName + ".jpg";
      
      var blob = Utilities.newBlob(decoded, "image/jpeg", fileName);
      var file = folder.createFile(blob);
      
      // Cho phép người có link xem trực tiếp ảnh
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      
      // Đường dẫn mở TRỰC TIẾP file ảnh đó (không mở cả thư mục)
      directFileUrl = "https://drive.google.com/file/d/" + file.getId() + "/view";
      
      // Công thức hiện ảnh thu nhỏ trực tiếp trong ô Sheet
      var directImgUrl = "https://drive.google.com/thumbnail?sz=w400&id=" + file.getId();
      imageFormula = '=IMAGE("' + directImgUrl + '")';
    }

    // 2. Ghi dòng dữ liệu
    var timeStr = data.timestamp || Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss");
    var rowData = [
      timeStr,
      data.barge_id || "Chưa đặt tên",
      data.volume || 0,
      data.mass || 0,
      data.note || "",
      directFileUrl ? '=HYPERLINK("' + directFileUrl + '"; "📁 Xem ảnh chi tiết")' : "Không có",
      imageFormula
    ];

    sheet.appendRow(rowData);
    var newRow = sheet.getLastRow();
    
    // Tự động kẻ bảng, dãn dòng và định dạng
    formatDataRow(sheet, newRow);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      message: "Đã lưu thành công vào Google Sheet!",
      row: newRow,
      fileUrl: directFileUrl
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ------------------------------------------------------------------------------
// HÀM TỰ ĐỘNG TẠO TIÊU ĐỀ & ĐỊNH DẠNG CỘT
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
      "Link Xem Ảnh Trực Tiếp", 
      "Hình Ảnh Hiện Trường"
    ];
    sheet.appendRow(headers);
  }
  sheet.setFrozenRows(1);

  sheet.setColumnWidth(1, 180);
  sheet.setColumnWidth(2, 140);
  sheet.setColumnWidth(3, 130);
  sheet.setColumnWidth(4, 140);
  sheet.setColumnWidth(5, 240);
  sheet.setColumnWidth(6, 170);
  sheet.setColumnWidth(7, 180);

  var headerRange = sheet.getRange(1, 1, 1, 7);
  headerRange.setBackground("#0f172a")
             .setFontColor("#ffffff")
             .setFontWeight("bold")
             .setFontSize(11)
             .setHorizontalAlignment("center")
             .setVerticalAlignment("middle");
  sheet.setRowHeight(1, 40);
}

function formatDataRow(sheet, rowIdx) {
  sheet.setRowHeight(rowIdx, 75);

  var rowRange = sheet.getRange(rowIdx, 1, 1, 7);
  rowRange.setBorder(true, true, true, true, true, true, "#cbd5e1", SpreadsheetApp.BorderStyle.SOLID);
  rowRange.setVerticalAlignment("middle");
  rowRange.setFontSize(10);

  if (rowIdx % 2 === 0) {
    rowRange.setBackground("#f8fafc");
  } else {
    rowRange.setBackground("#ffffff");
  }

  sheet.getRange(rowIdx, 1).setHorizontalAlignment("center");
  sheet.getRange(rowIdx, 2).setHorizontalAlignment("center").setFontWeight("bold").setFontColor("#1e40af");
  sheet.getRange(rowIdx, 3).setHorizontalAlignment("right").setNumberFormat("#,##0.000").setFontWeight("bold").setFontColor("#b45309");
  sheet.getRange(rowIdx, 4).setHorizontalAlignment("right").setNumberFormat("#,##0.000").setFontWeight("bold").setFontColor("#15803d");
  sheet.getRange(rowIdx, 5).setHorizontalAlignment("left");
  sheet.getRange(rowIdx, 6).setHorizontalAlignment("center");
  sheet.getRange(rowIdx, 7).setHorizontalAlignment("center");
}
