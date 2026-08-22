# BỘ CÔNG CỤ TÍNH THỂ TÍCH & KHỐI LƯỢNG CÁT TRÊN XÀ LAN (BARGE SAND VOLUME CALCULATOR)

Ứng dụng Python GUI chuyên dụng phục vụ công tác nghiệm thu, đo đạc và tính toán chính xác thể tích (m³) cùng khối lượng (tấn) cát san lấp/cát xây dựng trên các phương tiện thủy nội địa (xà lan đáy bằng, xà lan đáy chữ V).

---

## 🌟 TÍNH NĂNG NỔI BẬT

1. **Hỗ trợ 2 loại đáy xà lan:**
   - **Đáy bằng (Flat bottom):** Chiều sâu tính từ mép thành xuống mặt đáy phẳng.
   - **Đáy chữ V (V-bottom):** Nhập trực tiếp **Chiều sâu mạn** và **Chiều dài cạnh nghiêng chữ V** (rất tiện lợi cho việc đo đạc thực địa mà không cần phải lặn đo tim sâu nhất).

2. **Mô hình hóa 4 dạng phân bố bề mặt cát thực tế:**
   - **Dạng 1 (Mặt phẳng):** Cát san phẳng đều trong lòng khoang.
   - **Dạng 2 (Dốc nghiêng):** Cát dốc nghiêng từ Đầu (Mũi) đến Đuôi (Lái).
   - **Dạng 3 (Hình Nón):** Nền phẳng kết hợp đống chóp nón (tiết diện elip/tròn), có kích thước chiều dài chân nón dọc tàu và chiều rộng chân nón ngang tàu.
   - **Dạng 4 (Vòm Nipple):** Nền phẳng kết hợp đụn cát vòm cong mượt (Paraboloid elip).

3. **Thuật toán Tích phân số 2D (Gauss-Legendre Quadrature 2D):**
   - Tính chính xác tuyệt đối thể tích miền không gian phức tạp.
   - Tự động quét tích phân trọn vẹn từ tận đáy nhọn chữ V lên đến đỉnh đống cát.

4. **Giao diện trực quan 3 góc nhìn động (Tkinter + Matplotlib):**
   - **Góc nhìn 3D không gian:** Khối xà lan 3D với bề mặt cát vàng nhạt xuyên thấu, quan sát toàn cảnh.
   - **Mặt cắt dọc (Side View):** Hiển thị rõ các kích thước đo độ hụt, chiều sâu và chiều cao cát.
   - **Mặt chiếu bằng (Top View):** Nhìn từ trên xuống lòng khoang L × B, hiển thị rõ kích thước chân đống nón / vòm núm.

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

### 1. Yêu cầu hệ thống
- Python 3.8 trở lên
- Các thư viện phụ thuộc: `numpy`, `matplotlib`

### 2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3. Chạy phần mềm
```bash
python tinh_the_tich_cat_xa_lan.py
```

---

## 📋 THƯ MỤC DỰ ÁN

```text
├── tinh_the_tich_cat_xa_lan.py    # Ứng dụng chính (Giao diện GUI + Đồ họa 3D/2D)
├── requirements.txt               # Danh sách thư viện phụ thuộc
├── .gitignore                     # Bỏ qua file rác và cache
└── README.md                      # Tài liệu hướng dẫn sử dụng
```

---

## 📐 NGUYÊN LÝ TÍNH TOÁN

- Chiều dày lớp cát tại mỗi tọa độ (x, y):
  $$h(x, y) = \max(D_{\text{đáy}}(y) - D_{\text{mặt cát}}(x, y), 0)$$
- Thể tích cát:
  $$V = \iint h(x, y) \, dx \, dy$$
- Khối lượng cát:
  $$M = V \times \rho \quad (\text{với } \rho \text{ là khối lượng riêng cát, mặc định 1.65 tấn/m³})$$
