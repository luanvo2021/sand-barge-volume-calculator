import math
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

KHOI_LUONG_RIENG_MAC_DINH = 1.65

class LayerGeometry:
    def __init__(self, name, layer_type, params):
        self.name = name
        self.layer_type = layer_type
        self.params = params

class MultiTierBargeModel:
    def __init__(self, layers, loai_mat, thong_so_mat):
        self.layers = layers
        self.loai_mat = loai_mat
        self.thong_so_mat = thong_so_mat
        self._build_vertical_coordinates()

    def _build_vertical_coordinates(self):
        z_curr = 0.0
        self.layer_z_ranges = []
        for lay in self.layers:
            h = lay.params.get("H", 0.6)
            z_next = z_curr + h
            self.layer_z_ranges.append((z_curr, z_next, h))
            z_curr = z_next
        self.total_height = z_curr

    def do_sau_mat_cat(self, x, y, L_ref):
        p = self.thong_so_mat
        if self.loai_mat == 1:
            return p["do_hut_cat"]
        elif self.loai_mat == 2:
            return p["do_hut_dau"] + (p["do_hut_duoi"] - p["do_hut_dau"]) * (x / L_ref)
        elif self.loai_mat == 3:
            tam_x = L_ref / 2.0
            a = p["dai_chan_non"] / 2.0
            b = p["rong_chan_non"] / 2.0
            r = math.sqrt(((x - tam_x)/a)**2 + (y/b)**2)
            cao = p["cao_non"] * (1.0 - r) if r <= 1.0 else 0.0
            return p["do_hut_nen"] - cao
        elif self.loai_mat == 4:
            tam_x = L_ref / 2.0
            a = p["dai_chan_num"] / 2.0
            b = p["rong_chan_num"] / 2.0
            r_sq = ((x - tam_x)/a)**2 + (y/b)**2
            cao = p["cao_num"] * max(1.0 - r_sq, 0.0)
            return p["do_hut_nen"] - cao
        return 0.0

    def tinh_the_tich_tang(self, layer_idx, n=48):
        lay = self.layers[layer_idx]
        z_start, z_end, H_layer = self.layer_z_ranges[layer_idx]
        L = lay.params.get("L", 60.0)
        z_total = self.total_height
        
        pts, wts = np.polynomial.legendre.leggauss(n)
        x_subdomains = [(0.0, 0.5 * L), (0.5 * L, L)]
        
        if lay.name == "Phần 1":
            if lay.layer_type == "Đáy bằng":
                B = lay.params.get("B", 12.0)
                y_subdomains = [(-0.5 * B, 0.0), (0.0, 0.5 * B)]
                vol = 0.0
                for xs, xe in x_subdomains:
                    x_mid, x_half = 0.5*(xs+xe), 0.5*(xe-xs)
                    for ys, ye in y_subdomains:
                        y_mid, y_half = 0.5*(ys+ye), 0.5*(ye-ys)
                        for i in range(n):
                            xi = x_mid + x_half * pts[i]
                            wi = x_half * wts[i]
                            for j in range(n):
                                yj = y_mid + y_half * pts[j]
                                wj = y_half * wts[j]
                                D_mat_xy = self.do_sau_mat_cat(xi, yj, L)
                                Z_sand = z_total - D_mat_xy
                                h_in_layer = max(min(Z_sand - z_start, H_layer), 0.0)
                                vol += wi * wj * h_in_layer
                return vol

            elif lay.layer_type == "Đáy chữ V":
                B = lay.params.get("B", 12.0)
                y_subdomains = [(-0.5 * B, 0.0), (0.0, 0.5 * B)]
                vol = 0.0
                for xs, xe in x_subdomains:
                    x_mid, x_half = 0.5*(xs+xe), 0.5*(xe-xs)
                    for ys, ye in y_subdomains:
                        y_mid, y_half = 0.5*(ys+ye), 0.5*(ye-ys)
                        for i in range(n):
                            xi = x_mid + x_half * pts[i]
                            wi = x_half * wts[i]
                            for j in range(n):
                                yj = y_mid + y_half * pts[j]
                                wj = y_half * wts[j]
                                D_mat_xy = self.do_sau_mat_cat(xi, yj, L)
                                Z_sand = z_total - D_mat_xy
                                Z_floor = z_start + H_layer * (2.0 * abs(yj) / B)
                                h_in_layer = max(min(Z_sand - Z_floor, z_end - Z_floor), 0.0)
                                vol += wi * wj * h_in_layer
                return vol

            elif lay.layer_type == "Đáy hộp hình thang":
                B_top = lay.params.get("B_top", 12.0)
                B_bot = lay.params.get("B_bot", 7.5)
                y_subdomains = [
                    (-0.5 * B_top, -0.5 * B_bot),
                    (-0.5 * B_bot, 0.0),
                    (0.0, 0.5 * B_bot),
                    (0.5 * B_bot, 0.5 * B_top)
                ]
                vol = 0.0
                for xs, xe in x_subdomains:
                    x_mid, x_half = 0.5*(xs+xe), 0.5*(xe-xs)
                    for ys, ye in y_subdomains:
                        y_mid, y_half = 0.5*(ys+ye), 0.5*(ye-ys)
                        for i in range(n):
                            xi = x_mid + x_half * pts[i]
                            wi = x_half * wts[i]
                            for j in range(n):
                                yj = y_mid + y_half * pts[j]
                                wj = y_half * wts[j]
                                D_mat_xy = self.do_sau_mat_cat(xi, yj, L)
                                Z_sand = z_total - D_mat_xy
                                abs_y = abs(yj)
                                if abs_y <= 0.5 * B_bot:
                                    Z_floor = z_start
                                else:
                                    ty = (abs_y - 0.5 * B_bot) / max(0.5 * B_top - 0.5 * B_bot, 1e-6)
                                    Z_floor = z_start + H_layer * ty
                                h_in_layer = max(min(Z_sand - Z_floor, z_end - Z_floor), 0.0)
                                vol += wi * wj * h_in_layer
                return vol

        if lay.layer_type == "Hình hộp chữ nhật":
            B = lay.params.get("B", 12.0)
            y_subdomains = [(-0.5 * B, 0.0), (0.0, 0.5 * B)]
            vol = 0.0
            for xs, xe in x_subdomains:
                x_mid, x_half = 0.5*(xs+xe), 0.5*(xe-xs)
                for ys, ye in y_subdomains:
                    y_mid, y_half = 0.5*(ys+ye), 0.5*(ye-ys)
                    for i in range(n):
                        xi = x_mid + x_half * pts[i]
                        wi = x_half * wts[i]
                        for j in range(n):
                            yj = y_mid + y_half * pts[j]
                            wj = y_half * wts[j]
                            D_mat_xy = self.do_sau_mat_cat(xi, yj, L)
                            Z_sand = z_total - D_mat_xy
                            h_in_layer = max(min(Z_sand - z_start, H_layer), 0.0)
                            vol += wi * wj * h_in_layer
            return vol

        elif lay.layer_type == "Hình hộp thang":
            B_top = lay.params.get("B_top", 13.8)
            B_bot = lay.params.get("B_bot", 12.0)
            B_max = max(B_top, B_bot)
            B_min = min(B_top, B_bot)
            y_subdomains = [
                (-0.5 * B_max, -0.5 * B_min),
                (-0.5 * B_min, 0.0),
                (0.0, 0.5 * B_min),
                (0.5 * B_min, 0.5 * B_max)
            ]
            vol = 0.0
            for xs, xe in x_subdomains:
                x_mid, x_half = 0.5*(xs+xe), 0.5*(xe-xs)
                for ys, ye in y_subdomains:
                    if abs(ye - ys) < 1e-6:
                        continue
                    y_mid, y_half = 0.5*(ys+ye), 0.5*(ye-ys)
                    for i in range(n):
                        xi = x_mid + x_half * pts[i]
                        wi = x_half * wts[i]
                        for j in range(n):
                            yj = y_mid + y_half * pts[j]
                            wj = y_half * wts[j]
                            D_mat_xy = self.do_sau_mat_cat(xi, yj, L)
                            Z_sand = z_total - D_mat_xy
                            abs_y = abs(yj)
                            
                            if B_top >= B_bot:
                                if abs_y <= 0.5 * B_bot:
                                    Z_floor = z_start
                                else:
                                    ty = (abs_y - 0.5 * B_bot) / max(0.5 * B_top - 0.5 * B_bot, 1e-6)
                                    Z_floor = z_start + H_layer * ty
                                Z_ceil = z_end
                            else:
                                Z_floor = z_start
                                if abs_y <= 0.5 * B_top:
                                    Z_ceil = z_end
                                else:
                                    ty = (abs_y - 0.5 * B_top) / max(0.5 * B_bot - 0.5 * B_top, 1e-6)
                                    Z_ceil = z_start + H_layer * (1.0 - ty)
                            
                            h_in_layer = max(min(Z_sand - Z_floor, Z_ceil - Z_floor), 0.0)
                            vol += wi * wj * h_in_layer
            return vol

        return 0.0

    def tinh_tong_the_tich(self):
        total_vol = 0.0
        for i in range(len(self.layers)):
            total_vol += self.tinh_the_tich_tang(i)
        return total_vol


