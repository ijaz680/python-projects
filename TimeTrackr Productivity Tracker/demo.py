from tracker import Tracker


def run_demo():
    t = Tracker(interval=1.0, by_title=False)
    print("Running demo tracking for 15 seconds...")
    t.run_for(15)
    t.export_csv("demo_report.csv")
    t.plot("demo_plot.png")
    print("Demo complete. Files: demo_report.csv, demo_plot.png")


if __name__ == "__main__":
    run_demo()
