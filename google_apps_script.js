// ==============================================================================
// MÃ NGUỒN GOOGLE APPS SCRIPT (DÁN VÀO GOOGLE SHEETS)
// TỰ ĐỘNG LƯU ẢNH VÀO GOOGLE DRIVE VÀ GHI DÒNG VÀO GOOGLE SHEETS
// ==============================================================================

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // 1. Khởi tạo tiêu đề cột nếu sheet còn trống
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

    // 2. Lưu file ảnh vào Google Drive (nếu có ảnh đính kèm)
    if (data.image_base64 && data.image_base64.length > 50) {
      var folderName = "Anh_Nghiem_Thu_Xa_Lan";
      var folders = DriveApp.getFoldersByName(folderName);
      var folder;
      if (folders.hasNext()) {
        folder = folders.next();
      } else {
        folder = DriveApp.createFolder(folderName);
      }

      // Xử lý chuỗi Base64
      var base64Data = data.image_base64.replace(/^data:image\/(png|jpeg|jpg);base64,/, "");
      var decoded = Utilities.base64Decode(base64Data);
      var fileName = (data.barge_id || "XALAN") + "_" + Utilities.formatDate(new Date(), "GMT+7", "yyyyMMdd_HHmmss") + ".jpg";
      var blob = Utilities.newBlob(decoded, "image/jpeg", fileName);
      var file = folder.createFile(blob);
      
      // Cấp quyền xem cho mọi người có link
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      fileUrl = file.getUrl();
      
      // Link thumbnail trực tiếp để hiển thị trong Google Sheet
      var directImgUrl = "https://drive.google.com/thumbnail?sz=w400&id=" + file.getId();
      imageFormula = '=IMAGE("' + directImgUrl + '")';
    }

    // 3. Ghi dòng dữ liệu mới vào Google Sheet
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
    sheet.setRowHeight(lastRow, 60); // Tăng chiều cao dòng để hiện ảnh rõ ràng

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
