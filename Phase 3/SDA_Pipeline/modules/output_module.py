
import queue
from collections import deque

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

_BG_DARK    = "#0d1117"
_BG_PANEL   = "#161b22"
_FG_TEXT    = "#e6edf3"
_GRID_COLOR = "#21262d"
_GREEN      = "#2ea043"
_YELLOW     = "#d29922"
_RED        = "#da3633"
_BLUE_LINE  = "#58a6ff"
_ORANGE_LINE = "#f0883e"


class Dashboard:
    def __init__(self, config: dict, processed_queue, telemetry):
        self._config = config
        self._processed_queue = processed_queue
        self._telemetry = telemetry
        self._telemetry.subscribe(self)

        self._max_size: int = config["pipeline_dynamics"]["stream_queue_max_size"]
        viz = config["visualizations"]
        self._telem_cfg = viz["telemetry"]
        self._charts_cfg = viz["data_charts"]

        charts_by_type = {c.get("type"): c for c in self._charts_cfg}
        values_chart = charts_by_type.get("real_time_line_graph_values", {})
        avg_chart = charts_by_type.get("real_time_line_graph_average", {})
        stateless = config.get("processing", {}).get("stateless_tasks", {})
        stateful = config.get("processing", {}).get("stateful_tasks", {})
        self._entity_field = stateful.get("group_by_field", "entity_name")
        self._x_field = values_chart.get("x_axis") or avg_chart.get("x_axis") or "time_period"
        self._value_field = stateless.get("value_field") or values_chart.get("y_axis") or "metric_value"
        self._computed_field = stateful.get("output_field") or avg_chart.get("y_axis") or "computed_metric"

        self._x_vals: dict = {}
        self._y_vals: dict = {}
        self._avg_vals: dict = {}
        self._buf_len = 300

        self._telem_state: dict = {
            "raw_queue_size": 0,
            "intermediate_queue_size": 0,
            "processed_queue_size": 0,
            "max_size": self._max_size,
        }
        self._finished = False
        self._total_received = 0
        self._build_figure()

    #Observer interface 
    def update(self, state: dict) -> None:
        self._telem_state = state

    #figure setup 
    def _build_figure(self) -> None:
        plt.style.use("dark_background")
        self._fig = plt.figure(figsize=(15, 9), facecolor=_BG_DARK)
        self._fig.canvas.manager.set_window_title(
            "Generic Concurrent Real-Time Pipeline — Live Dashboard"
        )
        gs = GridSpec(3, 1, figure=self._fig,
                      height_ratios=[1, 2, 2], hspace=0.55)
        self._ax_telem = self._fig.add_subplot(gs[0])
        self._ax_line1 = self._fig.add_subplot(gs[1])
        self._ax_line2 = self._fig.add_subplot(gs[2])
        for ax in (self._ax_telem, self._ax_line1, self._ax_line2):
            ax.set_facecolor(_BG_PANEL)
            ax.tick_params(colors=_FG_TEXT, labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(_GRID_COLOR)
            ax.grid(color=_GRID_COLOR, linewidth=0.5)
        self._fig.suptitle(
            "⚙  Generic Concurrent Real-Time Pipeline — Live Dashboard",
            color=_FG_TEXT, fontsize=13, fontweight="bold", y=0.98,
        )

    #animation callback
    def _animate(self, _frame) -> None:
        while True:
            try:
                packet = self._processed_queue.get_nowait()
                if packet is None:
                    self._finished = True
                    break
                entity = packet.get(self._entity_field, "__stream__")
                if entity not in self._x_vals:
                    self._x_vals[entity] = deque(maxlen=self._buf_len)
                    self._y_vals[entity] = deque(maxlen=self._buf_len)
                    self._avg_vals[entity] = deque(maxlen=self._buf_len)
                x_val = packet.get(self._x_field, self._total_received)
                self._x_vals[entity].append(x_val)
                self._y_vals[entity].append(packet.get(self._value_field))
                self._avg_vals[entity].append(packet.get(self._computed_field))
                self._total_received += 1
            except queue.Empty:
                break

        self._telemetry.poll_and_notify()
        self._draw_telemetry()
        self._draw_line_charts()

        if self._finished:
            self._ax_telem.set_title(
                f"✅  Pipeline complete — {self._total_received} packets processed",
                color=_GREEN, fontsize=10)

    #Panel renderers
    def _queue_color(self, size, max_s) -> str:
        if max_s == 0:
            return _GREEN
        r = size / max_s
        return _GREEN if r < 0.50 else (_YELLOW if r < 0.80 else _RED)

    def _draw_telemetry(self) -> None:
        ax = self._ax_telem
        ax.clear()
        ax.set_facecolor(_BG_PANEL)
        ax.set_xlim(0, 1)
        ax.set_title(
            f"Pipeline Telemetry — Queue Backpressure  "
            f"(packets received by dashboard: {self._total_received})",
            color=_FG_TEXT, fontsize=9)
        ax.axis("off")

        s = self._telem_state
        max_s = s["max_size"]
        streams = []
        if self._telem_cfg.get("show_raw_stream"):
            streams.append(("Raw Stream\n(Input → Core)", s["raw_queue_size"], max_s))
        if self._telem_cfg.get("show_intermediate_stream"):
            streams.append(("Intermediate\n(Core → Aggregator)", s["intermediate_queue_size"], max_s))
        if self._telem_cfg.get("show_processed_stream"):
            streams.append(("Processed\n(Aggregator → Output)", s["processed_queue_size"], max_s))

        n = len(streams)
        if not n:
            return

        slot_w = 1.0 / n
        bar_h, bar_y = 0.30, 0.50

        for i, (label, size, max_size) in enumerate(streams):
            x0 = i * slot_w + 0.02
            bw = slot_w - 0.04
            ratio = min(size / max_size, 1.0) if max_size else 0
            color = self._queue_color(size, max_size)

            ax.add_patch(FancyBboxPatch(
                (x0, bar_y), bw, bar_h,
                boxstyle="round,pad=0.01",
                facecolor="#21262d", edgecolor="#30363d", linewidth=0.8,
                transform=ax.transAxes))

            if ratio > 0:
                ax.add_patch(FancyBboxPatch(
                    (x0, bar_y), bw * ratio, bar_h,
                    boxstyle="round,pad=0.01",
                    facecolor=color, alpha=0.85, edgecolor="none",
                    transform=ax.transAxes))

            ax.text(x0 + bw / 2, bar_y + bar_h + 0.10, label,
                    ha="center", va="bottom", color=_FG_TEXT, fontsize=8,
                    transform=ax.transAxes)
            status = ("● FLOWING" if color == _GREEN
                      else ("⚠ FILLING" if color == _YELLOW else "🔴 BACKPRESSURE"))
            ax.text(x0 + bw / 2, bar_y + bar_h / 2,
                    f"{size} / {max_size}  {status}",
                    ha="center", va="center", color="white",
                    fontsize=7.5, fontweight="bold", transform=ax.transAxes)

    def _draw_line_charts(self) -> None:
        chart_map = {
            "real_time_line_graph_values":  (self._ax_line1, self._y_vals,   _BLUE_LINE),
            "real_time_line_graph_average": (self._ax_line2, self._avg_vals, _ORANGE_LINE),
        }
        for cfg in self._charts_cfg:
            if cfg["type"] not in chart_map:
                continue
            ax, y_store, color = chart_map[cfg["type"]]
            ax.clear()
            ax.set_facecolor(_BG_PANEL)
            ax.set_title(cfg["title"], color=_FG_TEXT, fontsize=10)
            ax.set_xlabel(cfg["x_axis"], color=_FG_TEXT, fontsize=8)
            ax.set_ylabel(cfg["y_axis"], color=_FG_TEXT, fontsize=8)
            ax.tick_params(colors=_FG_TEXT, labelsize=7)
            ax.grid(color=_GRID_COLOR, linewidth=0.4, alpha=0.7)
            for spine in ax.spines.values():
                spine.set_edgecolor(_GRID_COLOR)

            if not self._x_vals:
                ax.text(0.5, 0.5, "Waiting for data…",
                        ha="center", va="center", color="#8b949e",
                        fontsize=10, transform=ax.transAxes)
                continue

            for entity, x_deq in self._x_vals.items():
                y_deq = y_store.get(entity, deque())
                if len(x_deq) >= 2:
                    ax.plot(list(x_deq), list(y_deq), color=color,
                            linewidth=1.2, label=entity)

            if self._x_vals:
                ax.legend(loc="upper left", fontsize=7,
                           facecolor=_BG_PANEL, edgecolor=_GRID_COLOR,
                           labelcolor=_FG_TEXT)

    #entry point
    def run(self) -> None:
        self._anim = animation.FuncAnimation(
            self._fig, self._animate, interval=200, cache_frame_data=False)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
