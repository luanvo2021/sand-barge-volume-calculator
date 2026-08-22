import math
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# PHẦN MỀM TÍNH THỂ TÍCH CÁT TRÊN XÀ LAN BẰNG TÍCH PHÂN 2D
# ============================================================

KHOI_LUONG_RIENG_MAC_DINH = 1.65  # tấn/m3


class MoHinhTheTichCat:
    def __init__(self, chieu_dai, chieu_rong, loai_day, thong_so_day, loai_mat, thong_so_mat):
        self.chieu_dai = chieu_dai
        self.chieu_rong = chieu_rong
        self.loai_day = loai_day
        self.thong_so_day = thong_so_day
        self.loai_mat = loai_mat
        self.thong_so_mat = thong_so_mat

    def do_sau_day(self, x, y):
        if self.loai_day == "Đáy bằng":
            return self.thong_so_day["sau_day"]

        if self.loai_day == "Đáy chữ V":
            sau_man = self.thong_so_day["sau_man"]
            canh_nghieng_V = self.thong_so_day["canh_nghieng_V"]
            nua_rong = self.chieu_rong / 2.0
            do_ha_sau_V = math.sqrt(max(canh_nghieng_V**2 - nua_rong**2, 0.0))
            return sau_man + do_ha_sau_V * (1.0 - 2.0 * abs(y) / self.chieu_rong)

        raise ValueError("Loại đáy xà lan không hợp lệ.")

    def do_sau_mat_cat(self, x, y):
        p = self.thong_so_mat

        # TRƯỜNG HỢP 1: Bề mặt phẳng
        if self.loai_mat == 1:
            return p["do_hut_cat"]

        # TRƯỜNG HỢP 2: Dốc nghiêng từ Đầu đến Đuôi
        if self.loai_mat == 2:
            hut_dau = p["do_hut_dau"]
            hut_duoi = p["do_hut_duoi"]
            return hut_dau + (hut_duoi - hut_dau) * (x / self.chieu_dai)

        # TRƯỜNG HỢP 3: Hình NÓN
        if self.loai_mat == 3:
            hut_nen = p["do_hut_nen"]
            cao_non = p["cao_non"]
            dai_chan_non = p["dai_chan_non"]
            rong_chan_non = p["rong_chan_non"]

            tam_x = self.chieu_dai / 2.0
            tam_y = 0.0

            ban_truc_a = dai_chan_non / 2.0
            ban_truc_b = rong_chan_non / 2.0

            he_so_x = (x - tam_x) / ban_truc_a
            he_so_y = (y - tam_y) / ban_truc_b
            ban_kinh_r = math.sqrt(he_so_x**2 + he_so_y**2)

            if ban_kinh_r <= 1.0:
                chieu_cao_non = cao_non * (1.0 - ban_kinh_r)
            else:
                chieu_cao_non = 0.0

            return hut_nen - chieu_cao_non

        # TRƯỜNG HỢP 4: Vòm NIPPLE
        if self.loai_mat == 4:
            hut_nen = p["do_hut_nen"]
            cao_num = p["cao_num"]
            dai_chan_num = p["dai_chan_num"]
            rong_chan_num = p["rong_chan_num"]

            tam_x = self.chieu_dai / 2.0
            tam_y = 0.0

            ban_truc_a = dai_chan_num / 2.0
            ban_truc_b = rong_chan_num / 2.0

            he_so_x = (x - tam_x) / ban_truc_a
            he_so_y = (y - tam_y) / ban_truc_b
            he_so_tong = he_so_x**2 + he_so_y**2

            chieu_cao_num = cao_num * max(1.0 - he_so_tong, 0.0)
            return hut_nen - chieu_cao_num

        raise ValueError("Dạng bề mặt cát không hợp lệ.")

    def chieu_day_cat(self, x, y):
        sau_day = self.do_sau_day(x, y)
        sau_mat = self.do_sau_mat_cat(x, y)
        return max(sau_day - sau_mat, 0.0)

    def tinh_the_tich(self, so_bac=120):
        diem_nut, trong_so = np.polynomial.legendre.leggauss(so_bac)

        x_nut = 0.5 * self.chieu_dai * (diem_nut + 1.0)
        x_trong_so = 0.5 * self.chieu_dai * trong_so

        y_nut = 0.5 * self.chieu_rong * diem_nut
        y_trong_so = 0.5 * self.chieu_rong * trong_so

        the_tich = 0.0
        for i, x in enumerate(x_nut):
            for j, y in enumerate(y_nut):
                the_tich += (
                    x_trong_so[i]
                    * y_trong_so[j]
                    * self.chieu_day_cat(float(x), float(y))
                )

        return float(the_tich)


# ============================================================
# GIAO DIỆN PHẦN MỀM (GUI TKINTER)
# ============================================================

