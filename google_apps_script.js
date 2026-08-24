// ==============================================================================
// MÃ NGUỒN GOOGLE APPS SCRIPT HOÀN CHỈNH (TỰ ĐỘNG KẾT NỐI MỌI BẢNG TÍNH)
// ==============================================================================

function doPost(e) {
  try {
    // 1. Lấy dữ liệu gửi lên
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

    // 2. Tìm bảng tính Google Sheet:
    // - Ưu tiên bảng tính gắn liền (Container-bound)
    // - Nếu là script độc lập, tự tìm file "Nhật Ký Nghiệm Thu Cát Xà Lan" trên Google Drive
    var sheet = null;
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (ss) {
      sheet = ss.getActiveSheet();
    } else {
      var files = DriveApp.getFilesByName("Nhật Ký Nghiệm Thu Cát Xà Lan");
      if (files.hasNext()) {
        var file = files.next();
        sheet = SpreadsheetApp.open(file).getActiveSheet();
      } else {
        // Tự tạo mới nếu chưa có
        var newSS = SpreadsheetApp.create("Nhật Ký Nghiệm Thu Cát Xà Lan");
        sheet = newSS.getActiveSheet();
      }
    }

    // 3. Khởi tạo tiêu đề cột nếu sheet còn trống
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Thời Gian", 
        "Mã Số Xà Lan", 
        "Thể Tích (m³)", 
        "Khối Lượng (tấn)", 
        "Ghi Chú", 
        "Link Ảnh Gốc Drive", 
        "Ảnh Thu Nhỏ"
      ]);
      sheet.getRange(1, 1, 1, 7).setBackground("#0f172a").setFontColor("#ffffff").setFontWeight("bold");
    }

    var fileUrl = "";
    var imageFormula = "Không có ảnh";

    // 4. Lưu file ảnh vào Google Drive (nếu có ảnh)
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

    // 5. Ghi dòng dữ liệu mới vào Google Sheet
    var timeStr = data.timestamp || Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss");
    var rowData = [
      timeStr,
      data.barge_id || "Chưa đặt tên",
      data.volume || 0,
      data.mass || 0,
      data.note || "",
      fileUrl,
      imageFormula
    ];

    sheet.appendRow(rowData);
    var lastRow = sheet.getLastRow();
    sheet.setRowHeight(lastRow, 60);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      message: "Đã lưu thành công vào Google Sheet!",
      row: lastRow,
      fileUrl: fileUrl
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
