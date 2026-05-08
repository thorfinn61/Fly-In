import tkinter as tk
import math
from typing import Any, Dict, List, Optional, Tuple


class Renderer:
    def __init__(self, simulation: Any) -> None:
        self.sim = simulation

        self.root = tk.Tk()
        self.root.title("Fly-In Simulator Pro Edition 2.0")

        # Dimensions and Resizing
        window_width = 1400
        window_height = 900
        self.root.geometry(f'{window_width}x{window_height}')
        self.root.minsize(1024, 768)
        self.root.configure(bg="#0B1120")  # Deep midnight blue

        # Minimalist Elegant Theme
        self.theme = {
            "bg": "#0f111a",
            "header_bg": "#141724",
            "card_bg": "#1f2233",
            "border": "#2b2f42",
            "text": "#e0e2ed",
            "subtext": "#878a9c",
            "line": "#2b2f42",
            "drone_waiting": "#ffb86c",
            "drone_flight": "#8be9fd",
            "drone_arrived": "#50fa7b",
            "btn_bg": "#2b2f42",
            "btn_hover": "#44475a"
        }

        # --- TOP DASHBOARD PANEL ---
        self.panel = tk.Frame(
            self.root, bg=self.theme["header_bg"], height=80
        )
        self.panel.pack(fill=tk.X, side=tk.TOP)
        self.panel.pack_propagate(False)

        # Subtle Separator
        tk.Frame(
            self.root, bg=self.theme["border"], height=1
        ).pack(fill=tk.X, side=tk.TOP)

        # -> LEFT: Logo & Branding
        logo_frame = tk.Frame(self.panel, bg=self.theme["header_bg"])
        logo_frame.pack(side=tk.LEFT, padx=30, fill=tk.Y, pady=25)
        tk.Label(
            logo_frame,
            text="FLY IN",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme["header_bg"],
            fg=self.theme["text"],
        ).pack(side=tk.LEFT)

        # -> RIGHT: Controls
        ctrl_frame = tk.Frame(self.panel, bg=self.theme["header_bg"])
        ctrl_frame.pack(side=tk.RIGHT, padx=30, fill=tk.Y, pady=15)

        # -> CENTER: Telemetry / Stats Cards
        stats_frame = tk.Frame(
            self.panel, bg=self.theme["card_bg"], padx=5, pady=2
        )
        stats_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Separator config for stats
        def add_stat(
            parent: tk.Misc, title: str, color: str = "white"
        ) -> tk.StringVar:
            var = tk.StringVar(value="0")
            col = tk.Frame(parent, bg=self.theme["card_bg"])
            col.pack(side=tk.LEFT, padx=5)
            tk.Label(
                col,
                text=title.upper(),
                font=("Segoe UI", 7, "bold"),
                bg=self.theme["card_bg"],
                fg=self.theme["subtext"],
            ).pack()
            tk.Label(
                col,
                textvariable=var,
                font=("Segoe UI", 13, "bold"),
                bg=self.theme["card_bg"],
                fg=color,
            ).pack()
            return var

        self.var_turn = add_stat(stats_frame, "Turn", self.theme["text"])
        tk.Frame(
            stats_frame, width=1, bg=self.theme["border"]
        ).pack(side=tk.LEFT, fill=tk.Y, pady=5)
        self.var_moves = add_stat(stats_frame, "Moves", "#facc15")
        tk.Frame(
            stats_frame, width=1, bg=self.theme["border"]
        ).pack(side=tk.LEFT, fill=tk.Y, pady=5)
        self.var_wait = add_stat(
            stats_frame, "Waiting", self.theme["drone_waiting"]
        )
        self.var_flight = add_stat(
            stats_frame, "In Flight", self.theme["drone_flight"]
        )
        self.var_arriv = add_stat(
            stats_frame, "Arrived", self.theme["drone_arrived"]
        )

        # Speed Control (Minimalist Scale)
        speed_frame = tk.Frame(ctrl_frame, bg=self.theme["header_bg"])
        speed_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(
            speed_frame,
            text="SPEED CAP",
            font=("Segoe UI", 8, "bold"),
            bg=self.theme["header_bg"],
            fg=self.theme["subtext"],
        ).pack()
        self.speed_slider = tk.Scale(
            speed_frame,
            from_=60,
            to=2,
            orient=tk.HORIZONTAL,
            bg=self.theme["header_bg"],
            fg=self.theme["text"],
            highlightthickness=0,
            showvalue=False,
            length=100,
            troughcolor=self.theme["card_bg"],
            width=8,
            bd=0,
            sliderrelief="flat",
        )
        self.speed_slider.set(20)
        self.speed_slider.pack()

        self.btn_play = tk.Button(
            ctrl_frame,
            text="PLAY",
            command=self.cmd_toggle,
            font=("Segoe UI", 10, "bold"),
            fg=self.theme["text"],
            bg=self.theme["btn_bg"],
            activebackground=self.theme["btn_hover"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            width=8,
        )
        self.btn_play.config(
            bg=self.theme["drone_flight"],
            fg="#0B1120",
            activebackground="#0EA5E9",
            activeforeground="#0B1120",
        )
        self.btn_play.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        self.btn_restart = tk.Button(
            ctrl_frame,
            text="RESET",
            command=self.cmd_restart,
            font=("Segoe UI", 10, "bold"),
            fg=self.theme["text"],
            bg=self.theme["btn_bg"],
            activebackground=self.theme["btn_hover"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            width=8,
        )
        self.btn_restart.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # --- CANVAS SECTION ---
        self.canvas_frame = tk.Frame(self.root, bg=self.theme["bg"])
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(
            self.canvas_frame, bg=self.theme["bg"], highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        self.canvas_width = window_width
        self.canvas_height = window_height - 80
        self.padding = 60
        self.node_radius = 35
        self.drone_radius = 8
        self.drone_shapes: Dict[int, Tuple[int, int]] = {}
        self.prev_positions: Dict[int, str] = {}
        self.connector_positions: Dict[int, Tuple[float, float]] = {}
        self.min_x: int = 0
        self.min_y: int = 0
        self.scale_x: float = 1.0
        self.scale_y: float = 1.0
        self.resize_timer: Optional[str] = None

        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event: "tk.Event[tk.Canvas]") -> None:
        self.canvas_width = event.width
        self.canvas_height = event.height
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        self.resize_timer = self.root.after(100, self.setup_from_graph)

    def setup_from_graph(self) -> None:
        self.canvas.delete("all")
        self.drone_shapes = {}
        self.connector_positions = {}
        self.prev_positions = {
            d.id: d.current_zone for d in self.sim.drones
        }

        xs = [z.x for z in self.sim.graph.zones.values()]
        ys = [z.y for z in self.sim.graph.zones.values()]
        self.min_x = min(xs, default=0)
        self.min_y = min(ys, default=0)
        span_x = max(xs, default=1) - self.min_x or 1
        span_y = max(ys, default=1) - self.min_y or 1

        self.scale_x = (self.canvas_width - 2 * self.padding) / span_x
        self.scale_y = (self.canvas_height - 2 * self.padding) / span_y

        # Connections
        for conn in self.sim.graph.connections:
            z1 = self.sim.graph.zones[conn.zone1]
            z2 = self.sim.graph.zones[conn.zone2]
            x1, y1 = self.get_coords(z1.x, z1.y)
            x2, y2 = self.get_coords(z2.x, z2.y)
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=self.theme["bg"], width=8, capstyle=tk.ROUND,
            )
            self.canvas.create_line(
                x1, y1, x2, y2, fill=self.theme["line"], width=2
            )

        # Hubs
        for zone in self.sim.graph.zones.values():
            x, y = self.get_coords(zone.x, zone.y)

            color_map = {
                "green": ("#064E3B", "#10B981"),
                "red": ("#7F1D1D", "#EF4444"),
                "blue": ("#1E3A8A", "#3B82F6"),
                "orange": ("#78350F", "#F59E0B"),
                "cyan": ("#312E81", "#8B5CF6"),
                "yellow": ("#713F12", "#FBBF24"),
                "purple": ("#4C1D95", "#A78BFA"),
                "black": ("#0F172A", "#475569"),
            }

            base_col, outline_col = ("#1E293B", "#475569")

            if zone.color in color_map:
                base_col, outline_col = color_map[zone.color]
            elif zone.zone_type == "priority":
                base_col, outline_col = ("#312E81", "#8B5CF6")
            elif zone.zone_type == "restricted":
                base_col, outline_col = ("#7F1D1D", "#EF4444")

            self.canvas.create_oval(
                x - self.node_radius,
                y - self.node_radius,
                x + self.node_radius,
                y + self.node_radius,
                fill=base_col,
                outline=outline_col,
                width=2,
            )

            cap = "inf" if zone.max_drones > 900 else str(zone.max_drones)
            self.canvas.create_text(
                x, y - self.node_radius - 14,
                text=zone.name, fill=self.theme["text"],
                font=("Segoe UI", 9, "bold"),
            )
            self.canvas.create_text(
                x, y + self.node_radius + 14,
                text=f"Max: {cap}", fill=self.theme["subtext"],
                font=("Segoe UI", 8),
            )

        self.render(self.sim.turn, initial=True)
        if not hasattr(self, '_started'):
            self._started = True
            if not self.sim.is_running:
                self.cmd_toggle()

    def get_coords(self, x: int, y: int) -> Tuple[float, float]:
        return (
            self.padding + (x - self.min_x) * self.scale_x,
            self.padding + (y - self.min_y) * self.scale_y,
        )

    def get_offsets(
        self, drones_list: List[Any]
    ) -> Dict[int, Tuple[float, float]]:
        opts: Dict[int, Tuple[float, float]] = {}
        n = len(drones_list)
        if n == 0:
            return opts
        if n == 1:
            return {drones_list[0].id: (0.0, 0.0)}

        radius = min(max(8, n * 2), self.node_radius - 6)
        for i, d in enumerate(drones_list):
            angle = i * (math.pi * 2 / n) - (math.pi / 2)
            opts[d.id] = (
                math.cos(angle) * radius,
                math.sin(angle) * radius,
            )
        return opts

    def cmd_toggle(self) -> None:
        self.sim.is_running = not self.sim.is_running
        if self.sim.is_running:
            self.btn_play.config(
                text="PAUSE",
                bg=self.theme["btn_bg"],
                fg=self.theme["text"],
            )
            self.pulse()
        else:
            self.btn_play.config(
                text="PLAY",
                bg=self.theme["drone_flight"],
                fg="#0B1120",
            )

    def cmd_restart(self) -> None:
        self.sim.is_running = False
        self.sim.reset()

    def pulse(self) -> None:
        if not self.sim.is_running:
            return
        self.sim.step()
        if self.sim.is_running:
            self.root.after(10, self.pulse)

    def render(self, turn: int, initial: bool = False) -> None:
        c_tot = len(self.sim.drones)
        c_arr = sum(1 for d in self.sim.drones if d.status == "arrived")
        c_fly = sum(1 for d in self.sim.drones if d.status == "in_flight")
        c_wat = sum(1 for d in self.sim.drones if d.status == "waiting")
        tot_moves = sum(d.moves for d in self.sim.drones)

        self.var_turn.set(f"{turn}")
        self.var_moves.set(f"{tot_moves}")
        self.var_arriv.set(f"{c_arr} / {c_tot}")
        self.var_flight.set(f"{c_fly}")
        self.var_wait.set(f"{c_wat}")

        starts: Dict[str, List[Any]] = {z: [] for z in self.sim.graph.zones}
        ends: Dict[str, List[Any]] = {z: [] for z in self.sim.graph.zones}
        for d in self.sim.drones:
            starts[self.prev_positions.get(d.id, d.current_zone)].append(d)
            ends[d.current_zone].append(d)

        start_o: Dict[int, Tuple[float, float]] = {}
        end_o: Dict[int, Tuple[float, float]] = {}
        for z in self.sim.graph.zones:
            start_o.update(self.get_offsets(starts[z]))
            end_o.update(self.get_offsets(ends[z]))

        frames = 1 if initial else max(1, int(self.speed_slider.get()))

        for f in range(frames + 1):
            t = f / frames
            t = t * t * (3 - 2 * t)

            for d in self.sim.drones:
                sz = self.prev_positions.get(d.id, d.current_zone)
                ez = d.current_zone
                sx, sy = self.get_coords(
                    self.sim.graph.zones[sz].x,
                    self.sim.graph.zones[sz].y,
                )
                ex, ey = self.get_coords(
                    self.sim.graph.zones[ez].x,
                    self.sim.graph.zones[ez].y,
                )

                sox, soy = start_o.get(d.id, (0.0, 0.0))
                eox, eoy = end_o.get(d.id, (0.0, 0.0))

                full_sx = sx + sox
                full_sy = sy + soy
                full_ex = ex + eox
                full_ey = ey + eoy

                dest_zone_obj = self.sim.graph.zones.get(ez)
                is_restricted_dest = (
                    dest_zone_obj is not None
                    and dest_zone_obj.zone_type == "restricted"
                )

                if sz != ez and is_restricted_dest and d.wait_turns > 0:
                    # Phase 1: entering restricted zone — animate to connector and stop
                    mid_x = (full_sx + full_ex) / 2
                    mid_y = (full_sy + full_ey) / 2
                    self.connector_positions[d.id] = (mid_x, mid_y)
                    cx = full_sx * (1 - t) + mid_x * t
                    cy = full_sy * (1 - t) + mid_y * t
                elif sz == ez and d.id in self.connector_positions:
                    # Phase 2: depart from connector to restricted zone node
                    con_x, con_y = self.connector_positions[d.id]
                    cx = con_x * (1 - t) + full_ex * t
                    cy = con_y * (1 - t) + full_ey * t
                else:
                    cx = full_sx * (1 - t) + full_ex * t
                    cy = full_sy * (1 - t) + full_ey * t

                col = self.theme["drone_waiting"]
                if d.status == "in_flight":
                    col = self.theme["drone_flight"]
                elif d.status == "arrived":
                    col = self.theme["drone_arrived"]

                if d.id not in self.drone_shapes:
                    g = self.canvas.create_oval(
                        0, 0, 0, 0,
                        fill="", outline=col, width=1,
                    )
                    c = self.canvas.create_oval(
                        0, 0, 0, 0,
                        fill=col, outline=self.theme["bg"], width=1,
                    )
                    self.drone_shapes[d.id] = (c, g)

                c, g = self.drone_shapes[d.id]
                self.canvas.coords(
                    g,
                    cx - self.drone_radius - 2,
                    cy - self.drone_radius - 2,
                    cx + self.drone_radius + 2,
                    cy + self.drone_radius + 2,
                )
                self.canvas.itemconfig(g, outline=col)
                self.canvas.coords(
                    c,
                    cx - self.drone_radius,
                    cy - self.drone_radius,
                    cx + self.drone_radius,
                    cy + self.drone_radius,
                )
                self.canvas.itemconfig(c, fill=col)

            self.root.update()
            if not initial:
                self.root.after(10)  # type: ignore[call-arg]

        for d in self.sim.drones:
            self.prev_positions[d.id] = d.current_zone
            # Clear connector after phase 2 completes
            if d.id in self.connector_positions and d.wait_turns == 0:
                dest_zone_obj = self.sim.graph.zones.get(d.current_zone)
                if dest_zone_obj and dest_zone_obj.zone_type == "restricted":
                    del self.connector_positions[d.id]
