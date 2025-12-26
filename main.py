import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib

matplotlib.use("TkAgg")

# Modern renk paleti
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "text": "#eaeaea",
    "text_muted": "#a0a0a0",
    "success": "#4ecca3",
    "warning": "#ffc107",
    "graph_bg": "#0f0f23",
}


class TrafficSimulation:
    def __init__(self):
        self.nodes = [
            "N1",
            "N2",
            "N3",
            "N4",
            "N5",
            "N6",
            "N7",
            "N8",
            "N9",
            "N10",
            "N11",
            "N12",
            "N13",
        ]
        self.n_map = {n: i for i, n in enumerate(self.nodes)}
        self.n_len = len(self.nodes)

        self.P = np.zeros((self.n_len, self.n_len))
        self.setup_matrix()

    def setup_matrix(self):
        def set_p(u, v, p):
            self.P[self.n_map[u], self.n_map[v]] = p

        # Yutan (Absorbing) Düğümler
        for n in ["N3", "N9", "N10", "N12"]:
            set_p(n, n, 1.0)

        # Geçişler
        set_p("N1", "N5", 1.0)
        set_p("N2", "N6", 1.0)
        set_p("N4", "N8", 1.0)
        set_p("N11", "N13", 1.0)

        # Kavşak İçi Dağılımlar
        set_p("N5", "N6", 0.7)
        set_p("N5", "N9", 0.3)
        set_p("N6", "N3", 0.2)
        set_p("N6", "N7", 0.4)
        set_p("N6", "N10", 0.4)
        set_p("N7", "N5", 0.3)
        set_p("N7", "N8", 0.7)
        set_p("N8", "N5", 0.5)
        set_p("N8", "N10", 0.5)
        set_p("N13", "N5", 0.5)
        set_p("N13", "N12", 0.5)

    def get_inflow(self, t):
        u = np.zeros(self.n_len)

        # Rush Hour: 08:00 ve 17:00 (yoğun saatler)
        if t == 8:
            n1, n2, n11 = 4200, 3800, 5000
        elif t == 17:
            n1, n2, n11 = 4800, 4200, 4600
        # Normal saatler - toplam 2000'i geçmeyecek şekilde ayarlandı
        else:
            n1, n2, n11 = 550, 450, 600  # Toplam: 1600

        u[self.n_map["N1"]] = n1
        u[self.n_map["N2"]] = n2
        u[self.n_map["N11"]] = n11
        return u

    def get_custom_inflow(self, n1, n2, n11):
        """Özel giriş değerleri ile inflow oluştur"""
        u = np.zeros(self.n_len)
        u[self.n_map["N1"]] = n1
        u[self.n_map["N2"]] = n2
        u[self.n_map["N11"]] = n11
        return u

    def run_simulation(self, hours=24):
        x = np.zeros(self.n_len)
        history = []
        for t in range(hours):
            U = self.get_inflow(t)
            x = np.dot((x + U), self.P)
            history.append(x.copy())
        return np.array(history)

    def run_custom_simulation(self, hours, n1_values, n2_values, n11_values):
        """Özel değerlerle simülasyon çalıştır"""
        x = np.zeros(self.n_len)
        history = []
        for t in range(hours):
            U = self.get_custom_inflow(n1_values[t], n2_values[t], n11_values[t])
            x = np.dot((x + U), self.P)
            history.append(x.copy())
        return np.array(history)

    def run_single_step(self, current_state, n1, n2, n11):
        """Tek adım simülasyon - mevcut durumdan bir sonraki duruma"""
        U = self.get_custom_inflow(n1, n2, n11)
        new_state = np.dot((current_state + U), self.P)
        return new_state

    def analyze_bottleneck(self, history):
        transient_indices = [
            self.n_map[n] for n in self.nodes if n not in ["N3", "N9", "N10", "N12"]
        ]
        transient_history = history[:, transient_indices]

        max_loads = transient_history.max(axis=0)
        bottleneck_idx = np.argmax(max_loads)
        bottleneck_node_name = self.nodes[transient_indices[bottleneck_idx]]
        max_val = max_loads[bottleneck_idx]

        return bottleneck_node_name, max_val

    def analyze_steady_state(self):
        transient_nodes = [n for n in self.nodes if n not in ["N3", "N9", "N10", "N12"]]
        t_indices = [self.n_map[n] for n in transient_nodes]

        Q = self.P[np.ix_(t_indices, t_indices)]
        I = np.eye(len(t_indices))

        try:
            N_fund = np.linalg.inv(I - Q)
            col_sums = N_fund.sum(axis=0)
            struct_bn_idx = np.argmax(col_sums)
            struct_bn_node = transient_nodes[struct_bn_idx]
            return struct_bn_node, N_fund
        except np.linalg.LinAlgError:
            return None, None