class UngDungV2:
    def __init__(self, root):
        self.root = root
        self.root.title("TÍNH THỂ TÍCH CÁT XÀ LAN V2 - 2 TAB KHỔ LỚN CHUYÊN BIỆT")
        self.root.geometry("1480x940")
        self.root.minsize(1300, 860)

        self.o_nhap_lieu = {}
        self.pan_start = None
        self.custom_trans_limits = None

        self._tao_giao_dien()
        self._setup_mouse_events()
        self._cap_nhat_toan_bo()

    def tao_o_nhap(self, parent, r, ma_khoa, ten_nhan, val_def, don_vi="m", note=""):
        ttk.Label(parent, text=ten_nhan, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="w", padx=4, pady=2)
        frame_val = ttk.Frame(parent)
        frame_val.grid(row=r, column=1, sticky="w", padx=4, pady=2)

        entry = ttk.Entry(frame_val, width=10, font=("Segoe UI", 9))
        entry.insert(0, str(val_def))
        entry.pack(side="left")
        ttk.Label(frame_val, text=f" {don_vi}", font=("Segoe UI", 9)).pack(side="left")

        if note:
            ttk.Label(parent, text=note, font=("Segoe UI", 8, "italic"), foreground="#666").grid(row=r, column=2, sticky="w", padx=4, pady=2)

        self.o_nhap_lieu[ma_khoa] = entry
        return entry

    def _tao_giao_dien(self):
        khung_tong = ttk.Frame(self.root)
        khung_tong.pack(fill="both", expand=True, padx=6, pady=6)

        cot_trai = ttk.Frame(khung_tong, width=480)
        cot_trai.pack(side="left", fill="both", expand=False, padx=(0, 6))

        canvas_scroll = tk.Canvas(cot_trai, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(cot_trai, orient="vertical", command=canvas_scroll.yview)
        self.scrollable_frame = ttk.Frame(canvas_scroll)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. PHẦN 1: ĐÁY SÀN
        self.khung_p1 = ttk.LabelFrame(self.scrollable_frame, text="1. PHẦN 1: ĐÁY SÀN (TẦNG 1)")
        self.khung_p1.pack(fill="x", pady=3, padx=2)

        ttk.Label(self.khung_p1, text="Dạng đáy sàn:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_p1 = tk.StringVar(value="Đáy hộp hình thang")
        cb_p1 = ttk.Combobox(self.khung_p1, textvariable=self.var_p1, values=["Đáy hộp hình thang", "Đáy bằng", "Đáy chữ V"], state="readonly", width=18)
        cb_p1.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        cb_p1.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_toan_bo(reset_zoom=True))
        self.frame_p1_dyn = ttk.Frame(self.khung_p1)
        self.frame_p1_dyn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 2. PHẦN 2: THÂN CHÍNH
        self.khung_p2 = ttk.LabelFrame(self.scrollable_frame, text="2. PHẦN 2: THÂN CHÍNH (TẦNG 2)")
        self.khung_p2.pack(fill="x", pady=3, padx=2)

        ttk.Label(self.khung_p2, text="Dạng thân chính:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_p2 = tk.StringVar(value="Hình hộp thang")
        cb_p2 = ttk.Combobox(self.khung_p2, textvariable=self.var_p2, values=["Hình hộp thang", "Hình hộp chữ nhật"], state="readonly", width=18)
        cb_p2.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        cb_p2.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_toan_bo(reset_zoom=True))
        self.frame_p2_dyn = ttk.Frame(self.khung_p2)
        self.frame_p2_dyn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 3. PHẦN 3: CỔ KHOANG
        self.khung_p3 = ttk.LabelFrame(self.scrollable_frame, text="3. PHẦN 3: TẦNG PHỤ 1 (CỔ KHOANG / THÀNH BE)")
        self.khung_p3.pack(fill="x", pady=3, padx=2)

        ttk.Label(self.khung_p3, text="Chọn tầng phụ 1:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_p3 = tk.StringVar(value="Không có phần 3")
        cb_p3 = ttk.Combobox(self.khung_p3, textvariable=self.var_p3, values=["Không có phần 3", "Hình hộp chữ nhật", "Hình hộp thang"], state="readonly", width=18)
        cb_p3.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        cb_p3.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_toan_bo(reset_zoom=True))
        self.frame_p3_dyn = ttk.Frame(self.khung_p3)
        self.frame_p3_dyn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 4. PHẦN 4
        self.khung_p4 = ttk.LabelFrame(self.scrollable_frame, text="4. PHẦN 4: TẦNG PHỤ 2 (NẰM TRÊN PHẦN 3)")
        self.khung_p4.pack(fill="x", pady=3, padx=2)

        ttk.Label(self.khung_p4, text="Chọn tầng phụ 2:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_p4 = tk.StringVar(value="Không có phần 4")
        cb_p4 = ttk.Combobox(self.khung_p4, textvariable=self.var_p4, values=["Không có phần 4", "Hình hộp chữ nhật", "Hình hộp thang"], state="readonly", width=18)
        cb_p4.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        cb_p4.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_toan_bo(reset_zoom=True))
        self.frame_p4_dyn = ttk.Frame(self.khung_p4)
        self.frame_p4_dyn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 5. DẠNG MẶT CÁT
        khung_mat = ttk.LabelFrame(self.scrollable_frame, text="5. DẠNG PHÂN BỐ BỀ MẶT CÁT")
        khung_mat.pack(fill="x", pady=3, padx=2)

        ttk.Label(khung_mat, text="Kiểu mặt cát:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_mat = tk.StringVar(value="1 - Mặt phẳng (Dàn trải đều)")
        cb_mat = ttk.Combobox(khung_mat, textvariable=self.var_mat, values=[
            "1 - Mặt phẳng (Dàn trải đều)",
            "2 - Dốc nghiêng trải dài từ Đầu đến Đuôi",
            "3 - Nền phẳng + Đỉnh hình nón (Mặt cắt tam giác)",
            "4 - Nền phẳng + Đỉnh vòm núm cong mượt (Nipple)"
        ], state="readonly", width=36)
        cb_mat.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        cb_mat.bind("<<ComboboxSelected>>", lambda e: self._cap_nhat_toan_bo())
        self.frame_mat_dyn = ttk.Frame(khung_mat)
        self.frame_mat_dyn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=2)

        # 6. KHỐI LƯỢNG RIÊNG & NÚT
        khung_act = ttk.Frame(self.scrollable_frame)
        khung_act.pack(fill="x", pady=4, padx=2)
        self.tao_o_nhap(khung_act, 0, "rho", "Khối lượng riêng cát:", KHOI_LUONG_RIENG_MAC_DINH, "tấn/m³")

        btn_box = ttk.Frame(khung_act)
        btn_box.grid(row=1, column=0, columnspan=3, sticky="w", pady=4)
        ttk.Button(btn_box, text="▶ TÍNH THỂ TÍCH & KHỐI LƯỢNG", command=self.thuc_hien_tinh).pack(side="left", padx=2, ipadx=8, ipady=3)
        ttk.Button(btn_box, text="Làm mới", command=self.reset_form).pack(side="left", padx=4)
        ttk.Button(btn_box, text="⟲ Reset Zoom 2D", command=self.reset_zoom_2d).pack(side="left", padx=4)

        # BÁO CÁO KẾT QUẢ
        khung_kq = ttk.LabelFrame(self.scrollable_frame, text="BÁO CÁO KẾT QUẢ")
        khung_kq.pack(fill="x", pady=4, padx=2)
        self.txt_kq = tk.Text(khung_kq, height=7, width=50, font=("Consolas", 9), bg="#fcfcfc")
        self.txt_kq.pack(fill="both", expand=True, padx=4, pady=4)

        # CỘT PHẢI: KHUNG ĐỒ HỌA 2 TAB KHỔ LỚN
        cot_phai = ttk.Frame(khung_tong)
        cot_phai.pack(side="right", fill="both", expand=True, padx=(4, 0))

        # Thanh nút chuyển đổi 2 Tab
        bar_toggle = ttk.Frame(cot_phai)
        bar_toggle.pack(fill="x", pady=(0, 4))
        
        ttk.Label(bar_toggle, text="CHẾ ĐỘ XEM:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(2, 6))
        ttk.Button(bar_toggle, text="📐 1. XEM 2D MẶT CẮT KHỔ LỚN (ZOOM & PAN)", command=lambda: self.notebook.select(0)).pack(side="left", padx=3)
        ttk.Button(bar_toggle, text="🌐 2. XEM 3D TOÀN MÀN HÌNH (XOAY 360°)", command=lambda: self.notebook.select(1)).pack(side="left", padx=3)

        self.notebook = ttk.Notebook(cot_phai)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: 2D KHỔ LỚN
        self.tab_2d = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2d, text="   📐 TAB 1: BẢN VẼ 2D KHỔ LỚN (LĂN CHUỘT ZOOM & PAN)   ")
        self.fig_2d = plt.figure(figsize=(9.2, 8.5), dpi=105, facecolor='#ffffff')
        self.canvas_2d = FigureCanvasTkAgg(self.fig_2d, master=self.tab_2d)
        self.canvas_2d.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)

        # Tab 2: 3D TOÀN MÀN HÌNH
        self.tab_3d = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3d, text="   🌐 TAB 2: MÔ HÌNH 3D TOÀN MÀN HÌNH (XOAY 360°)   ")
        self.fig_3d = plt.figure(figsize=(9.2, 8.5), dpi=105, facecolor='#ffffff')
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, master=self.tab_3d)
        self.canvas_3d.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)

    def _setup_mouse_events(self):
        self.canvas_2d.mpl_connect('scroll_event', self._on_scroll)
        self.canvas_2d.mpl_connect('button_press_event', self._on_press)
        self.canvas_2d.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas_2d.mpl_connect('button_release_event', self._on_release)

    def reset_zoom_2d(self):
        self.custom_trans_limits = None
        self._ve_do_hoa()

    def _on_scroll(self, event):
        if hasattr(self, 'ax_trans') and event.inaxes == self.ax_trans:
            cur_xlim = self.ax_trans.get_xlim()
            cur_ylim = self.ax_trans.get_ylim()
            
            xdata = event.xdata if event.xdata is not None else (cur_xlim[0] + cur_xlim[1]) / 2.0
            ydata = event.ydata if event.ydata is not None else (cur_ylim[0] + cur_ylim[1]) / 2.0

            scale_factor = 1.0 / 1.25 if event.button == 'up' else 1.25
            
            cur_w = cur_xlim[1] - cur_xlim[0]
            new_width = cur_w * scale_factor
            
            if new_width < 2.0 or new_width > 55.0:
                return

            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            rel_x = (cur_xlim[1] - xdata) / cur_w
            rel_y = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - rel_x), xdata + new_width * rel_x]
            new_ylim = [ydata - new_height * (1 - rel_y), ydata + new_height * rel_y]

            self.custom_trans_limits = (new_xlim, new_ylim)
            self.ax_trans.set_xlim(new_xlim)
            self.ax_trans.set_ylim(new_ylim)
            self.canvas_2d.draw_idle()

    def _on_press(self, event):
        if hasattr(self, 'ax_trans') and event.inaxes == self.ax_trans:
            if event.dblclick:
                self.reset_zoom_2d()
                return
            if event.button in [1, 2, 3]:
                self.pan_start = (event.xdata, event.ydata)

    def _on_motion(self, event):
        if self.pan_start is not None and hasattr(self, 'ax_trans') and event.inaxes == self.ax_trans:
            if event.xdata is not None and event.ydata is not None:
                dx = event.xdata - self.pan_start[0]
                dy = event.ydata - self.pan_start[1]
                
                cur_xlim = self.ax_trans.get_xlim()
                cur_ylim = self.ax_trans.get_ylim()

                new_xlim = [cur_xlim[0] - dx, cur_xlim[1] - dx]
                new_ylim = [cur_ylim[0] - dy, cur_ylim[1] - dy]

                self.custom_trans_limits = (new_xlim, new_ylim)
                self.ax_trans.set_xlim(new_xlim)
                self.ax_trans.set_ylim(new_ylim)
                self.canvas_2d.draw_idle()

    def _on_release(self, event):
        self.pan_start = None

    def _cap_nhat_toan_bo(self, reset_zoom=False):
        if reset_zoom:
            self.custom_trans_limits = None
        self._build_dyn_p1()
        self._build_dyn_p2()
        self._build_dyn_p3()
        self._build_dyn_p4()
        self._build_dyn_mat()
        self._ve_do_hoa()

    def _build_dyn_p1(self):
        for w in self.frame_p1_dyn.winfo_children(): w.destroy()
        t = self.var_p1.get()
        self.tao_o_nhap(self.frame_p1_dyn, 0, "p1_L", "Chiều dài lòng khoang L:", 60.0, "m")
        if t == "Đáy bằng":
            self.tao_o_nhap(self.frame_p1_dyn, 1, "p1_B", "Chiều rộng sàn phẳng B1:", 12.0, "m")
            self.tao_o_nhap(self.frame_p1_dyn, 2, "p1_H", "Chiều cao tầng đáy H1:", 0.6, "m")
        elif t == "Đáy chữ V":
            self.tao_o_nhap(self.frame_p1_dyn, 1, "p1_B", "Chiều rộng miệng mạn B1:", 12.0, "m")
            self.tao_o_nhap(self.frame_p1_dyn, 2, "p1_C", "Cạnh nghiêng chữ V C1:", 6.03, "m", "(Pytago tính H1)")
        elif t == "Đáy hộp hình thang":
            self.tao_o_nhap(self.frame_p1_dyn, 1, "p1_B_top", "Chiều rộng Đáy trên B1_top:", 12.0, "m")
            self.tao_o_nhap(self.frame_p1_dyn, 2, "p1_B_bot", "Chiều rộng Đáy dưới B1_bot:", 7.5, "m")
            self.tao_o_nhap(self.frame_p1_dyn, 3, "p1_H", "Chiều cao vát đáy H1:", 0.6, "m")

    def _build_dyn_p2(self):
        for w in self.frame_p2_dyn.winfo_children(): w.destroy()
        t = self.var_p2.get()
        self.tao_o_nhap(self.frame_p2_dyn, 0, "p2_L", "Chiều dài mạn P2:", 60.0, "m")
        if t == "Hình hộp chữ nhật":
            self.tao_o_nhap(self.frame_p2_dyn, 1, "p2_B", "Chiều rộng thân chính B2:", 12.0, "m")
            self.tao_o_nhap(self.frame_p2_dyn, 2, "p2_H", "Chiều cao thân chính H2:", 2.2, "m")
        elif t == "Hình hộp thang":
            self.tao_o_nhap(self.frame_p2_dyn, 1, "p2_B_top", "Chiều rộng Đáy trên B2_top:", 13.8, "m")
            self.tao_o_nhap(self.frame_p2_dyn, 2, "p2_B_bot", "Chiều rộng Đáy dưới B2_bot:", 12.0, "m")
            self.tao_o_nhap(self.frame_p2_dyn, 3, "p2_H", "Chiều cao thân chính H2:", 2.2, "m")

    def _build_dyn_p3(self):
        for w in self.frame_p3_dyn.winfo_children(): w.destroy()
        t = self.var_p3.get()
        if t == "Không có phần 3":
            ttk.Label(self.frame_p3_dyn, text="(Đã tắt phần 3)", font=("Segoe UI", 8, "italic"), foreground="#888").pack(anchor="w")
            return
        self.tao_o_nhap(self.frame_p3_dyn, 0, "p3_L", "Chiều dài mạn P3:", 60.0, "m")
        if t == "Hình hộp chữ nhật":
            self.tao_o_nhap(self.frame_p3_dyn, 1, "p3_B", "Chiều rộng cổ khoang B3:", 10.5, "m", "(Thụt vào trong)")
            self.tao_o_nhap(self.frame_p3_dyn, 2, "p3_H", "Chiều cao cổ khoang H3:", 0.8, "m")
        elif t == "Hình hộp thang":
            self.tao_o_nhap(self.frame_p3_dyn, 1, "p3_B_top", "Chiều rộng Đáy trên B3_top:", 11.5, "m")
            self.tao_o_nhap(self.frame_p3_dyn, 2, "p3_B_bot", "Chiều rộng Đáy dưới B3_bot:", 10.5, "m")
            self.tao_o_nhap(self.frame_p3_dyn, 3, "p3_H", "Chiều cao phần 3 H3:", 0.8, "m")

    def _build_dyn_p4(self):
        for w in self.frame_p4_dyn.winfo_children(): w.destroy()
        t = self.var_p4.get()
        if t == "Không có phần 4":
            ttk.Label(self.frame_p4_dyn, text="(Đã tắt phần 4)", font=("Segoe UI", 8, "italic"), foreground="#888").pack(anchor="w")
            return
        self.tao_o_nhap(self.frame_p4_dyn, 0, "p4_L", "Chiều dài mạn P4:", 60.0, "m")
        if t == "Hình hộp chữ nhật":
            self.tao_o_nhap(self.frame_p4_dyn, 1, "p4_B", "Chiều rộng phần 4 B4:", 9.0, "m")
            self.tao_o_nhap(self.frame_p4_dyn, 2, "p4_H", "Chiều cao phần 4 H4:", 0.5, "m")
        elif t == "Hình hộp thang":
            self.tao_o_nhap(self.frame_p4_dyn, 1, "p4_B_top", "Chiều rộng Đáy trên B4_top:", 9.5, "m")
            self.tao_o_nhap(self.frame_p4_dyn, 2, "p4_B_bot", "Chiều rộng Đáy dưới B4_bot:", 9.0, "m")
            self.tao_o_nhap(self.frame_p4_dyn, 3, "p4_H", "Chiều cao phần 4 H4:", 0.5, "m")

    def _build_dyn_mat(self):
        for w in self.frame_mat_dyn.winfo_children(): w.destroy()
        lm = int(self.var_mat.get()[0])
        if lm == 1:
            self.tao_o_nhap(self.frame_mat_dyn, 0, "do_hut_cat", "Độ hụt mặt cát từ mép trên:", 0.8, "m")
        elif lm == 2:
            self.tao_o_nhap(self.frame_mat_dyn, 0, "do_hut_dau", "Độ hụt tại ĐẦU tàu:", 0.5, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 1, "do_hut_duoi", "Độ hụt tại ĐUÔI tàu:", 1.5, "m")
        elif lm == 3:
            self.tao_o_nhap(self.frame_mat_dyn, 0, "do_hut_nen", "1. Độ hụt cát nền:", 1.2, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 1, "cao_non", "2. Chiều cao đống nón:", 1.0, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 2, "dai_chan_non", "3. Dài chân nón (dọc):", 16.0, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 3, "rong_chan_non", "4. Rộng chân nón (ngang):", 8.0, "m")
        elif lm == 4:
            self.tao_o_nhap(self.frame_mat_dyn, 0, "do_hut_nen", "1. Độ hụt cát nền:", 1.2, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 1, "cao_num", "2. Cao đỉnh vòm núm:", 1.0, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 2, "dai_chan_num", "3. Dài chân đụn (dọc):", 24.0, "m")
            self.tao_o_nhap(self.frame_mat_dyn, 3, "rong_chan_num", "4. Rộng chân đụn (ngang):", 8.0, "m")

    def _lay_f(self, k, name=""):
        try:
            return float(self.o_nhap_lieu[k].get().strip())
        except Exception:
            raise ValueError(f"Giá trị '{name}' không đúng định dạng số.")

    def _doc_layers(self):
        layers = []
        t1 = self.var_p1.get()
        L1 = self._lay_f("p1_L", "Chiều dài P1")
        if t1 == "Đáy bằng":
            layers.append(LayerGeometry("Phần 1", t1, {"L": L1, "B": self._lay_f("p1_B", "Rộng P1"), "H": self._lay_f("p1_H", "Chiều cao P1")}))
        elif t1 == "Đáy chữ V":
            B1 = self._lay_f("p1_B", "Rộng miệng mạn P1")
            C1 = self._lay_f("p1_C", "Cạnh nghiêng chữ V P1")
            halfB = B1 / 2.0
            if C1 <= halfB:
                raise ValueError(f"Cạnh nghiêng chữ V C1 ({C1}m) phải lớn hơn nửa chiều rộng mạn B1/2 ({halfB}m) để tạo thành tam giác.")
            H1 = math.sqrt(C1**2 - halfB**2)
            layers.append(LayerGeometry("Phần 1", t1, {"L": L1, "B": B1, "C": C1, "H": H1}))
        elif t1 == "Đáy hộp hình thang":
            layers.append(LayerGeometry("Phần 1", t1, {
                "L": L1, "B_top": self._lay_f("p1_B_top", "Đáy trên P1"),
                "B_bot": self._lay_f("p1_B_bot", "Đáy dưới P1"), "H": self._lay_f("p1_H", "Chiều cao P1")
            }))

        t2 = self.var_p2.get()
        L2 = self._lay_f("p2_L", "Chiều dài P2")
        if t2 == "Hình hộp chữ nhật":
            layers.append(LayerGeometry("Phần 2", t2, {"L": L2, "B": self._lay_f("p2_B", "Rộng P2"), "H": self._lay_f("p2_H", "Chiều cao P2")}))
        elif t2 == "Hình hộp thang":
            layers.append(LayerGeometry("Phần 2", t2, {
                "L": L2, "B_top": self._lay_f("p2_B_top", "Đáy trên P2"),
                "B_bot": self._lay_f("p2_B_bot", "Đáy dưới P2"), "H": self._lay_f("p2_H", "Chiều cao P2")
            }))

        t3 = self.var_p3.get()
        if t3 != "Không có phần 3":
            L3 = self._lay_f("p3_L", "Chiều dài P3")
            if t3 == "Hình hộp chữ nhật":
                layers.append(LayerGeometry("Phần 3", t3, {"L": L3, "B": self._lay_f("p3_B", "Rộng P3"), "H": self._lay_f("p3_H", "Chiều cao P3")}))
            elif t3 == "Hình hộp thang":
                layers.append(LayerGeometry("Phần 3", t3, {
                    "L": L3, "B_top": self._lay_f("p3_B_top", "Đáy trên P3"),
                    "B_bot": self._lay_f("p3_B_bot", "Đáy dưới P3"), "H": self._lay_f("p3_H", "Chiều cao P3")
                }))

        t4 = self.var_p4.get()
        if t4 != "Không có phần 4":
            L4 = self._lay_f("p4_L", "Chiều dài P4")
            if t4 == "Hình hộp chữ nhật":
                layers.append(LayerGeometry("Phần 4", t4, {"L": L4, "B": self._lay_f("p4_B", "Rộng P4"), "H": self._lay_f("p4_H", "Chiều cao P4")}))
            elif t4 == "Hình hộp thang":
                layers.append(LayerGeometry("Phần 4", t4, {
                    "L": L4, "B_top": self._lay_f("p4_B_top", "Đáy trên P4"),
                    "B_bot": self._lay_f("p4_B_bot", "Đáy dưới P4"), "H": self._lay_f("p4_H", "Chiều cao P4")
                }))

        return layers

    def _doc_mat(self):
        lm = int(self.var_mat.get()[0])
        if lm == 1:
            return lm, {"do_hut_cat": self._lay_f("do_hut_cat", "Độ hụt cát")}
        elif lm == 2:
            return lm, {"do_hut_dau": self._lay_f("do_hut_dau", "Độ hụt đầu"), "do_hut_duoi": self._lay_f("do_hut_duoi", "Độ hụt đuôi")}
        elif lm == 3:
            return lm, {
                "do_hut_nen": self._lay_f("do_hut_nen", "Độ hụt nền"), "cao_non": self._lay_f("cao_non", "Chiều cao nón"),
                "dai_chan_non": self._lay_f("dai_chan_non", "Dài chân nón"), "rong_chan_non": self._lay_f("rong_chan_non", "Rộng chân nón")
            }
        elif lm == 4:
            return lm, {
                "do_hut_nen": self._lay_f("do_hut_nen", "Độ hụt nền"), "cao_num": self._lay_f("cao_num", "Cao đỉnh núm"),
                "dai_chan_num": self._lay_f("dai_chan_num", "Dài chân đụn"), "rong_chan_num": self._lay_f("rong_chan_num", "Rộng chân đụn")
            }
        return 1, {}

    def _ve_do_hoa(self):
        try:
            layers = self._doc_layers()
            loai_mat, thong_so_mat = self._doc_mat()
            model = MultiTierBargeModel(layers, loai_mat, thong_so_mat)
        except Exception:
            return

        L_ref = layers[0].params.get("L", 60.0)
        z_total = model.total_height

        C_HULL_LINE = '#0f172a'
        C_LINE_RED = '#dc2626'
        C_DIVIDER = '#2563eb'
        C_DIM = '#0284c7'

        def dim_h(ax, x1, x2, z, text, offset_z=0.0, text_above=True, color=C_DIM):
            zl = z + offset_z
            ax.plot([x1, x1], [z, zl + (0.06 if offset_z>=0 else -0.06)], color=color, lw=0.7, linestyle=':', clip_on=True)
            ax.plot([x2, x2], [z, zl + (0.06 if offset_z>=0 else -0.06)], color=color, lw=0.7, linestyle=':', clip_on=True)
            ax.annotate('', xy=(x1, zl), xytext=(x2, zl),
                        arrowprops=dict(arrowstyle='<->', color=color, lw=1.1, shrinkA=0, shrinkB=0),
                        annotation_clip=True)
            tz = zl + (0.10 if text_above else -0.18)
            ax.text((x1 + x2)/2, tz, text, color=color, fontsize=8.5, fontweight='bold', ha='center', va='center',
                    bbox=dict(boxstyle='square,pad=0.12', facecolor='#ffffff', edgecolor='none', alpha=0.9),
                    clip_on=True)

        def dim_v(ax, z1, z2, x, text, offset_x=0.0, color=C_DIM):
            xl = x + offset_x
            ax.plot([x, xl + (0.15 if offset_x>=0 else -0.15)], [z1, z1], color=color, lw=0.7, linestyle=':', clip_on=True)
            ax.plot([x, xl + (0.15 if offset_x>=0 else -0.15)], [z2, z2], color=color, lw=0.7, linestyle=':', clip_on=True)
            ax.annotate('', xy=(xl, z1), xytext=(xl, z2),
                        arrowprops=dict(arrowstyle='<->', color=color, lw=1.1, shrinkA=0, shrinkB=0),
                        annotation_clip=True)
            tx = xl + (0.16 if offset_x>=0 else -0.16)
            ha = 'left' if offset_x>=0 else 'right'
            ax.text(tx, (z1 + z2)/2, text, color=color, fontsize=8.5, fontweight='bold', ha=ha, va='center',
                    bbox=dict(boxstyle='square,pad=0.12', facecolor='#ffffff', edgecolor='none', alpha=0.9),
                    clip_on=True)

        def dim_slanted(ax, x1, z1, x2, z2, text, offset=0.42, color=C_DIM):
            dx = x2 - x1
            dz = z2 - z1
            L = math.sqrt(dx**2 + dz**2)
            if L < 1e-6:
                return
            nx = dz / L
            nz = -dx / L
            p1_start = (x1, z1)
            p1_end = (x1 + offset * nx, z1 + offset * nz)
            p2_start = (x2, z2)
            p2_end = (x2 + offset * nx, z2 + offset * nz)
            ax.plot([p1_start[0], p1_end[0] + 0.08*nx], [p1_start[1], p1_end[1] + 0.08*nz], color=color, lw=0.7, linestyle=':', clip_on=True)
            ax.plot([p2_start[0], p2_end[0] + 0.08*nx], [p2_start[1], p2_end[1] + 0.08*nz], color=color, lw=0.7, linestyle=':', clip_on=True)
            ax.annotate('', xy=p1_end, xytext=p2_end,
                        arrowprops=dict(arrowstyle='<->', color=color, lw=1.2, shrinkA=0, shrinkB=0),
                        annotation_clip=True)
            mx = (p1_end[0] + p2_end[0]) / 2.0 + 0.12 * nx
            mz = (p1_end[1] + p2_end[1]) / 2.0 + 0.12 * nz
            angle = math.degrees(math.atan2(dz, dx))
            ax.text(mx, mz, text, color=color, fontsize=9.0, fontweight='bold', ha='center', va='center',
                    rotation=angle,
                    bbox=dict(boxstyle='square,pad=0.12', facecolor='#ffffff', edgecolor='none', alpha=0.9),
                    clip_on=True)

        def draw_2d_transverse(ax):
            prev_top_half = 0.0
            for idx, lay in enumerate(layers):
                zs, ze, h_lay = model.layer_z_ranges[idx]
                if idx == 0:
                    if lay.layer_type == "Đáy bằng":
                        halfB = lay.params.get("B", 12.0) / 2.0
                        ax.plot([-halfB, halfB], [zs, zs], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        ax.plot([-halfB, -halfB], [zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        ax.plot([halfB, halfB], [zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        prev_top_half = halfB
                        dim_h(ax, -halfB, halfB, zs, "B1", offset_z=-0.35, text_above=False)
                    elif lay.layer_type == "Đáy chữ V":
                        halfB = lay.params.get("B", 12.0) / 2.0
                        ax.plot([-halfB, 0, halfB], [ze, zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        prev_top_half = halfB
                        dim_h(ax, -halfB, halfB, ze, "B1", offset_z=0.0, text_above=True)
                        dim_slanted(ax, -halfB, ze, 0, zs, "C1", offset=0.45)
                    elif lay.layer_type == "Đáy hộp hình thang":
                        halfTop = lay.params.get("B_top", 12.0) / 2.0
                        halfBot = lay.params.get("B_bot", 7.5) / 2.0
                        ax.plot([-halfTop, -halfBot, halfBot, halfTop], [ze, zs, zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        prev_top_half = halfTop
                        dim_h(ax, -halfBot, halfBot, zs, "B1_bot", offset_z=-0.35, text_above=False)
                    
                    dim_v(ax, zs, ze, -prev_top_half, "H1", offset_x=-0.9)
                    if len(layers) > 1:
                        ax.plot([-prev_top_half, prev_top_half], [ze, ze], color=C_DIVIDER, lw=2.0, linestyle='-', clip_on=True)
                else:
                    if lay.layer_type == "Hình hộp chữ nhật":
                        halfB = lay.params.get("B", 12.0) / 2.0
                        if abs(halfB - prev_top_half) > 0.05:
                            ax.plot([-prev_top_half, -halfB], [zs, zs], color=C_HULL_LINE, lw=2.4, clip_on=True)
                            ax.plot([prev_top_half, halfB], [zs, zs], color=C_HULL_LINE, lw=2.4, clip_on=True)
                        ax.plot([-halfB, -halfB], [zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        ax.plot([halfB, halfB], [zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        prev_top_half = halfB
                        dim_h(ax, -halfB, halfB, zs, f"B{idx+1}", offset_z=0.0, text_above=True)
                    elif lay.layer_type == "Hình hộp thang":
                        halfTop = lay.params.get("B_top", 13.8) / 2.0
                        halfBot = lay.params.get("B_bot", 12.0) / 2.0
                        if abs(halfBot - prev_top_half) > 0.05:
                            ax.plot([-prev_top_half, -halfBot], [zs, zs], color=C_HULL_LINE, lw=2.4, clip_on=True)
                            ax.plot([prev_top_half, halfBot], [zs, zs], color=C_HULL_LINE, lw=2.4, clip_on=True)
                        ax.plot([-halfBot, -halfTop], [zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        ax.plot([halfBot, halfTop], [zs, ze], color=C_HULL_LINE, lw=2.8, clip_on=True)
                        prev_top_half = halfTop
                        dim_h(ax, -halfBot, halfBot, zs, f"B{idx+1}_bot", offset_z=0.0, text_above=True)

                    dim_v(ax, zs, ze, -prev_top_half, f"H{idx+1}", offset_x=-0.9)
                    if idx < len(layers) - 1:
                        ax.plot([-prev_top_half, prev_top_half], [ze, ze], color=C_DIVIDER, lw=2.0, linestyle='-', clip_on=True)

                ax.annotate(f" {lay.name}", xy=(prev_top_half, (zs+ze)/2), xytext=(prev_top_half + 2.0, (zs+ze)/2),
                            arrowprops=dict(arrowstyle="->", color=C_DIVIDER, lw=1.4),
                            fontsize=9.0, fontweight='bold', color=C_DIVIDER, va='center', annotation_clip=True)

            ax.plot([-prev_top_half, prev_top_half], [z_total, z_total], color=C_HULL_LINE, lw=2.8, clip_on=True)
            last_lay = layers[-1]
            if "B_top" in last_lay.params:
                dim_h(ax, -prev_top_half, prev_top_half, z_total, f"B{len(layers)}_top", offset_z=0.25, text_above=True)
            elif "B" in last_lay.params:
                dim_h(ax, -prev_top_half, prev_top_half, z_total, f"B{len(layers)}", offset_z=0.25, text_above=True)

            ax.axhline(z_total, color=C_LINE_RED, linestyle='--', lw=1.4, clip_on=True)
            ax.text(0, z_total + 0.42, "MỐC MÉP TRÊN (0.0m)", color=C_LINE_RED, fontsize=9.0, fontweight='bold', ha='center', clip_on=True)

            D_mat_mid = model.do_sau_mat_cat(L_ref/2, 0, L_ref)
            z_sand_mid = max(z_total - D_mat_mid, 0.0)
            ax.plot([-prev_top_half * 0.95, prev_top_half * 0.95], [z_sand_mid, z_sand_mid], color='#b45309', lw=2.0, clip_on=True)
            ax.text(0, z_sand_mid - 0.22, "MẶT CÁT", color='#78350f', fontsize=9.0, fontweight='bold', ha='center', clip_on=True)
            dim_v(ax, z_sand_mid, z_total, prev_top_half, "Độ hụt (D)", offset_x=0.85, color='#b45309')

            ax.set_title(f"1. MẶT CẮT NGANG KHỔ LỚN (LĂN CHUỘT ZOOM - KÉO ĐỂ PAN - DOUBLE CLICK RESET)", fontsize=10.5, fontweight='bold', color='#0b2545', pad=8)
            ax.set_aspect('equal')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#cbd5e1')
                spine.set_linewidth(1.4)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_facecolor('#f8fafc')

        def draw_2d_longitudinal(ax):
            ax.axhline(z_total, color=C_LINE_RED, linestyle='--', lw=1.2)
            ax.text(L_ref/2, z_total + 0.22, 'MÉP TRÊN THÀNH XÀ LAN (0.0m)', color=C_LINE_RED, fontsize=8.5, fontweight='bold', ha='center')
            for idx, lay in enumerate(layers):
                zs, ze, h_lay = model.layer_z_ranges[idx]
                ax.plot([0, L_ref], [zs, zs], color='#64748b', linestyle=':', lw=1.0)
                ax.plot([0, 0], [zs, ze], color='#334155', lw=2)
                ax.plot([L_ref, L_ref], [zs, ze], color='#334155', lw=2)
            x_line = np.linspace(0, L_ref, 100)
            z_sand_line = np.array([max(z_total - model.do_sau_mat_cat(xi, 0, L_ref), 0.0) for xi in x_line])
            ax.fill_between(x_line, 0, z_sand_line, color='#fef08a', alpha=0.85, edgecolor='#ca8a04', lw=1.2)
            ax.plot(x_line, z_sand_line, color='#ca8a04', lw=2.0)
            dim_h(ax, 0, L_ref, 0, "Chiều dài khoang (L)", offset_z=-0.45, text_above=False)
            dim_v(ax, z_sand_line[-1], z_total, L_ref, "Độ hụt (D)", offset_x=2.4, color='#b45309')
            ax.set_title(f"2. MẶT CẮT DỌC CHIỀU DÀI & ĐỘ HỤT CÁT", fontsize=10.0, fontweight='bold', color='#0b2545', pad=6)
            ax.set_xlim(-6, L_ref + 10)
            ax.set_ylim(-0.8, z_total + 0.8)
            ax.axis('off')

        def draw_3d_model(ax):
            tier_colors = ['#0284c7', '#2563eb', '#4f46e5', '#7c3aed']
            def get_ring(z_lv, half_w, length=L_ref):
                return np.array([
                    [0, -half_w, z_lv],
                    [length, -half_w, z_lv],
                    [length, half_w, z_lv],
                    [0, half_w, z_lv],
                    [0, -half_w, z_lv]
                ])

            prev_half_top = 0.0
            for idx, lay in enumerate(layers):
                zs, ze, h_lay = model.layer_z_ranges[idx]
                col = tier_colors[idx % len(tier_colors)]
                if idx == 0:
                    if lay.layer_type == "Đáy bằng":
                        halfB = lay.params.get("B", 12.0) / 2.0
                        r_bot = get_ring(zs, halfB)
                        r_top = get_ring(ze, halfB)
                        ax.plot(r_bot[:,0], r_bot[:,1], r_bot[:,2], color='#0ea5e9', lw=2.2)
                        if len(layers) > 1:
                            ax.plot(r_top[:,0], r_top[:,1], r_top[:,2], color='#2563eb', lw=2.4)
                        for c in range(4):
                            ax.plot([r_bot[c,0], r_top[c,0]], [r_bot[c,1], r_top[c,1]], [r_bot[c,2], r_top[c,2]], color=col, lw=1.6)
                        prev_half_top = halfB
                    elif lay.layer_type == "Đáy chữ V":
                        halfB = lay.params.get("B", 12.0) / 2.0
                        ax.plot([0, L_ref], [0, 0], [zs, zs], color='#0284c7', lw=2.6)
                        r_top = get_ring(ze, halfB)
                        if len(layers) > 1:
                            ax.plot(r_top[:,0], r_top[:,1], r_top[:,2], color='#2563eb', lw=2.4)
                        for x_pt in [0, L_ref]:
                            ax.plot([x_pt, x_pt], [-halfB, 0], [ze, zs], color=col, lw=2.0)
                            ax.plot([x_pt, x_pt], [halfB, 0], [ze, zs], color=col, lw=2.0)
                        prev_half_top = halfB
                    elif lay.layer_type == "Đáy hộp hình thang":
                        halfTop = lay.params.get("B_top", 12.0) / 2.0
                        halfBot = lay.params.get("B_bot", 7.5) / 2.0
                        r_bot = get_ring(zs, halfBot)
                        r_top = get_ring(ze, halfTop)
                        ax.plot(r_bot[:,0], r_bot[:,1], r_bot[:,2], color='#0ea5e9', lw=2.2)
                        if len(layers) > 1:
                            ax.plot(r_top[:,0], r_top[:,1], r_top[:,2], color='#2563eb', lw=2.4)
                        for c in range(4):
                            ax.plot([r_bot[c,0], r_top[c,0]], [r_bot[c,1], r_top[c,1]], [r_bot[c,2], r_top[c,2]], color=col, lw=1.6)
                        prev_half_top = halfTop
                    if len(layers) > 1:
                        ax.plot([0, 0], [-prev_half_top, prev_half_top], [ze, ze], color='#2563eb', lw=2.2)
                        ax.plot([L_ref, L_ref], [-prev_half_top, prev_half_top], [ze, ze], color='#2563eb', lw=2.2)
                else:
                    if lay.layer_type == "Hình hộp chữ nhật":
                        halfB = lay.params.get("B", 12.0) / 2.0
                        r_bot = get_ring(zs, halfB)
                        r_top = get_ring(ze, halfB)
                        if abs(halfB - prev_half_top) > 0.05:
                            for c in range(4):
                                r_prev = get_ring(zs, prev_half_top)
                                ax.plot([r_prev[c,0], r_bot[c,0]], [r_prev[c,1], r_bot[c,1]], [zs, zs], color='#64748b', lw=1.4)
                        if idx < len(layers) - 1:
                            ax.plot(r_top[:,0], r_top[:,1], r_top[:,2], color=col, lw=2.4)
                        for c in range(4):
                            ax.plot([r_bot[c,0], r_top[c,0]], [r_bot[c,1], r_top[c,1]], [r_bot[c,2], r_top[c,2]], color=col, lw=1.6)
                        prev_half_top = halfB
                    elif lay.layer_type == "Hình hộp thang":
                        halfTop = lay.params.get("B_top", 13.8) / 2.0
                        halfBot = lay.params.get("B_bot", 12.0) / 2.0
                        r_bot = get_ring(zs, halfBot)
                        r_top = get_ring(ze, halfTop)
                        if abs(halfBot - prev_half_top) > 0.05:
                            for c in range(4):
                                r_prev = get_ring(zs, prev_half_top)
                                ax.plot([r_prev[c,0], r_bot[c,0]], [r_prev[c,1], r_bot[c,1]], [zs, zs], color='#64748b', lw=1.4)
                        if idx < len(layers) - 1:
                            ax.plot(r_top[:,0], r_top[:,1], r_top[:,2], color=col, lw=2.4)
                        for c in range(4):
                            ax.plot([r_bot[c,0], r_top[c,0]], [r_bot[c,1], r_top[c,1]], [r_bot[c,2], r_top[c,2]], color=col, lw=1.6)
                        prev_half_top = halfTop

                ax.text(-3, 0, (zs+ze)/2, f"◀ {lay.name}", color=col, fontsize=9.5, fontweight='bold')

            r_topmost = get_ring(z_total, prev_half_top)
            ax.plot(r_topmost[:,0], r_topmost[:,1], r_topmost[:,2], color='#dc2626', lw=2.4, linestyle='--')

            top_half_w = prev_half_top
            x_g = np.linspace(0, L_ref, 20)
            y_g = np.linspace(-top_half_w * 0.95, top_half_w * 0.95, 12)
            X, Y = np.meshgrid(x_g, y_g)
            Z_3d = np.zeros_like(X)
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    D_mat = model.do_sau_mat_cat(X[i, j], Y[i, j], L_ref)
                    Z_3d[i, j] = max(z_total - D_mat, 0.0)

            ax.plot_surface(X, Y, Z_3d, color='#fde047', alpha=0.80, edgecolor='#ca8a04', lw=0.1, shade=True)
            ax.set_title(f"MÔ HÌNH 3D TOÀN KHUNG (XOAY 360° - {len(layers)} TẦNG KẾT CẤU)", fontsize=11, fontweight='bold', color='#0b2545', pad=10)
            ax.set_xlim(-4, L_ref+4)
            ax.set_ylim(-9.0, 9.0)
            ax.set_zlim(-0.3, z_total + 1.4)
            ax.view_init(elev=24, azim=-55)
            ax.set_axis_off()

        # 1. TAB 1: 2D KHỔ LỚN
        self.fig_2d.clf()
        gs2d = self.fig_2d.add_gridspec(2, 1, height_ratios=[1.45, 1.0], hspace=0.30)
        self.ax_trans = self.fig_2d.add_subplot(gs2d[0])
        ax_long_2d = self.fig_2d.add_subplot(gs2d[1])
        draw_2d_transverse(self.ax_trans)
        if self.custom_trans_limits is not None:
            self.ax_trans.set_xlim(self.custom_trans_limits[0])
            self.ax_trans.set_ylim(self.custom_trans_limits[1])
        else:
            self.ax_trans.set_xlim(-11.0, 13.0)
            self.ax_trans.set_ylim(-0.8, z_total + 0.8)
        draw_2d_longitudinal(ax_long_2d)
        self.fig_2d.subplots_adjust(left=0.04, right=0.96, top=0.94, bottom=0.06, hspace=0.35)
        self.canvas_2d.draw()

        # 2. TAB 2: 3D KHỔ LỚN
        self.fig_3d.clf()
        ax_3d_tab = self.fig_3d.add_subplot(1, 1, 1, projection='3d')
        draw_3d_model(ax_3d_tab)
        self.fig_3d.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.02)
        self.canvas_3d.draw()

    def thuc_hien_tinh(self):
        try:
            layers = self._doc_layers()
            loai_mat, thong_so_mat = self._doc_mat()
            rho = self._lay_f("rho", "Khối lượng riêng")
            if rho <= 0: raise ValueError("Khối lượng riêng phải > 0.")

            model = MultiTierBargeModel(layers, loai_mat, thong_so_mat)
            the_tich = model.tinh_tong_the_tich()
            khoi_luong = the_tich * rho

            self.txt_kq.delete("1.0", tk.END)
            msg = "=======================================================\n"
            msg += "       BÁO CÁO TÍNH THỂ TÍCH CÁT XÀ LAN V2 (ĐA TẦNG)   \n"
            msg += "=======================================================\n"
            msg += f"• Số lượng tầng kết cấu: {len(layers)} phần xếp chồng\n"
            for idx, lay in enumerate(layers):
                msg += f"  + {lay.name}: {lay.layer_type}\n"
                if lay.layer_type == "Đáy chữ V":
                    msg += f"    (Cạnh xiên C1 = {lay.params.get('C'):.2f}m ➔ H1 tính theo Pytago = {lay.params.get('H'):.2f}m)\n"
            msg += f"• Kiểu bề mặt cát      : Option {loai_mat}\n"
            msg += f"• Khối lượng riêng cát : {rho:.2f} tấn/m³\n"
            msg += "-------------------------------------------------------\n"
            msg += f"▶▶ TỔNG THỂ TÍCH (V)  : {the_tich:,.3f} m³\n"
            msg += f"▶▶ TỔNG KHỐI LƯỢNG (M): {khoi_luong:,.3f} tấn\n"
            msg += "=======================================================\n"
            self.txt_kq.insert(tk.END, msg)

        except Exception as e:
            messagebox.showerror("Thông báo nhập liệu", str(e))

    def reset_form(self):
        self.var_p1.set("Đáy hộp hình thang")
        self.var_p2.set("Hình hộp thang")
        self.var_p3.set("Không có phần 3")
        self.var_p4.set("Không có phần 4")
        self.var_mat.set("1 - Mặt phẳng (Dàn trải đều)")
        self.custom_trans_limits = None
        self._cap_nhat_toan_bo()

def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    UngDungV2(root)
    root.mainloop()

if __name__ == "__main__":
    main()
