import argparse
from tracker import Tracker
import os


def main():
    parser = argparse.ArgumentParser(prog="timetrackr", description="Track active window usage on Windows")
    parser.add_argument("--duration", "-d", type=float, default=60, help="Duration in seconds to run the tracker")
    parser.add_argument("--interval", "-i", type=float, default=1.0, help="Polling interval in seconds")
    parser.add_argument("--by-title", action="store_true", help="Aggregate by window title as well as process name")
    parser.add_argument("--csv", type=str, help="Path to output CSV file")
    parser.add_argument("--plot", type=str, help="Path to save matplotlib plot image (png)")

    args = parser.parse_args()

    t = Tracker(interval=args.interval, by_title=args.by_title)
    print(f"Running tracker for {args.duration} seconds (interval={args.interval})...")
    t.run_for(args.duration)

    out_csv = args.csv or os.path.join(os.getcwd(), "timetrackr_report.csv")
    t.export_csv(out_csv)
    print(f"Exported CSV to {out_csv}")

    if args.plot:
        t.plot(args.plot)


if __name__ == "__main__":
    main()