class ModernButton(tk.Canvas):
    """Hover efektli modern buton"""

    def __init__(
        self, parent, text, command, width=220, height=45, color=None, **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=COLORS["bg_card"],
            highlightthickness=0,
            **kwargs,
        )

        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.hovered = False
        self.base_color = color or COLORS["accent"]
        self.hover_color = COLORS["accent_hover"]

        self.draw_button()

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw_button(self):
        self.delete("all")
        color = self.hover_color if self.hovered else self.base_color

        # Rounded rectangle
        r = 10
        self.create_arc(
            0, 0, r * 2, r * 2, start=90, extent=90, fill=color, outline=color
        )
        self.create_arc(
            self.width - r * 2,
            0,
            self.width,
            r * 2,
            start=0,
            extent=90,
            fill=color,
            outline=color,
        )
        self.create_arc(
            0,
            self.height - r * 2,
            r * 2,
            self.height,
            start=180,
            extent=90,
            fill=color,
            outline=color,
        )
        self.create_arc(
            self.width - r * 2,
            self.height - r * 2,
            self.width,
            self.height,
            start=270,
            extent=90,
            fill=color,
            outline=color,
        )
        self.create_rectangle(
            r, 0, self.width - r, self.height, fill=color, outline=color
        )
        self.create_rectangle(
            0, r, self.width, self.height - r, fill=color, outline=color
        )

        # Text
        self.create_text(
            self.width // 2,
            self.height // 2,
            text=self.text,
            fill="white",
            font=("Segoe UI", 11, "bold"),
        )

    def on_enter(self, e):
        self.hovered = True
        self.draw_button()
        self.config(cursor="hand2")

    def on_leave(self, e):
        self.hovered = False
        self.draw_button()

    def on_click(self, e):
        if self.command:
            self.command()


class ModernSlider(tk.Frame):
    """Modern görünümlü slider"""

    def __init__(self, parent, label, from_, to, initial, command=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)

        self.command = command
        self.value = tk.IntVar(value=initial)
        self.from_ = from_
        self.to_ = to

        # Label
        self.label = tk.Label(
            self,
            text=label,
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        )
        self.label.pack(anchor="w")

        # Slider container
        self.slider_frame = tk.Frame(self, bg=COLORS["bg_card"])
        self.slider_frame.pack(fill=tk.X, pady=5)

        # Slider
        self.slider = ttk.Scale(
            self.slider_frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=self.value,
            command=self._on_change,
        )
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Value display
        self.value_label = tk.Label(
            self.slider_frame,
            text=str(initial),
            bg=COLORS["bg_card"],
            fg=COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
            width=6,
        )
        self.value_label.pack(side=tk.RIGHT, padx=(10, 0))

    def _on_change(self, val):
        int_val = int(float(val))
        # Limit kontrolü
        int_val = max(self.from_, min(self.to_, int_val))
        self.value.set(int_val)
        self.value_label.config(text=str(int_val))
        if self.command:
            self.command(int_val)

    def get(self):
        return self.value.get()

    def set(self, val, trigger_callback=False):
        val = max(self.from_, min(self.to_, val))
        self.value.set(val)
        self.slider.set(val)
        self.value_label.config(text=str(val))
        if trigger_callback and self.command:
            self.command(val)

    def set_range(self, from_, to):
        """Slider aralığını değiştir"""
        self.from_ = from_
        self.to_ = to
        self.slider.config(from_=from_, to=to)
        # Mevcut değer aralık dışındaysa düzelt
        current = self.get()
        if current < from_:
            self.set(from_)
        elif current > to:
            self.set(to)


