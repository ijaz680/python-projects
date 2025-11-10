import time
import threading
import csv
import datetime

import psutil
import win32gui
import win32process


class Tracker:
    """Simple Windows active-window tracker.

    Polls the foreground window at a regular interval and accumulates
    time spent per process (or per process+title when by_title=True).
    """

    def __init__(self, interval: float = 1.0, by_title: bool = False):
        self.interval = float(interval)
        self.by_title = bool(by_title)
        self._running = False
        self.data = {}  # mapping: key -> seconds
        self._lock = threading.Lock()

    def _get_active_app(self) -> str:
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            name = proc.name()
            title = win32gui.GetWindowText(hwnd) or ""
            if self.by_title:
                key = f"{name} - {title}"
            else:
                key = name
            return key
        except Exception:
            return "Unknown"

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if hasattr(self, "_thread"):
            self._thread.join(timeout=self.interval * 2)

    def _run_loop(self) -> None:
        last_time = time.time()
        last_key = self._get_active_app()
        while self._running:
            time.sleep(self.interval)
            now = time.time()
            elapsed = now - last_time
            key = self._get_active_app()
            with self._lock:
                self.data[last_key] = self.data.get(last_key, 0.0) + elapsed
            last_key = key
            last_time = now

    def run_for(self, seconds: float) -> None:
        """Run tracking for a fixed number of seconds (blocking)."""
        self.start()
        time.sleep(seconds)
        self.stop()

    def export_csv(self, path: str) -> None:
        """Export aggregated results to CSV.

        Columns: app, seconds, hh:mm:ss, percent
        """
        with self._lock:
            items = sorted(self.data.items(), key=lambda x: x[1], reverse=True)
        total = sum(v for _, v in items) or 1.0
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["app", "seconds", "hh:mm:ss", "percent"])
            for k, v in items:
                writer.writerow([k, round(v, 2), str(datetime.timedelta(seconds=int(v))), round(100 * v / total, 2)])

    def plot(self, path: str = None, top_n: int = 10) -> None:
        """Create a horizontal bar chart of time spent using matplotlib.

        If `path` is provided the plot is saved to that filename, otherwise
        it will be shown interactively.
        """
        import matplotlib.pyplot as plt

        with self._lock:
            items = sorted(self.data.items(), key=lambda x: x[1], reverse=True)[:top_n]

        if not items:
            print("No data to plot.")
            return

        apps = [i[0] for i in items]
        secs = [i[1] for i in items]

        fig, ax = plt.subplots(figsize=(8, max(3, len(apps) * 0.5)))
        ax.barh(apps[::-1], [s / 3600 for s in secs[::-1]], color="#4C72B0")
        ax.set_xlabel("Hours")
        ax.set_title("Time spent per app")
        plt.tight_layout()

        if path:
            plt.savefig(path)
            print(f"Saved plot to {path}")
        else:
            plt.show()

        plt.close(fig)


if __name__ == "__main__":
    print("TimeTrackr Tracker module. Use the CLI or import Tracker in your code.")