class UngDungTinhTheTich:
    def __init__(self, root):
        self.root = root
        self.root.title("PHẦN MỀM TÍNH THỂ TÍCH CÁT TRÊN XÀ LAN (TÍCH HỢP 3D, MẶT CẮT, MẶT BẰNG)")
        self.root.geometry("1400x920")
        self.root.minsize(1240, 840)

        self.o_nhap_lieu = {}

        self._tao_giao_dien()
        self._cap_nhat_giao_dien_toan_bo()

    def tao_o_nhap(self, khung_chua, hang, ma_khoa, ten_nhan, gia_tri_mac_dinh, don_vi="m", chu_thich=""):
        nhan = ttk.Label(khung_chua, text=ten_nhan, font=("Segoe UI", 9, "bold"))
        nhan.grid(row=hang, column=0, sticky="w", padx=6, pady=3)

        khung_gia_tri = ttk.Frame(khung_chua)
        khung_gia_tri.grid(row=hang, column=1, sticky="w", padx=6, pady=3)

        o_nhap = ttk.Entry(khung_gia_tri, width=11, font=("Segoe UI", 9))
        o_nhap.insert(0, str(gia_tri_mac_dinh))
        o_nhap.pack(side="left")

        ttk.Label(khung_gia_tri, text=f" {don_vi}", font=("Segoe UI", 9)).pack(side="left")

        if chu_thich:
            ttk.Label(
                khung_chua, text=chu_thich, font=("Segoe UI", 8, "italic"), foreground="#555555"
            ).grid(row=hang, column=2, sticky="w", padx=6, pady=3)

        self.o_nhap_lieu[ma_khoa] = o_nhap
        return o_nhap

    def _tao_giao_dien(self):
        khung_tong = ttk.Frame(self.root)
        khung_tong.pack(fill="both", expand=True, padx=8, pady=8)

        # CỘT TRÁI: NHẬP LIỆU
        cot_trai = ttk.Frame(khung_tong)
        cot_trai.pack(side="left", fill="both", expand=False, padx=(0, 6))

        # 1. KÍCH THƯỚC XÀ LAN
        khung_xa_lan = ttk.LabelFrame(cot_trai, text="1. KÍCH THƯỚC KHOANG CHỨA CỦA XÀ LAN")
        khung_xa_lan.pack(fill="x", pady=4)

        self.tao_o_nhap(khung_xa_lan, 0, "chieu_dai", "Chiều dài lòng khoang chứa:", 60.0, "m", "Dài khoang")
        self.tao_o_nhap(khung_xa_lan, 1, "chieu_rong", "Chiều rộng lòng khoang chứa:", 12.0, "m", "Rộng khoang")

        ttk.Label(khung_xa_lan, text="Dạng đáy xà lan:", font=("Segoe UI", 9, "bold")).grid(
            row=2, column=0, sticky="w", padx=6, pady=3
        )

        self.bien_loai_day = tk.StringVar(value="Đáy bằng")
        hop_loai_day = ttk.Combobox(
            khung_xa_lan,
            textvariable=self.bien_loai_day,
            values=["Đáy bằng", "Đáy chữ V"],
            state="readonly",
            width=16,
            font=("Segoe UI", 9)
        )
        hop_loai_day.grid(row=2, column=1, sticky="w", padx=6, pady=3)
        hop_loai_day.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_giao_dien_toan_bo())

        self.khung_day_dong = ttk.Frame(khung_xa_lan)
        self.khung_day_dong.grid(row=3, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 2. DẠNG BỀ MẶT CÁT
        khung_mat_cat = ttk.LabelFrame(cot_trai, text="2. DẠNG PHÂN BỐ BỀ MẶT CÁT")
        khung_mat_cat.pack(fill="x", pady=4)

        ttk.Label(khung_mat_cat, text="Chọn dạng bề mặt cát:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=6, pady=3
        )

        self.bien_loai_mat = tk.StringVar(value="1 - Mặt phẳng (Dàn trải đều)")
        hop_loai_mat = ttk.Combobox(
            khung_mat_cat,
            textvariable=self.bien_loai_mat,
            values=[
                "1 - Mặt phẳng (Dàn trải đều)",
                "2 - Dốc nghiêng trải dài từ Đầu đến Đuôi",
                "3 - Nền phẳng + Đỉnh hình nón (Mặt cắt tam giác)",
                "4 - Nền phẳng + Đỉnh vòm núm cong mượt (Nipple)",
            ],
            state="readonly",
            width=40,
            font=("Segoe UI", 9)
        )
        hop_loai_mat.grid(row=0, column=1, sticky="w", padx=6, pady=3)
        hop_loai_mat.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_giao_dien_toan_bo())

        self.khung_mat_dong = ttk.Frame(khung_mat_cat)
        self.khung_mat_dong.grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 3. KHỐI LƯỢNG RIÊNG
        khung_vat_lieu = ttk.LabelFrame(cot_trai, text="3. KHỐI LƯỢNG RIÊNG")
        khung_vat_lieu.pack(fill="x", pady=4)

        self.tao_o_nhap(
            khung_vat_lieu, 0, "khoi_luong_rieng", "Khối lượng riêng của cát:", KHOI_LUONG_RIENG_MAC_DINH, "tấn/m³",
            "Mặc định 1.65 tấn/m³"
        )

        # 4. NÚT ĐIỀU KHIỂN
        khung_nut = ttk.Frame(cot_trai)
        khung_nut.pack(fill="x", pady=4)

        nut_tinh = ttk.Button(khung_nut, text="▶ TÍNH THỂ TÍCH & KHỐI LƯỢNG", command=self.thuc_hien_tinh_toan)
        nut_tinh.pack(side="left", padx=4, ipadx=8, ipady=3)

        nut_xoa = ttk.Button(khung_nut, text="Làm mới lại", command=self.xoa_ket_qua)
        nut_xoa.pack(side="left", padx=4, ipadx=4, ipady=3)

        # 5. KẾT QUẢ
        khung_ket_qua = ttk.LabelFrame(cot_trai, text="4. BÁO CÁO KẾT QUẢ TÍNH TOÁN")
        khung_ket_qua.pack(fill="both", expand=True, pady=4)

        self.o_ket_qua = tk.Text(
            khung_ket_qua,
            height=9,
            width=56,
            wrap="word",
            font=("Consolas", 9),
            bg="#fcfcfc"
        )
        self.o_ket_qua.pack(fill="both", expand=True, padx=4, pady=4)

        # CỘT PHẢI: KHUNG ĐỒ HỌA
        cot_phai = ttk.LabelFrame(khung_tong, text="🔍 HÌNH ẢNH TRỰC QUAN 3 GÓC NHÌN (3D - MẶT CẮT - MẶT BẰNG)")
        cot_phai.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self.fig = plt.figure(figsize=(7.6, 8.6), dpi=110, facecolor='#ffffff')
        self.canvas = FigureCanvasTkAgg(self.fig, master=cot_phai)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)

        self.xoa_ket_qua()

    def _cap_nhat_giao_dien_toan_bo(self):
        self._cap_nhat_o_nhap_day()
        self._cap_nhat_o_nhap_mat_cat()
        self._ve_hinh_minh_hoa()

    def _cap_nhat_o_nhap_day(self):
        for w in self.khung_day_dong.winfo_children():
            w.destroy()

        if self.bien_loai_day.get() == "Đáy bằng":
            self.tao_o_nhap(
                self.khung_day_dong, 0, "sau_day",
                "Chiều sâu khoang xà lan:", 3.0, "m",
                "Đo từ mép trên thành xuống đáy phẳng"
            )
        else:
            self.tao_o_nhap(
                self.khung_day_dong, 0, "sau_man",
                "Chiều sâu đáy tại 2 bên mạn:", 2.0, "m",
                "Đo từ mép trên thành xuống đáy sát mạn"
            )
            self.tao_o_nhap(
                self.khung_day_dong, 1, "canh_nghieng_V",
                "Chiều dài 1 cạnh nghiêng chữ V:", 6.5, "m",
                "Kéo thước dọc sàn nghiêng từ mạn xuống tim đáy"
            )

    def _cap_nhat_o_nhap_mat_cat(self):
        for w in self.khung_mat_dong.winfo_children():
            w.destroy()

        loai_mat = int(self.bien_loai_mat.get()[0])

        if loai_mat == 1:
            self.tao_o_nhap(
                self.khung_mat_dong, 0, "do_hut_cat",
                "Độ hụt mặt cát từ mép thành:", 1.0, "m",
                "Thả thước từ mép thành xuống cát (nhô cao nhập số âm)"
            )

        elif loai_mat == 2:
            self.tao_o_nhap(
                self.khung_mat_dong, 0, "do_hut_dau",
                "Độ hụt mặt cát tại ĐẦU tàu:", 0.8, "m",
                "Thả thước từ mép thành tại mũi/đầu xà lan"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 1, "do_hut_duoi",
                "Độ hụt mặt cát tại ĐUÔI tàu:", 1.8, "m",
                "Thả thước từ mép thành tại lái/đuôi xà lan"
            )

        elif loai_mat == 3:
            self.tao_o_nhap(
                self.khung_mat_dong, 0, "do_hut_nen",
                "Độ hụt của lớp cát phẳng nền:", 1.5, "m",
                "Độ sâu của mặt cát phẳng xung quanh chân đống nón"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 1, "cao_non",
                "Chiều cao đống nón cát nhô lên:", 0.8, "m",
                "Đo từ đỉnh chóp nón xuống mặt phẳng nền"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 2, "dai_chan_non",
                "Chiều dài chân đống nón (dọc tàu):", 12.0, "m",
                "Đường kính chân đống nón theo chiều dọc xà lan"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 3, "rong_chan_non",
                "Chiều rộng chân đống nón (ngang tàu):", 8.0, "m",
                "Đường kính chân đống nón theo chiều ngang xà lan"
            )

        elif loai_mat == 4:
            self.tao_o_nhap(
                self.khung_mat_dong, 0, "do_hut_nen",
                "Độ hụt của lớp cát phẳng nền:", 1.5, "m",
                "Độ sâu của mặt cát phẳng xung quanh chân đụn cát"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 1, "cao_num",
                "Chiều cao đỉnh núm cát nhô lên:", 0.8, "m",
                "Đo từ đỉnh vòm cong cao nhất xuống mặt phẳng nền"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 2, "dai_chan_num",
                "Chiều dài chân đụn cát (dọc tàu):", 24.0, "m",
                "Toàn bộ chiều dài chân đụn cát theo chiều dọc"
            )
            self.tao_o_nhap(
                self.khung_mat_dong, 3, "rong_chan_num",
                "Chiều rộng chân đụn cát (ngang tàu):", 8.0, "m",
                "Toàn bộ chiều rộng chân đụn cát theo chiều ngang"
            )

    # --------------------------------------------------------
    # VẼ HÌNH MINH HỌA (3D: VÀNG NHẠT XUYÊN THẤU | 2D: VÀNG ĐẬM RÕ RÀNG NHƯ CŨ)
    # --------------------------------------------------------
    def _ve_hinh_minh_hoa(self):
        self.fig.clf()

        # TĂNG TỶ LỆ HÌNH 3D TO HƠN
        gs = self.fig.add_gridspec(2, 2, height_ratios=[1.7, 1.0], hspace=0.26, wspace=0.2)

        # 3 Subplot
        ax_3d = self.fig.add_subplot(gs[0, :], projection='3d')
        ax_sec = self.fig.add_subplot(gs[1, 0])
        ax_top = self.fig.add_subplot(gs[1, 1])

        # 1. MÀU DÙNG CHO 3D: VÀNG NHẠT XUYÊN THẤU
        C_SAND_3D = '#f9e79f'         # Vàng nhạt cát
        C_SAND_DARK_3D = '#d4ac0d'    # Viền vàng cát
        ALPHA_SAND_3D = 0.50          # Độ xuyên thấu trong suốt cho 3D

        # 2. MÀU DÙNG CHO 2D: VÀNG ĐẬM RÕ NÉT NHƯ CŨ
        C_SAND_2D = '#e5b869'         # Màu cát vàng chuẩn như cũ
        C_SAND_DARK_2D = '#b8860b'    # Viền đậm
        C_SAND_CONE_2D = '#d4a047'    # Chóp nón vàng đậm
        
        C_HULL_SIDE = '#5d6d7e'       # Thành xà lan
        C_HULL_BOTTOM = '#78281f'     # Đáy nâu đỏ
        C_CABIN = '#2471a3'           # Cabin xanh
        C_MEASURE = '#ba4a00'         # Màu đo thước
        C_LINE = '#c0392b'            # Đường mốc

        loai_day = self.bien_loai_day.get()
        loai_mat = int(self.bien_loai_mat.get()[0])

        L_d = 40.0
        B_d = 12.0
        H_wall = 3.0
        x_mid = L_d / 2.0

        # Grid cho 3D
        x_grid = np.linspace(0, L_d, 40)
        y_grid = np.linspace(-B_d/2, B_d/2, 25)
        X, Y = np.meshgrid(x_grid, y_grid)

        # =====================================================
        # 1. TÍNH TOÁN BỀ MẶT CÁT & VẼ 3D (CÁT XUYÊN THẤU VÀNG NHẠT)
        # =====================================================
        if loai_mat == 1:
            h_cat_d = 2.0
            Z_3d = np.full_like(X, h_cat_d)
            ten_th = "TH1: MẶT PHẲNG (DÀN TRẢI ĐỀU)"
        elif loai_mat == 2:
            h_dau_d = 2.5
            h_duoi_d = 0.7
            Z_3d = h_dau_d - (h_dau_d - h_duoi_d) * (X / L_d)
            ten_th = "TH2: DỐC TỪ ĐẦU ĐẾN ĐUÔI"
        elif loai_mat == 3:
            h_nen_d = 1.2
            H_non_d = 2.0
            D_doc_d = 20.0
            D_ngang_d = 8.0
            r_c = np.sqrt(((X - x_mid)/(D_doc_d/2))**2 + (Y/(D_ngang_d/2))**2)
            Z_3d = h_nen_d + np.maximum(0.0, H_non_d * (1.0 - r_c))
            ten_th = "TH3: NỀN PHẲNG + ĐỈNH HÌNH NÓN"
        elif loai_mat == 4:
            h_nen_d = 1.2
            H_num_d = 2.0
            D_doc_d = 24.0
            D_ngang_d = 8.0
            r_c_sq = ((X - x_mid)/(D_doc_d/2))**2 + (Y/(D_ngang_d/2))**2
            Z_3d = h_nen_d + H_num_d * np.maximum(0.0, 1.0 - r_c_sq)
            ten_th = "TH4: NỀN PHẲNG + VÒM NÚM NIPPLE"

        # Vẽ bề mặt cát 3D vàng nhạt xuyên thấu
        ax_3d.plot_surface(X, Y, Z_3d, color=C_SAND_3D, alpha=ALPHA_SAND_3D, edgecolor=C_SAND_DARK_3D, lw=0.15, shade=True)

        # Sàn đáy xà lan 3D
        if loai_day == "Đáy chữ V":
            Hv_3d = 1.6
            v_bottom_l = [[0, -B_d/2, 0], [L_d, -B_d/2, 0], [L_d, 0, -Hv_3d], [0, 0, -Hv_3d]]
            v_bottom_r = [[0, B_d/2, 0], [L_d, B_d/2, 0], [L_d, 0, -Hv_3d], [0, 0, -Hv_3d]]
            ax_3d.add_collection3d(Poly3DCollection([v_bottom_l, v_bottom_r], facecolors=C_HULL_BOTTOM, edgecolors='darkred', alpha=0.9, lw=0.8))
        else:
            flat_bottom = [[0, -B_d/2, 0], [L_d, -B_d/2, 0], [L_d, B_d/2, 0], [0, B_d/2, 0]]
            ax_3d.add_collection3d(Poly3DCollection([flat_bottom], facecolors=C_HULL_BOTTOM, edgecolors='black', alpha=0.9, lw=0.8))

        # Vách thành xà lan 3D
        left_w = [[0, -B_d/2, 0], [L_d, -B_d/2, 0], [L_d, -B_d/2, H_wall], [0, -B_d/2, H_wall]]
        right_w = [[0, B_d/2, 0], [L_d, B_d/2, 0], [L_d, B_d/2, H_wall], [0, B_d/2, H_wall]]
        front_w = [[0, -B_d/2, 0], [0, B_d/2, 0], [0, B_d/2, H_wall], [0, -B_d/2, H_wall]]
        back_w = [[L_d, -B_d/2, 0], [L_d, B_d/2, 0], [L_d, B_d/2, H_wall], [L_d, -B_d/2, H_wall]]
        ax_3d.add_collection3d(Poly3DCollection([left_w, right_w, front_w, back_w], facecolors=C_HULL_SIDE, edgecolors='black', alpha=0.5, lw=0.6))

        # Cabin buồng lái ở đuôi
        cabin_p = [
            [[L_d+1, -2.5, H_wall], [L_d+4, -2.5, H_wall], [L_d+4, 2.5, H_wall], [L_d+1, 2.5, H_wall]],
            [[L_d+1, -2.5, H_wall+2.0], [L_d+4, -2.5, H_wall+2.0], [L_d+4, 2.5, H_wall+2.0], [L_d+1, 2.5, H_wall+2.0]],
            [[L_d+1, -2.5, H_wall], [L_d+4, -2.5, H_wall], [L_d+4, -2.5, H_wall+2.0], [L_d+1, -2.5, H_wall+2.0]],
            [[L_d+1, 2.5, H_wall], [L_d+4, 2.5, H_wall], [L_d+4, 2.5, H_wall+2.0], [L_d+1, 2.5, H_wall+2.0]],
            [[L_d+1, -2.5, H_wall], [L_d+1, 2.5, H_wall], [L_d+1, 2.5, H_wall+2.0], [L_d+1, -2.5, H_wall+2.0]]
        ]
        ax_3d.add_collection3d(Poly3DCollection(cabin_p, facecolors=C_CABIN, edgecolors='navy', alpha=0.9, lw=0.6))

        ax_3d.set_title(f"1. GÓC NHÌN 3D KHÔNG GIAN (CÁT XUYÊN THẤU) - {ten_th}", fontsize=11, fontweight='bold', color='#0b2545', pad=4)
        ax_3d.set_xlim(-3, L_d+5)
        ax_3d.set_ylim(-B_d/2-2.5, B_d/2+2.5)
        ax_3d.set_zlim(-1.8 if loai_day == "Đáy chữ V" else -0.5, H_wall + 2.5)
        ax_3d.view_init(elev=26, azim=-58)
        ax_3d.set_axis_off()

        # =====================================================
        # 2. VẼ MẶT CẮT DỌC (SIDE VIEW) - MÀU CÁT 2D VÀNG ĐẬM RÕ NÉT NHƯ CŨ
        # =====================================================
        y_rim = 5.5
        y_bot = 1.8
        y_tim_v = y_bot - 1.2

        ax_sec.axhline(y_rim, color=C_LINE, linestyle='--', lw=1.2)
        ax_sec.text(x_mid, y_rim + 0.15, 'MÉP TRÊN THÀNH (0.0m)', color=C_LINE, fontsize=7.5, fontweight='bold', ha='center')

        if loai_mat == 1:
            h_cat = y_rim - 1.5
            if loai_day == "Đáy bằng":
                ax_sec.fill([0, L_d, L_d, 0], [y_bot, y_bot, h_cat, h_cat], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.5)
            else:
                ax_sec.fill([0, x_mid, L_d, L_d, 0], [y_bot, y_tim_v, y_bot, h_cat, h_cat], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.5)
                ax_sec.plot([0, L_d], [y_bot, y_bot], color='#8b5a2b', linestyle=':', lw=0.8)
            ax_sec.annotate('', xy=(x_mid, h_cat), xytext=(x_mid, y_rim), arrowprops=dict(arrowstyle='<->', color=C_MEASURE, lw=1.8))
            ax_sec.text(x_mid + 0.8, (h_cat + y_rim)/2, 'Độ hụt mặt cát', color=C_MEASURE, fontsize=8, fontweight='bold', va='center')

        elif loai_mat == 2:
            h_dau = y_rim - 1.0
            h_duoi = y_rim - 2.5
            if loai_day == "Đáy bằng":
                ax_sec.fill([0, L_d, L_d, 0], [y_bot, y_bot, h_duoi, h_dau], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.5)
            else:
                ax_sec.fill([0, x_mid, L_d, L_d, 0], [y_bot, y_tim_v, y_bot, h_duoi, h_dau], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.5)
                ax_sec.plot([0, L_d], [y_bot, y_bot], color='#8b5a2b', linestyle=':', lw=0.8)
            ax_sec.annotate('', xy=(2.5, h_dau), xytext=(2.5, y_rim), arrowprops=dict(arrowstyle='<->', color=C_MEASURE, lw=1.8))
            ax_sec.text(2.5, h_dau - 0.3, 'Độ hụt ĐẦU', color=C_MEASURE, fontsize=7.5, fontweight='bold', ha='center', va='top')
            ax_sec.annotate('', xy=(L_d - 2.5, h_duoi), xytext=(L_d - 2.5, y_rim), arrowprops=dict(arrowstyle='<->', color='#2980b9', lw=1.8))
            ax_sec.text(L_d - 2.5, h_duoi - 0.3, 'Độ hụt ĐUÔI', color='#2980b9', fontsize=7.5, fontweight='bold', ha='center', va='top')

        elif loai_mat == 3:
            h_nen = y_rim - 2.0
            H_non_w = 1.4
            D_non_w = 16.0
            if loai_day == "Đáy bằng":
                ax_sec.fill([0, L_d, L_d, 0], [y_bot, y_bot, h_nen, h_nen], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.2)
            else:
                ax_sec.fill([0, x_mid, L_d, L_d, 0], [y_bot, y_tim_v, y_bot, h_nen, h_nen], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.2)
                ax_sec.plot([0, L_d], [y_bot, y_bot], color='#8b5a2b', linestyle=':', lw=0.8)
            ax_sec.fill([x_mid - D_non_w/2, x_mid, x_mid + D_non_w/2], [h_nen, h_nen + H_non_w, h_nen], color=C_SAND_CONE_2D, edgecolor=C_SAND_DARK_2D, lw=1.5)
            ax_sec.annotate('', xy=(2.5, h_nen), xytext=(2.5, y_rim), arrowprops=dict(arrowstyle='<->', color=C_MEASURE, lw=1.5))
            ax_sec.text(2.5, (h_nen + y_rim)/2, 'Độ hụt nền', color=C_MEASURE, fontsize=7.5, fontweight='bold', ha='center', va='center')
            ax_sec.annotate('', xy=(x_mid, h_nen + H_non_w), xytext=(x_mid, h_nen), arrowprops=dict(arrowstyle='<->', color='#27ae60', lw=1.8))
            ax_sec.text(x_mid + 0.6, (h_nen*2 + H_non_w)/2, 'Cao nón', color='#27ae60', fontsize=8, fontweight='bold', va='center')

        elif loai_mat == 4:
            h_nen = y_rim - 2.0
            H_num_w = 1.4
            D_num_w = 18.0
            if loai_day == "Đáy bằng":
                ax_sec.fill([0, L_d, L_d, 0], [y_bot, y_bot, h_nen, h_nen], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.2)
            else:
                ax_sec.fill([0, x_mid, L_d, L_d, 0], [y_bot, y_tim_v, y_bot, h_nen, h_nen], color=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.2)
                ax_sec.plot([0, L_d], [y_bot, y_bot], color='#8b5a2b', linestyle=':', lw=0.8)
            x_l = np.linspace(0, L_d, 150)
            z_n = h_nen + H_num_w * np.maximum(0.0, 1.0 - ((x_l - x_mid)/(D_num_w/2))**2)
            ax_sec.fill_between(x_l, h_nen, z_n, color=C_SAND_CONE_2D, edgecolor=C_SAND_DARK_2D, lw=1.5)
            ax_sec.annotate('', xy=(2.5, h_nen), xytext=(2.5, y_rim), arrowprops=dict(arrowstyle='<->', color=C_MEASURE, lw=1.5))
            ax_sec.text(2.5, (h_nen + y_rim)/2, 'Độ hụt nền', color=C_MEASURE, fontsize=7.5, fontweight='bold', ha='center', va='center')
            ax_sec.annotate('', xy=(x_mid, h_nen + H_num_w), xytext=(x_mid, h_nen), arrowprops=dict(arrowstyle='<->', color='#27ae60', lw=1.8))
            ax_sec.text(x_mid + 0.6, (h_nen*2 + H_num_w)/2, 'Cao núm', color='#27ae60', fontsize=8, fontweight='bold', va='center')

        # Khung thân và đáy 2D
        if loai_day == "Đáy bằng":
            ax_sec.plot([-1.5, 0, L_d, L_d+1.5], [y_rim, y_bot, y_bot, y_rim], color=C_HULL_SIDE, lw=2.5)
        else:
            ax_sec.plot([0, x_mid, L_d], [y_bot, y_tim_v, y_bot], color=C_HULL_BOTTOM, lw=3)
            ax_sec.plot([0, 0], [y_bot, y_rim], color=C_HULL_SIDE, lw=2.5)
            ax_sec.plot([L_d, L_d], [y_bot, y_rim], color=C_HULL_SIDE, lw=2.5)

        ax_sec.set_title("2. MẶT CẮT DỌC (SIDE VIEW)", fontsize=9.5, fontweight='bold', color='#0b2545', pad=2)
        ax_sec.set_xlim(-3, L_d + 3)
        ax_sec.set_ylim(-0.2 if loai_day == "Đáy chữ V" else 0.8, y_rim + 1.0)
        ax_sec.axis('off')

        # =====================================================
        # 3. VẼ MẶT CHIẾU BẰNG (TOP VIEW) - MÀU CÁT 2D VÀNG ĐẬM RÕ NÉT NHƯ CŨ
        # =====================================================
        ax_top.add_patch(patches.Rectangle((-2.5, -B_d/2 - 0.6), L_d + 6.5, B_d + 1.2, facecolor=C_HULL_SIDE, edgecolor='black', lw=1.0))
        ax_top.add_patch(patches.Rectangle((L_d + 0.5, -2.5), 3, 5, facecolor=C_CABIN, edgecolor='navy', lw=1.0))
        ax_top.add_patch(patches.Rectangle((0, -B_d/2), L_d, B_d, facecolor=C_SAND_2D, edgecolor=C_SAND_DARK_2D, lw=1.0))

        if loai_mat == 1:
            ax_top.text(x_mid, 0, 'CÁT DÀN PHẲNG ĐỀU (L × B)', color='#5a3e1b', fontsize=8.5, fontweight='bold', ha='center', va='center')
        elif loai_mat == 2:
            ax_top.plot([0, L_d], [-B_d/2, B_d/2], color='red', linestyle='--', lw=1.2)
            ax_top.annotate('', xy=(L_d - 4, 0), xytext=(4, 0), arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
            ax_top.text(x_mid, 1.2, 'Hướng dốc từ Đầu ➔ Đuôi', color='red', fontsize=8, fontweight='bold', ha='center')
        elif loai_mat == 3:
            d_doc_t = 16.0
            d_ngang_t = 7.5
            elip_c = patches.Ellipse((x_mid, 0), d_doc_t, d_ngang_t, facecolor=C_SAND_CONE_2D, edgecolor=C_SAND_DARK_2D, lw=1.2)
            ax_top.add_patch(elip_c)
            ax_top.plot(x_mid, 0, 'ro', markersize=3)
            ax_top.annotate('', xy=(x_mid - d_doc_t/2, 0), xytext=(x_mid + d_doc_t/2, 0), arrowprops=dict(arrowstyle='<->', color='#8e44ad', lw=1.4))
            ax_top.text(x_mid, 0.8, 'Dài chân nón', color='#8e44ad', fontsize=7.5, fontweight='bold', ha='center')
            ax_top.annotate('', xy=(x_mid, -d_ngang_t/2), xytext=(x_mid, d_ngang_t/2), arrowprops=dict(arrowstyle='<->', color='#2980b9', lw=1.4))
            ax_top.text(x_mid + d_doc_t/2 + 0.8, 0, 'Rộng nón', color='#2980b9', fontsize=7.5, fontweight='bold', va='center')
        elif loai_mat == 4:
            d_doc_t = 20.0
            d_ngang_t = 8.0
            for rx, ry in [(d_doc_t, d_ngang_t), (d_doc_t*0.65, d_ngang_t*0.65), (d_doc_t*0.35, d_ngang_t*0.35)]:
                elip_n = patches.Ellipse((x_mid, 0), rx, ry, fill=False, edgecolor='red', linestyle='--', lw=1.0)
                ax_top.add_patch(elip_n)
            ax_top.plot(x_mid, 0, 'ro', markersize=3)
            ax_top.annotate('', xy=(x_mid - d_doc_t/2, 0), xytext=(x_mid + d_doc_t/2, 0), arrowprops=dict(arrowstyle='<->', color='#8e44ad', lw=1.4))
            ax_top.text(x_mid, 0.8, 'Dài chân đụn (dọc)', color='#8e44ad', fontsize=7.5, fontweight='bold', ha='center')
            ax_top.annotate('', xy=(x_mid, -d_ngang_t/2), xytext=(x_mid, d_ngang_t/2), arrowprops=dict(arrowstyle='<->', color='#2980b9', lw=1.4))
            ax_top.text(x_mid + d_doc_t/2 + 0.8, 0, 'Rộng đụn\n(ngang)', color='#2980b9', fontsize=7.5, fontweight='bold', va='center')

        # Kích thước L, B
        ax_top.annotate('', xy=(0, -B_d/2 - 1.2), xytext=(L_d, -B_d/2 - 1.2), arrowprops=dict(arrowstyle='<->', color='blue', lw=1.2))
        ax_top.text(x_mid, -B_d/2 - 2.5, 'Dài L', fontsize=8, fontweight='bold', color='blue', ha='center')

        ax_top.set_title("3. MẶT CHIẾU BẰNG (TOP VIEW)", fontsize=9.5, fontweight='bold', color='#0b2545', pad=2)
        ax_top.set_xlim(-4, L_d + 8)
        ax_top.set_ylim(-B_d/2 - 3.2, B_d/2 + 2.0)
        ax_top.axis('off')

        self.canvas.draw()

    # --------------------------------------------------------
    # TÍNH TOÁN
    # --------------------------------------------------------
    def _lay_so_thuc(self, ma_khoa, ten_hien_thi):
        try:
            gia_tri = float(self.o_nhap_lieu[ma_khoa].get().strip())
        except Exception:
            raise ValueError(f"'{ten_hien_thi}': giá trị nhập vào không đúng định dạng số.")
        if not math.isfinite(gia_tri):
            raise ValueError(f"'{ten_hien_thi}': phải là số hữu hạn.")
        return gia_tri

    def _doc_du_lieu_dau_vao(self):
        chieu_dai = self._lay_so_thuc("chieu_dai", "Chiều dài khoang")
        chieu_rong = self._lay_so_thuc("chieu_rong", "Chiều rộng khoang")

        if chieu_dai <= 0 or chieu_rong <= 0:
            raise ValueError("Chiều dài và Chiều rộng khoang chứa xà lan phải lớn hơn 0.")

        loai_day = self.bien_loai_day.get()
        if loai_day == "Đáy bằng":
            sau_day = self._lay_so_thuc("sau_day", "Chiều sâu khoang xà lan")
            if sau_day <= 0:
                raise ValueError("Chiều sâu khoang xà lan phải lớn hơn 0.")
            thong_so_day = {"sau_day": sau_day}
        else:
            sau_man = self._lay_so_thuc("sau_man", "Chiều sâu đáy tại 2 bên mạn")
            canh_nghieng_V = self._lay_so_thuc("canh_nghieng_V", "Chiều dài 1 cạnh nghiêng chữ V")
            
            if sau_man <= 0 or canh_nghieng_V <= 0:
                raise ValueError("Chiều sâu tại mạn và Chiều dài cạnh nghiêng chữ V phải lớn hơn 0.")
            
            nua_rong = chieu_rong / 2.0
            if canh_nghieng_V < nua_rong:
                raise ValueError(
                    f"Chiều dài cạnh nghiêng chữ V ({canh_nghieng_V}m) không hợp lệ.\n"
                    f"Cạnh nghiêng phải lớn hơn hoặc bằng nửa chiều rộng xà lan (B/2 = {nua_rong:.2f}m)."
                )
            
            thong_so_day = {"sau_man": sau_man, "canh_nghieng_V": canh_nghieng_V}

        loai_mat = int(self.bien_loai_mat.get()[0])

        if loai_mat == 1:
            do_hut_cat = self._lay_so_thuc("do_hut_cat", "Độ hụt mặt cát")
            thong_so_mat = {"do_hut_cat": do_hut_cat}

        elif loai_mat == 2:
            do_hut_dau = self._lay_so_thuc("do_hut_dau", "Độ hụt tại đầu tàu")
            do_hut_duoi = self._lay_so_thuc("do_hut_duoi", "Độ hụt tại đuôi tàu")
            thong_so_mat = {"do_hut_dau": do_hut_dau, "do_hut_duoi": do_hut_duoi}

        elif loai_mat == 3:
            do_hut_nen = self._lay_so_thuc("do_hut_nen", "Độ hụt lớp cát nền")
            cao_non = self._lay_so_thuc("cao_non", "Chiều cao đống nón")
            dai_chan_non = self._lay_so_thuc("dai_chan_non", "Chiều dài chân đống nón")
            rong_chan_non = self._lay_so_thuc("rong_chan_non", "Chiều rộng chân đống nón")

            if cao_non < 0 or dai_chan_non <= 0 or rong_chan_non <= 0:
                raise ValueError("Chiều cao đống nón phải >= 0 và các kích thước chân nón phải > 0.")

            if dai_chan_non > chieu_dai:
                raise ValueError(f"Chiều dài chân đống nón ({dai_chan_non}m) lớn hơn chiều dài khoang ({chieu_dai}m).")
            if rong_chan_non > chieu_rong:
                raise ValueError(f"Chiều rộng chân đống nón ({rong_chan_non}m) lớn hơn chiều rộng khoang ({chieu_rong}m).")

            thong_so_mat = {
                "do_hut_nen": do_hut_nen,
                "cao_non": cao_non,
                "dai_chan_non": dai_chan_non,
                "rong_chan_non": rong_chan_non
            }

        elif loai_mat == 4:
            do_hut_nen = self._lay_so_thuc("do_hut_nen", "Độ hụt lớp cát nền")
            cao_num = self._lay_so_thuc("cao_num", "Chiều cao đỉnh núm cát")
            dai_chan_num = self._lay_so_thuc("dai_chan_num", "Chiều dài chân đụn cát")
            rong_chan_num = self._lay_so_thuc("rong_chan_num", "Chiều rộng chân đụn cát")

            if cao_num < 0 or dai_chan_num <= 0 or rong_chan_num <= 0:
                raise ValueError("Chiều cao đỉnh núm phải >= 0 và các kích thước chân đụn cát phải > 0.")

            if dai_chan_num > chieu_dai:
                raise ValueError(f"Chiều dài chân đụn cát ({dai_chan_num}m) vượt quá chiều dài khoang ({chieu_dai}m).")
            if rong_chan_num > chieu_rong:
                raise ValueError(f"Chiều rộng chân đụn cát ({rong_chan_num}m) vượt quá chiều rộng khoang ({chieu_rong}m).")

            thong_so_mat = {
                "do_hut_nen": do_hut_nen,
                "cao_num": cao_num,
                "dai_chan_num": dai_chan_num,
                "rong_chan_num": rong_chan_num,
            }

        else:
            raise ValueError("Dạng bề mặt cát không hợp lệ.")

        khoi_luong_rieng = self._lay_so_thuc("khoi_luong_rieng", "Khối lượng riêng của cát")
        if khoi_luong_rieng <= 0:
            raise ValueError("Khối lượng riêng của cát phải lớn hơn 0.")

        return chieu_dai, chieu_rong, loai_day, thong_so_day, loai_mat, thong_so_mat, khoi_luong_rieng

    def thuc_hien_tinh_toan(self):
        try:
            (
                chieu_dai,
                chieu_rong,
                loai_day,
                thong_so_day,
                loai_mat,
                thong_so_mat,
                khoi_luong_rieng,
            ) = self._doc_du_lieu_dau_vao()

            mo_hinh = MoHinhTheTichCat(
                chieu_dai=chieu_dai,
                chieu_rong=chieu_rong,
                loai_day=loai_day,
                thong_so_day=thong_so_day,
                loai_mat=loai_mat,
                thong_so_mat=thong_so_mat,
            )

            the_tich = mo_hinh.tinh_the_tich(so_bac=120)
            khoi_luong = the_tich * khoi_luong_rieng

            self.o_ket_qua.delete("1.0", tk.END)

            self.o_ket_qua.insert(
                tk.END,
                "=======================================================================\n"
                "               BÁO CÁO KẾT QUẢ TÍNH THỂ TÍCH & KHỐI LƯỢNG CÁT          \n"
                "=======================================================================\n\n"
            )

            thong_tin_day = loai_day
            if loai_day == "Đáy chữ V":
                nua_rong = chieu_rong / 2.0
                do_ha_sau_V = math.sqrt(max(thong_so_day["canh_nghieng_V"]**2 - nua_rong**2, 0.0))
                sau_tim = thong_so_day["sau_man"] + do_ha_sau_V
                thong_tin_day = f"Đáy chữ V (Sâu mạn = {thong_so_day['sau_man']:.2f}m, Cạnh V = {thong_so_day['canh_nghieng_V']:.2f}m -> Sâu tim = {sau_tim:.2f}m)"

            self.o_ket_qua.insert(
                tk.END,
                f"1. KÍCH THƯỚC KHOANG CHỨA : Chiều dài = {chieu_dai:.2f} m  |  Chiều rộng = {chieu_rong:.2f} m\n"
                f"2. LOẠI ĐÁY XÀ LAN        : {thong_tin_day}\n"
                f"3. DẠNG BỀ MẶT CÁT        : {self.bien_loai_mat.get()}\n"
                f"4. KHỐI LƯỢNG RIÊNG CÁT   : {khoi_luong_rieng:.3f} tấn/m³\n"
                "-----------------------------------------------------------------------\n"
            )

            self.o_ket_qua.insert(
                tk.END,
                f"▶▶ TỔNG THỂ TÍCH CÁT (V)  : {the_tich:,.3f} mét khối (m³)\n"
                f"▶▶ TỔNG KHỐI LƯỢNG CÁT (M): {khoi_luong:,.3f} tấn\n"
                "-----------------------------------------------------------------------\n"
            )

        except Exception as loi:
            messagebox.showerror("Thông báo kiểm tra nhập liệu", str(loi))

    def xoa_ket_qua(self):
        self.o_ket_qua.delete("1.0", tk.END)
        self.o_ket_qua.insert(
            tk.END,
            "💡 Hướng dẫn: Xem sơ đồ 3D - Mặt cắt - Mặt bằng bên phải, nhập các số đo tương ứng rồi bấm nút '▶ TÍNH THỂ TÍCH & KHỐI LƯỢNG'.\n"
        )


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    UngDungTinhTheTich(root)
    root.mainloop()


if __name__ == "__main__":
    main()