class InteractiveSimulation(tk.Toplevel):
    """İnteraktif simülasyon penceresi"""

    def __init__(self, parent, sim):
        super().__init__(parent)
        self.sim = sim
        self.parent = parent

        self.title("🎮 İnteraktif Trafik Simülasyonu")
        self.geometry("1400x900")
        self.configure(bg=COLORS["bg_dark"])
        self.minsize(1200, 800)

        # Simülasyon durumu
        self.current_hour = 0
        self.state_history = []
        self.current_state = np.zeros(self.sim.n_len)

        self.create_widgets()
        self.update_visualization()

    def create_widgets(self):
        # Ana container
        main_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Başlık
        title_frame = tk.Frame(main_frame, bg=COLORS["bg_card"])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            title_frame,
            text="🎮 İnteraktif Trafik Simülasyonu",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=15)

        tk.Label(
            title_frame,
            text="Parametreleri değiştirin ve simülasyonu adım adım izleyin",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 10),
        ).pack(pady=(0, 15))

        # İçerik alanı
        content_frame = tk.Frame(main_frame, bg=COLORS["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Sol Panel - Kontroller
        left_panel = tk.Frame(content_frame, bg=COLORS["bg_card"], width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)

        # Saat kontrolü
        time_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        time_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            time_frame,
            text="⏰ Saat Kontrolü",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.hour_slider = ModernSlider(
            time_frame, "Saat (0-23):", 0, 23, 0, command=self.on_hour_change
        )
        self.hour_slider.pack(fill=tk.X)

        # Mevcut saat göstergesi
        self.time_display = tk.Label(
            time_frame,
            text="🕐 00:00",
            bg=COLORS["bg_card"],
            fg=COLORS["success"],
            font=("Segoe UI", 24, "bold"),
        )
        self.time_display.pack(pady=15)

        # Ayırıcı
        tk.Frame(left_panel, bg=COLORS["accent"], height=2).pack(
            fill=tk.X, padx=20, pady=10
        )

        # Araç sayısı kontrolleri
        vehicle_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        vehicle_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            vehicle_frame,
            text="🚗 Araç Girişleri (araç/saat)",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        self.n1_slider = ModernSlider(
            vehicle_frame,
            "N1 (Kuzey Giriş):",
            0,
            700,
            550,
            command=self.on_vehicle_change,
        )
        self.n1_slider.pack(fill=tk.X, pady=5)

        self.n2_slider = ModernSlider(
            vehicle_frame,
            "N2 (Doğu Giriş):",
            0,
            700,
            450,
            command=self.on_vehicle_change,
        )
        self.n2_slider.pack(fill=tk.X, pady=5)

        self.n11_slider = ModernSlider(
            vehicle_frame,
            "N11 (Güney Giriş):",
            0,
            700,
            600,
            command=self.on_vehicle_change,
        )
        self.n11_slider.pack(fill=tk.X, pady=5)

        # Limit göstergesi
        self.limit_label = tk.Label(
            vehicle_frame,
            text="✓ Normal Saat: 0-2000 araç",
            bg=COLORS["bg_card"],
            fg=COLORS["success"],
            font=("Segoe UI", 9),
        )
        self.limit_label.pack(pady=(10, 5))

        # Toplam gösterge
        self.total_label = tk.Label(
            vehicle_frame,
            text="Toplam Giriş: 1,600 araç/saat",
            bg=COLORS["bg_card"],
            fg=COLORS["success"],
            font=("Segoe UI", 10, "bold"),
        )
        self.total_label.pack(pady=5)

        # Ayırıcı
        tk.Frame(left_panel, bg=COLORS["accent"], height=2).pack(
            fill=tk.X, padx=20, pady=10
        )

        # Kontrol butonları
        btn_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        btn_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(
            btn_frame,
            text="🎮 Simülasyon Kontrolleri",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        ModernButton(
            btn_frame,
            "▶  Adım İlerle",
            self.step_forward,
            width=260,
            height=40,
            color=COLORS["success"],
        ).pack(pady=5)

        ModernButton(
            btn_frame,
            "⏭  10 Adım İlerle",
            self.step_forward_10,
            width=260,
            height=40,
            color="#3498db",
        ).pack(pady=5)

        ModernButton(
            btn_frame,
            "🔄  Sıfırla",
            self.reset_simulation,
            width=260,
            height=40,
            color=COLORS["warning"],
        ).pack(pady=5)

        ModernButton(
            btn_frame,
            "📊  Rush Hour Yükle",
            self.load_rush_hour,
            width=260,
            height=40,
            color="#9b59b6",
        ).pack(pady=5)

        # Durum göstergesi
        status_frame = tk.Frame(left_panel, bg="#1e3a5f")
        status_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(
            status_frame,
            text="📊 Simülasyon Durumu",
            bg="#1e3a5f",
            fg=COLORS["text"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.status_text = tk.Label(
            status_frame,
            text="Adım: 0\nToplam Araç: 0\nDarboğaz: -",
            bg="#1e3a5f",
            fg=COLORS["text_muted"],
            font=("Consolas", 9),
            justify="left",
        )
        self.status_text.pack(anchor="w", padx=15, pady=(0, 15))

        # Sağ Panel - Görselleştirme
        right_panel = tk.Frame(content_frame, bg=COLORS["bg_card"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.viz_frame = right_panel

    def on_hour_change(self, val):
        self.current_hour = val
        self.time_display.config(text=f"🕐 {val:02d}:00")

        # Rush hour kontrolü (saat 8 ve 17)
        is_rush_hour = val in [8, 17]

        if is_rush_hour:
            # Rush hour: 2000-5000 arası
            self.n1_slider.set_range(667, 1667)
            self.n2_slider.set_range(667, 1667)
            self.n11_slider.set_range(667, 1667)
            self.limit_label.config(
                text="⚠️ Rush Hour: 2000-5000 araç", fg=COLORS["warning"]
            )
            self.time_display.config(fg=COLORS["warning"])

            # Varsayılan rush hour değerleri
            if val == 8:
                self.n1_slider.set(1400)
                self.n2_slider.set(1300)
                self.n11_slider.set(1300)
            else:  # 17
                self.n1_slider.set(1500)
                self.n2_slider.set(1400)
                self.n11_slider.set(1100)
        else:
            # Normal saat: 0-2000 arası
            self.n1_slider.set_range(0, 700)
            self.n2_slider.set_range(0, 700)
            self.n11_slider.set_range(0, 700)
            self.limit_label.config(
                text="✓ Normal Saat: 0-2000 araç", fg=COLORS["success"]
            )
            self.time_display.config(fg=COLORS["success"])

            # Varsayılan normal değerler
            self.n1_slider.set(550)
            self.n2_slider.set(450)
            self.n11_slider.set(600)

        self.update_total()

    def on_vehicle_change(self, val=None):
        self.update_total()

    def update_hour_limits(self):
        """Saate göre slider limitlerini güncelle (değerleri değiştirmeden)"""
        is_rush_hour = self.current_hour in [8, 17]

        if is_rush_hour:
            # Rush hour: 2000-5000 arası (toplam için her slider 667-1667)
            self.n1_slider.set_range(667, 1667)
            self.n2_slider.set_range(667, 1667)
            self.n11_slider.set_range(667, 1667)
            self.limit_label.config(
                text="⚠️ Rush Hour: 2000-5000 araç", fg=COLORS["warning"]
            )
            self.time_display.config(fg=COLORS["warning"])
        else:
            # Normal saat: 0-2000 arası (toplam için her slider 0-700)
            self.n1_slider.set_range(0, 700)
            self.n2_slider.set_range(0, 700)
            self.n11_slider.set_range(0, 700)
            self.limit_label.config(
                text="✓ Normal Saat: 0-2000 araç", fg=COLORS["success"]
            )
            self.time_display.config(fg=COLORS["success"])

        self.update_total()

    def update_total(self):
        total = self.n1_slider.get() + self.n2_slider.get() + self.n11_slider.get()
        color = (
            COLORS["success"]
            if total <= 2000
            else (COLORS["warning"] if total <= 5000 else COLORS["accent"])
        )
        self.total_label.config(text=f"Toplam Giriş: {total:,} araç/saat", fg=color)

    def step_forward(self):
        """Bir adım ilerle"""
        n1 = self.n1_slider.get()
        n2 = self.n2_slider.get()
        n11 = self.n11_slider.get()

        self.current_state = self.sim.run_single_step(self.current_state, n1, n2, n11)
        self.state_history.append(self.current_state.copy())

        # Saati ilerlet
        self.current_hour = (self.current_hour + 1) % 24
        self.hour_slider.set(self.current_hour)

        # Saat göstergesini ve limitleri güncelle
        self.time_display.config(text=f"🕐 {self.current_hour:02d}:00")
        self.update_hour_limits()

        self.update_visualization()
        self.update_status()

    def step_forward_10(self):
        """10 adım ilerle"""
        for _ in range(10):
            self.step_forward()

    def reset_simulation(self):
        """Simülasyonu sıfırla"""
        self.current_state = np.zeros(self.sim.n_len)
        self.state_history = []
        self.current_hour = 0
        self.hour_slider.set(0)
        self.time_display.config(text="🕐 00:00")

        # Normal saat limitleri
        self.n1_slider.set_range(0, 700)
        self.n2_slider.set_range(0, 700)
        self.n11_slider.set_range(0, 700)
        self.limit_label.config(text="✓ Normal Saat: 0-2000 araç", fg=COLORS["success"])

        self.n1_slider.set(550)
        self.n2_slider.set(450)
        self.n11_slider.set(600)
        self.update_total()
        self.update_visualization()
        self.update_status()

    def load_rush_hour(self):
        """Rush hour değerlerini yükle"""
        self.current_hour = 8
        self.hour_slider.set(8)
        self.time_display.config(text="🕐 08:00")

        # Rush hour limitleri
        self.n1_slider.set_range(667, 1667)
        self.n2_slider.set_range(667, 1667)
        self.n11_slider.set_range(667, 1667)
        self.limit_label.config(
            text="⚠️ Rush Hour: 2000-5000 araç", fg=COLORS["warning"]
        )

        self.n1_slider.set(1400)
        self.n2_slider.set(1300)
        self.n11_slider.set(1300)
        self.update_total()

    def update_status(self):
        """Durum metnini güncelle"""
        total_vehicles = np.sum(self.current_state)

        # Darboğaz bul
        transient_indices = [
            self.sim.n_map[n]
            for n in self.sim.nodes
            if n not in ["N3", "N9", "N10", "N12"]
        ]
        transient_values = self.current_state[transient_indices]
        if np.max(transient_values) > 0:
            bn_idx = np.argmax(transient_values)
            bn_node = [
                n for n in self.sim.nodes if n not in ["N3", "N9", "N10", "N12"]
            ][bn_idx]
            bn_val = int(transient_values[bn_idx])
        else:
            bn_node = "-"
            bn_val = 0

        status = f"Adım: {len(self.state_history)}\n"
        status += f"Toplam Araç: {int(total_vehicles):,}\n"
        status += f"Darboğaz: {bn_node} ({bn_val:,})"

        self.status_text.config(text=status)

    def update_visualization(self):
        """Görselleştirmeyi güncelle"""
        for widget in self.viz_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(10, 8), facecolor=COLORS["bg_card"])

        # 2x2 subplot
        ax1 = fig.add_subplot(221)  # Ağ grafiği
        ax2 = fig.add_subplot(222)  # Düğüm değerleri bar chart
        ax3 = fig.add_subplot(212)  # Zaman serisi

        # Ağ Grafiği (Düğüm pozisyonları)
        ax1.set_facecolor(COLORS["graph_bg"])
        ax1.set_title(
            "🗺️ Trafik Ağı Durumu",
            fontsize=12,
            fontweight="bold",
            color=COLORS["text"],
            pad=10,
        )

        # Düğüm pozisyonları (manuel yerleşim)
        positions = {
            "N1": (0.5, 1.0),  # Kuzey giriş
            "N2": (1.0, 0.5),  # Doğu giriş
            "N3": (1.0, 0.8),  # Çıkış
            "N4": (0.0, 0.5),  # Batı giriş
            "N5": (0.5, 0.7),  # Merkez üst
            "N6": (0.7, 0.5),  # Merkez sağ
            "N7": (0.5, 0.5),  # Merkez
            "N8": (0.3, 0.5),  # Merkez sol
            "N9": (0.5, 0.3),  # Çıkış
            "N10": (1.0, 0.2),  # Çıkış
            "N11": (0.5, 0.0),  # Güney giriş
            "N12": (0.0, 0.2),  # Çıkış
            "N13": (0.3, 0.2),  # Güney kavşak
        }

        # Bağlantıları çiz
        connections = [
            ("N1", "N5"),
            ("N2", "N6"),
            ("N4", "N8"),
            ("N11", "N13"),
            ("N5", "N6"),
            ("N5", "N9"),
            ("N6", "N3"),
            ("N6", "N7"),
            ("N6", "N10"),
            ("N7", "N5"),
            ("N7", "N8"),
            ("N8", "N5"),
            ("N8", "N10"),
            ("N13", "N5"),
            ("N13", "N12"),
        ]

        for src, dst in connections:
            x1, y1 = positions[src]
            x2, y2 = positions[dst]
            ax1.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=COLORS["text_muted"], alpha=0.5),
            )

        # Düğümleri çiz
        max_val = max(np.max(self.current_state), 1)
        for node, (x, y) in positions.items():
            idx = self.sim.n_map[node]
            val = self.current_state[idx]

            # Renk ve boyut değere göre
            if node in ["N3", "N9", "N10", "N12"]:
                color = COLORS["success"]  # Çıkışlar
                size = 400
            elif node in ["N1", "N2", "N4", "N11"]:
                color = "#3498db"  # Girişler
                size = 400
            else:
                # Yoğunluğa göre renk
                intensity = min(val / max_val, 1) if max_val > 0 else 0
                if intensity > 0.7:
                    color = COLORS["accent"]
                elif intensity > 0.3:
                    color = COLORS["warning"]
                else:
                    color = COLORS["success"]
                size = 300 + intensity * 400

            ax1.scatter(
                x, y, s=size, c=color, zorder=5, edgecolors="white", linewidths=2
            )
            ax1.annotate(
                f"{node}\n{int(val):,}",
                (x, y),
                ha="center",
                va="center",
                fontsize=7,
                fontweight="bold",
                color="white",
            )

        ax1.set_xlim(-0.1, 1.1)
        ax1.set_ylim(-0.1, 1.1)
        ax1.axis("off")

        # Bar Chart - Düğüm değerleri
        ax2.set_facecolor(COLORS["graph_bg"])
        ax2.set_title(
            "📊 Düğüm Yoğunlukları",
            fontsize=12,
            fontweight="bold",
            color=COLORS["text"],
            pad=10,
        )

        transient_nodes = [
            n for n in self.sim.nodes if n not in ["N3", "N9", "N10", "N12"]
        ]
        transient_values = [
            self.current_state[self.sim.n_map[n]] for n in transient_nodes
        ]

        colors = []
        for val in transient_values:
            if val > 3000:
                colors.append(COLORS["accent"])
            elif val > 1000:
                colors.append(COLORS["warning"])
            else:
                colors.append(COLORS["success"])

        bars = ax2.barh(transient_nodes, transient_values, color=colors)
        ax2.set_xlabel("Araç Sayısı", fontsize=10, color=COLORS["text_muted"])
        ax2.tick_params(colors=COLORS["text_muted"])

        for spine in ax2.spines.values():
            spine.set_color(COLORS["text_muted"])
            spine.set_alpha(0.3)

        # Değerleri bar üzerine yaz
        for bar, val in zip(bars, transient_values):
            ax2.text(
                bar.get_width() + 50,
                bar.get_y() + bar.get_height() / 2,
                f"{int(val):,}",
                va="center",
                fontsize=8,
                color=COLORS["text"],
            )

        # Zaman Serisi
        ax3.set_facecolor(COLORS["graph_bg"])
        ax3.set_title(
            "📈 Zaman İçinde Değişim",
            fontsize=12,
            fontweight="bold",
            color=COLORS["text"],
            pad=10,
        )

        if len(self.state_history) > 1:
            history_array = np.array(self.state_history)
            steps = range(len(self.state_history))

            plot_nodes = ["N5", "N6", "N7", "N8"]
            plot_colors = ["#e94560", "#4ecca3", "#ffc107", "#00d9ff"]

            for node, color in zip(plot_nodes, plot_colors):
                idx = self.sim.n_map[node]
                ax3.plot(
                    steps,
                    history_array[:, idx],
                    label=node,
                    color=color,
                    linewidth=2,
                    marker="o",
                    markersize=3,
                )

            ax3.legend(
                loc="upper left",
                facecolor=COLORS["bg_card"],
                edgecolor=COLORS["accent"],
                labelcolor=COLORS["text"],
            )
        else:
            ax3.text(
                0.5,
                0.5,
                "Simülasyonu başlatmak için\n'Adım İlerle' butonuna tıklayın",
                ha="center",
                va="center",
                fontsize=12,
                color=COLORS["text_muted"],
                transform=ax3.transAxes,
            )

        ax3.set_xlabel("Adım", fontsize=10, color=COLORS["text_muted"])
        ax3.set_ylabel("Araç Sayısı", fontsize=10, color=COLORS["text_muted"])
        ax3.tick_params(colors=COLORS["text_muted"])
        ax3.grid(True, alpha=0.2, color=COLORS["text_muted"])

        for spine in ax3.spines.values():
            spine.set_color(COLORS["text_muted"])
            spine.set_alpha(0.3)

        fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚗 İTÜ Trafik Analizi - Markov Zinciri Simülasyonu")
        self.geometry("1200x800")
        self.configure(bg=COLORS["bg_dark"])
        self.minsize(1000, 700)

        self.sim = TrafficSimulation()
        self.history = None

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        self.create_widgets()

    def configure_styles(self):
        self.style.configure("Dark.TFrame", background=COLORS["bg_dark"])
        self.style.configure("Card.TFrame", background=COLORS["bg_card"])
        self.style.configure(
            "Title.TLabel",
            background=COLORS["bg_card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 18, "bold"),
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg_card"],
            foreground=COLORS["text_muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Info.TLabel",
            background=COLORS["bg_card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10),
        )
        # Slider stili
        self.style.configure(
            "TScale",
            background=COLORS["bg_card"],
            troughcolor=COLORS["graph_bg"],
        )

    def create_widgets(self):
        # Ana container
        main_container = tk.Frame(self, bg=COLORS["bg_dark"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sol Panel
        left_panel = tk.Frame(main_container, bg=COLORS["bg_card"], width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)

        # Logo/Başlık Alanı
        header_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        header_frame.pack(fill=tk.X, padx=20, pady=25)

        title_label = tk.Label(
            header_frame,
            text="🚦 Trafik Analizi",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Markov Zinciri Simülasyonu",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 10),
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Ayırıcı çizgi
        separator = tk.Frame(left_panel, bg=COLORS["accent"], height=2)
        separator.pack(fill=tk.X, padx=20, pady=10)

        # Butonlar
        buttons_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)

        btn1 = ModernButton(buttons_frame, "▶  Simülasyonu Başlat", self.run_sim)
        btn1.pack(pady=8)

        btn_interactive = ModernButton(
            buttons_frame, "🎮  İnteraktif Mod", self.open_interactive, color="#9b59b6"
        )
        btn_interactive.pack(pady=8)

        btn2 = ModernButton(buttons_frame, "📊  Darboğaz Analizi", self.show_bottleneck)
        btn2.pack(pady=8)

        btn3 = ModernButton(
            buttons_frame, "⚖  Steady State Analizi", self.show_steady_state
        )
        btn3.pack(pady=8)

        btn4 = ModernButton(
            buttons_frame, "🎲  P Matrisi Göster", self.show_probability_matrix
        )
        btn4.pack(pady=8)

        # Info Card
        info_frame = tk.Frame(left_panel, bg="#1e3a5f")
        info_frame.pack(fill=tk.X, padx=20, pady=20)

        info_title = tk.Label(
            info_frame,
            text="ℹ️  Bilgi",
            bg="#1e3a5f",
            fg=COLORS["text"],
            font=("Segoe UI", 11, "bold"),
        )
        info_title.pack(anchor="w", padx=15, pady=(15, 5))

        info_text = tk.Label(
            info_frame,
            text="Rush Hour: 08:00 & 17:00\nNormal: <2000 araç/saat\n\n13 düğümlü ağ modeli\n4 çıkış noktası (N3,N9,N10,N12)",
            bg="#1e3a5f",
            fg=COLORS["text_muted"],
            font=("Segoe UI", 9),
            justify="left",
        )
        info_text.pack(anchor="w", padx=15, pady=(0, 15))

        # Log Alanı
        log_label = tk.Label(
            left_panel,
            text="📋 Simülasyon Logları",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 11, "bold"),
        )
        log_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.text_output = tk.Text(
            left_panel,
            height=8,
            width=30,
            bg=COLORS["graph_bg"],
            fg=COLORS["success"],
            font=("Consolas", 9),
            relief="flat",
            insertbackground=COLORS["text"],
        )
        self.text_output.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Sağ Panel (Grafik)
        self.graph_frame = tk.Frame(main_container, bg=COLORS["bg_card"])
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Başlangıç mesajı
        self.show_welcome()

    def show_welcome(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        welcome_frame = tk.Frame(self.graph_frame, bg=COLORS["bg_card"])
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center")

        emoji = tk.Label(
            welcome_frame, text="🚗", bg=COLORS["bg_card"], font=("Segoe UI", 72)
        )
        emoji.pack()

        welcome_text = tk.Label(
            welcome_frame,
            text='Simülasyonu başlatmak için\n"Simülasyonu Başlat" veya "İnteraktif Mod" butonuna tıklayın',
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 14),
            justify="center",
        )
        welcome_text.pack(pady=20)

    def log(self, message):
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.see(tk.END)

    def open_interactive(self):
        """İnteraktif simülasyon penceresini aç"""
        self.log("✓ İnteraktif mod açıldı!")
        InteractiveSimulation(self, self.sim)

    def run_sim(self):
        self.history = self.sim.run_simulation()
        self.log("✓ Simülasyon tamamlandı!")
        self.log(f"  24 saatlik veri oluşturuldu.")
        self.plot_results()

    def plot_results(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Figure oluştur
        fig = Figure(figsize=(10, 7), facecolor=COLORS["bg_card"])

        # 2 subplot: üstte ana grafik, altta heatmap
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        hours = np.arange(24)

        # Grafik 1: Düğüm yoğunlukları
        ax1.set_facecolor(COLORS["graph_bg"])

        colors_plot = ["#e94560", "#4ecca3", "#ffc107", "#00d9ff"]
        target_nodes = ["N5", "N6", "N7", "N8"]

        for i, node in enumerate(target_nodes):
            idx = self.sim.n_map[node]
            ax1.plot(
                hours,
                self.history[:, idx],
                label=f"{node}",
                color=colors_plot[i],
                linewidth=2.5,
                marker="o",
                markersize=4,
            )

        # Rush hour bölgelerini vurgula
        ax1.axvspan(7.5, 8.5, alpha=0.3, color="#e94560", label="Rush Hour")
        ax1.axvspan(16.5, 17.5, alpha=0.3, color="#e94560")

        ax1.set_title(
            "🚦 Saatlik Düğüm Yoğunlukları",
            fontsize=14,
            fontweight="bold",
            color=COLORS["text"],
            pad=15,
        )
        ax1.set_xlabel("Saat", fontsize=10, color=COLORS["text_muted"])
        ax1.set_ylabel("Araç Sayısı", fontsize=10, color=COLORS["text_muted"])
        ax1.legend(
            loc="upper right",
            facecolor=COLORS["bg_card"],
            edgecolor=COLORS["accent"],
            labelcolor=COLORS["text"],
        )
        ax1.grid(True, alpha=0.2, color=COLORS["text_muted"])
        ax1.tick_params(colors=COLORS["text_muted"])
        ax1.set_xticks(range(0, 24, 2))

        for spine in ax1.spines.values():
            spine.set_color(COLORS["text_muted"])
            spine.set_alpha(0.3)

        # Grafik 2: Tüm düğümlerin heatmap'i
        ax2.set_facecolor(COLORS["graph_bg"])

        # Sadece transient (geçici) düğümleri göster
        transient_nodes = [
            n for n in self.sim.nodes if n not in ["N3", "N9", "N10", "N12"]
        ]
        transient_indices = [self.sim.n_map[n] for n in transient_nodes]
        transient_data = self.history[:, transient_indices].T

        im = ax2.imshow(
            transient_data, aspect="auto", cmap="hot", interpolation="nearest"
        )
        ax2.set_yticks(range(len(transient_nodes)))
        ax2.set_yticklabels(transient_nodes)
        ax2.set_xticks(range(0, 24, 2))
        ax2.set_xlabel("Saat", fontsize=10, color=COLORS["text_muted"])
        ax2.set_title(
            "🔥 Trafik Yoğunluk Haritası (Heatmap)",
            fontsize=14,
            fontweight="bold",
            color=COLORS["text"],
            pad=15,
        )
        ax2.tick_params(colors=COLORS["text_muted"])

        cbar = fig.colorbar(im, ax=ax2, shrink=0.8)
        cbar.ax.tick_params(colors=COLORS["text_muted"])
        cbar.set_label("Araç Sayısı", color=COLORS["text_muted"])

        fig.tight_layout(pad=3)

        # Canvas'a yerleştir
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_bottleneck(self):
        if self.history is None:
            messagebox.showwarning("⚠️ Uyarı", "Önce simülasyonu çalıştırın!")
            return

        node, val = self.sim.analyze_bottleneck(self.history)

        self.log("\n─── DARBOĞAZ ANALİZİ ───")
        self.log(f"  En yoğun düğüm: {node}")
        self.log(f"  Maksimum araç: {int(val)}")

        # Modern dialog
        dialog = tk.Toplevel(self)
        dialog.title("Darboğaz Analizi")
        dialog.geometry("350x250")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="🚧", bg=COLORS["bg_card"], font=("Segoe UI", 48)).pack(
            pady=20
        )
        tk.Label(
            dialog,
            text="Darboğaz Tespit Edildi!",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack()
        tk.Label(
            dialog,
            text=f"Düğüm: {node}\nMaksimum Araç: {int(val):,}",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 12),
            justify="center",
        ).pack(pady=15)

        close_btn = ModernButton(dialog, "Tamam", dialog.destroy, width=120, height=40)
        close_btn.pack(pady=10)

    def show_steady_state(self):
        node, N_matrix = self.sim.analyze_steady_state()

        if node:
            self.log("\n─── STEADY STATE ───")
            self.log(f"  Yapısal darboğaz: {node}")
            self.log("  Ağ topolojisi trafiği")
            self.log(f"  {node}'de biriktiriyor.")

            dialog = tk.Toplevel(self)
            dialog.title("Steady State Analizi")
            dialog.geometry("400x300")
            dialog.configure(bg=COLORS["bg_card"])
            dialog.transient(self)
            dialog.grab_set()

            tk.Label(
                dialog, text="⚖️", bg=COLORS["bg_card"], font=("Segoe UI", 48)
            ).pack(pady=20)
            tk.Label(
                dialog,
                text="Durağan Durum Analizi",
                bg=COLORS["bg_card"],
                fg=COLORS["text"],
                font=("Segoe UI", 14, "bold"),
            ).pack()

            explanation = f"""Yapısal Darboğaz: {node}

Simülasyon girişlerinden bağımsız olarak,
ağ topolojisi trafiğin yapısal olarak
{node} düğümünde birikmesine neden olmaktadır.

Bu, Markov zincirinin Fundamental Matrix
analizi ile tespit edilmiştir."""

            tk.Label(
                dialog,
                text=explanation,
                bg=COLORS["bg_card"],
                fg=COLORS["text_muted"],
                font=("Segoe UI", 10),
                justify="center",
            ).pack(pady=15)

            close_btn = ModernButton(
                dialog, "Tamam", dialog.destroy, width=120, height=40
            )
            close_btn.pack(pady=10)
        else:
            self.log("✗ Matris hatası!")

    def show_probability_matrix(self):
        """P olasılık matrisini görselleştir"""
        self.log("\n─── P MATRİSİ ───")
        self.log("  Geçiş olasılıkları yüklendi.")

        # Yeni pencere oluştur
        matrix_window = tk.Toplevel(self)
        matrix_window.title("🎲 P Olasılık Matrisi (Geçiş Matrisi)")
        matrix_window.geometry("1100x750")
        matrix_window.configure(bg=COLORS["bg_dark"])
        matrix_window.transient(self)

        # Ana container
        main_frame = tk.Frame(matrix_window, bg=COLORS["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Başlık
        title_frame = tk.Frame(main_frame, bg=COLORS["bg_card"])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            title_frame,
            text="🎲 Markov Zinciri Geçiş Olasılık Matrisi (P)",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=15)

        tk.Label(
            title_frame,
            text="P[i,j] = i düğümünden j düğümüne geçiş olasılığı",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 10),
        ).pack(pady=(0, 15))

        # İki panel: Sol heatmap, Sağ tablo
        content_frame = tk.Frame(main_frame, bg=COLORS["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Sol Panel - Heatmap
        left_frame = tk.Frame(content_frame, bg=COLORS["bg_card"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        fig = Figure(figsize=(6, 5), facecolor=COLORS["bg_card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["graph_bg"])

        # Heatmap çiz
        im = ax.imshow(self.sim.P, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)

        # Eksen etiketleri
        ax.set_xticks(range(self.sim.n_len))
        ax.set_yticks(range(self.sim.n_len))
        ax.set_xticklabels(self.sim.nodes, fontsize=8, rotation=45)
        ax.set_yticklabels(self.sim.nodes, fontsize=8)
        ax.tick_params(colors=COLORS["text_muted"])

        # Her hücreye değer yaz
        for i in range(self.sim.n_len):
            for j in range(self.sim.n_len):
                val = self.sim.P[i, j]
                if val > 0:
                    color = "white" if val > 0.5 else "black"
                    ax.text(
                        j,
                        i,
                        f"{val:.1f}",
                        ha="center",
                        va="center",
                        fontsize=7,
                        color=color,
                        fontweight="bold",
                    )

        ax.set_title(
            "Geçiş Olasılıkları Heatmap",
            fontsize=12,
            fontweight="bold",
            color=COLORS["text"],
            pad=10,
        )
        ax.set_xlabel("Hedef Düğüm (j)", fontsize=10, color=COLORS["text_muted"])
        ax.set_ylabel("Kaynak Düğüm (i)", fontsize=10, color=COLORS["text_muted"])

        # Colorbar
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.tick_params(colors=COLORS["text_muted"])
        cbar.set_label("Olasılık", color=COLORS["text_muted"])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=left_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sağ Panel - Detaylı Geçiş Listesi
        right_frame = tk.Frame(content_frame, bg=COLORS["bg_card"], width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        tk.Label(
            right_frame,
            text="📋 Geçiş Detayları",
            bg=COLORS["bg_card"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=(15, 10))

        # Scrollable text area
        text_frame = tk.Frame(right_frame, bg=COLORS["bg_card"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        detail_text = tk.Text(
            text_frame,
            bg=COLORS["graph_bg"],
            fg=COLORS["success"],
            font=("Consolas", 9),
            relief="flat",
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
        )
        detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=detail_text.yview)

        # Geçişleri listele
        detail_text.insert(tk.END, "═══ YUTAN DÜĞÜMLER ═══\n")
        detail_text.insert(tk.END, "(Çıkış Noktaları)\n\n")
        for node in ["N3", "N9", "N10", "N12"]:
            detail_text.insert(tk.END, f"  • {node} → {node} (1.0)\n")

        detail_text.insert(tk.END, "\n═══ DİREKT GEÇİŞLER ═══\n\n")
        direct_transitions = [
            ("N1", "N5", "Giriş → Kavşak"),
            ("N2", "N6", "Giriş → Kavşak"),
            ("N4", "N8", "Giriş → Kavşak"),
            ("N11", "N13", "Giriş → Kavşak"),
        ]
        for src, dst, desc in direct_transitions:
            detail_text.insert(tk.END, f"  • {src} → {dst} (1.0)\n")
            detail_text.insert(tk.END, f"    {desc}\n\n")

        detail_text.insert(tk.END, "═══ KAVŞAK DAĞILIMLARI ═══\n\n")
        distributions = [
            ("N5", [("N6", 0.7), ("N9", 0.3)]),
            ("N6", [("N3", 0.2), ("N7", 0.4), ("N10", 0.4)]),
            ("N7", [("N5", 0.3), ("N8", 0.7)]),
            ("N8", [("N5", 0.5), ("N10", 0.5)]),
            ("N13", [("N5", 0.5), ("N12", 0.5)]),
        ]
        for src, targets in distributions:
            detail_text.insert(tk.END, f"  {src} düğümünden:\n")
            for dst, prob in targets:
                bar = "█" * int(prob * 10) + "░" * (10 - int(prob * 10))
                detail_text.insert(tk.END, f"    → {dst}: {bar} {prob:.0%}\n")
            detail_text.insert(tk.END, "\n")

        detail_text.config(state=tk.DISABLED)

        # Alt bilgi
        info_frame = tk.Frame(main_frame, bg=COLORS["bg_card"])
        info_frame.pack(fill=tk.X, pady=(15, 0))

        tk.Label(
            info_frame,
            text="💡 Not: Satır toplamları 1'e eşittir (stokastik matris). Yutan düğümler kendine döner.",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 9),
        ).pack(pady=10)

        # Kapat butonu
        close_btn = ModernButton(
            info_frame, "Kapat", matrix_window.destroy, width=120, height=40
        )
        close_btn.pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
