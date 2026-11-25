"""
COMPROG 1 - PYTHON LAB 8: DATA VISUALIZATION
Section E: Additional Exercises 1-3
Student: PENA, MARY GRACE D.
Student ID: TUPM-26-1140

Place the Spotify Top 1000 Tracks CSV in the same folder as this script.
Expected filename: spotify_top_1000_tracks.csv
The script also searches for another .csv file in the same folder if the
expected filename is not found.
"""

from pathlib import Path
import re
import sys

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.ticker import MaxNLocator


# ============================================================
# STUDENT-SPECIFIC PARAMETERS - EDIT THESE BEFORE RUNNING
# ============================================================
STUDENT_NAME = "PENA"                 # Replace with complete student name
STUDENT_ID = "TUPM-26-1140"        # Enter complete student ID

COLOR_BAR = "#315C8C"                 # Exercise 1 bar color
COLOR_LINE = "#D97706"                # Exercise 2 line color
CMAP_COLOR = "viridis"                # Exercise 3 density colormap

CSV_FILE = "spotify_top_1000_tracks.csv"
OUTPUT_DIR = Path("Lab8_Outputs")


# ============================================================
# GENERAL FUNCTIONS
# ============================================================
def normalize_column_name(name):
    """Normalize column names to lowercase underscore format."""
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def find_dataset():
    """Find the assigned Spotify CSV file beside this Python script."""
    script_folder = Path(__file__).resolve().parent
    expected = script_folder / CSV_FILE

    if expected.exists():
        return expected

    csv_files = [
        file for file in script_folder.glob("*.csv")
        if file.name.lower() != "top_10_longest_tracks.csv"
    ]

    if len(csv_files) == 1:
        print(f"Using CSV file found in folder: {csv_files[0].name}")
        return csv_files[0]

    if not csv_files:
        raise FileNotFoundError(
            f"Dataset not found. Place the Spotify CSV beside this script "
            f"and name it '{CSV_FILE}'."
        )

    names = ", ".join(file.name for file in csv_files)
    raise FileNotFoundError(
        "More than one CSV file was found. Set CSV_FILE to the exact "
        f"Spotify dataset filename. Found: {names}"
    )


def load_and_prepare_data():
    """Load the CSV and prepare the required columns."""
    csv_path = find_dataset()
    df = pd.read_csv(csv_path)
    df.columns = [normalize_column_name(col) for col in df.columns]

    # Support common alternative column names.
    aliases = {
        "track_name": ["track_name", "track", "name", "song_name"],
        "artist": ["artist", "artists", "artist_name"],
        "duration_min": ["duration_min", "duration_minutes"],
        "duration_ms": ["duration_ms", "duration_milliseconds"],
        "popularity": ["popularity"],
        "year": ["year", "release_year"],
        "release_date": ["release_date", "released", "release"],
    }

    def locate(possible_names):
        for candidate in possible_names:
            if candidate in df.columns:
                return candidate
        return None

    track_col = locate(aliases["track_name"])
    artist_col = locate(aliases["artist"])
    duration_col = locate(aliases["duration_min"])
    duration_ms_col = locate(aliases["duration_ms"])
    popularity_col = locate(aliases["popularity"])
    year_col = locate(aliases["year"])
    release_date_col = locate(aliases["release_date"])

    missing = []
    if track_col is None:
        missing.append("track_name")
    if artist_col is None:
        missing.append("artist")
    if duration_col is None and duration_ms_col is None:
        missing.append("duration_min or duration_ms")
    if popularity_col is None:
        missing.append("popularity")
    if year_col is None and release_date_col is None:
        missing.append("year or release_date")

    if missing:
        raise ValueError(
            "The dataset is missing required column(s): "
            + ", ".join(missing)
            + f"\nAvailable columns: {list(df.columns)}"
        )

    prepared = pd.DataFrame()
    prepared["track_name"] = df[track_col].astype("string").str.strip()
    prepared["artist"] = df[artist_col].astype("string").str.strip()

    if duration_col is not None:
        prepared["duration_min"] = pd.to_numeric(
            df[duration_col], errors="coerce"
        )
    else:
        prepared["duration_min"] = (
            pd.to_numeric(df[duration_ms_col], errors="coerce") / 60000
        )

    prepared["popularity"] = pd.to_numeric(
        df[popularity_col], errors="coerce"
    )

    if year_col is not None:
        prepared["year"] = pd.to_numeric(df[year_col], errors="coerce")
    else:
        prepared["year"] = pd.to_datetime(
            df[release_date_col], errors="coerce"
        ).dt.year

    prepared = prepared.dropna(
        subset=[
            "track_name", "artist", "duration_min",
            "popularity", "year"
        ]
    ).copy()

    prepared = prepared[
        (prepared["track_name"] != "")
        & (prepared["artist"] != "")
        & (prepared["duration_min"] > 0)
        & (prepared["year"] > 0)
    ].copy()

    prepared["year"] = prepared["year"].astype(int)

    if prepared.empty:
        raise ValueError("No valid records remain after cleaning the dataset.")

    return prepared, csv_path


def personalized_title(title):
    return f"{title}\nStudent: {STUDENT_NAME} | ID: {STUDENT_ID}"


# ============================================================
# EXERCISE 1: IDENTIFY LONGEST TRACKS
# ============================================================
def exercise_1(df):
    print("\n" + "=" * 72)
    print("EXERCISE 1 - IDENTIFY LONGEST TRACKS")
    print("=" * 72)

    top_10 = (
        df.sort_values("duration_min", ascending=False)
        .head(10)
        .copy()
        .reset_index(drop=True)
    )

    table = top_10[["track_name", "artist", "duration_min"]].copy()
    table["duration_min"] = table["duration_min"].round(2)

    print("\nTOP 10 LONGEST TRACKS")
    print(table.to_string(index=False))

    table.to_csv(
        OUTPUT_DIR / "top_10_longest_tracks.csv",
        index=False
    )

    # Horizontal bar chart: track names on y-axis, durations on x-axis.
    plot_data = top_10.sort_values("duration_min", ascending=True)

    plt.figure(figsize=(12, 8))
    plt.barh(
        plot_data["track_name"],
        plot_data["duration_min"],
        color=COLOR_BAR
    )
    plt.title(personalized_title("Top 10 Longest Spotify Tracks"))
    plt.xlabel("Duration (minutes)")
    plt.ylabel("Track Name")
    plt.grid(axis="x", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "exercise1_top_10_longest_tracks.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()
    plt.close()


# ============================================================
# EXERCISE 2: SONG RELEASE TREND
# ============================================================
def exercise_2(df):
    print("\n" + "=" * 72)
    print("EXERCISE 2 - SONG RELEASE TREND")
    print("=" * 72)

    yearly = (
        df.groupby("year")
        .size()
        .sort_index()
        .rename("yearly_releases")
        .reset_index()
    )
    yearly["cumulative_releases"] = yearly["yearly_releases"].cumsum()

    print("\nSONG RELEASES PER YEAR AND CUMULATIVE TOTAL")
    print(yearly.to_string(index=False))

    yearly.to_csv(
        OUTPUT_DIR / "song_release_trend.csv",
        index=False
    )

    fig, ax1 = plt.subplots(figsize=(13, 7))

    ax1.bar(
        yearly["year"],
        yearly["yearly_releases"],
        color=COLOR_BAR,
        alpha=0.85,
        label="Songs released per year"
    )
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of Songs Released")
    ax1.set_title(personalized_title("Spotify Song Release Trend"))
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(
        yearly["year"],
        yearly["cumulative_releases"],
        color=COLOR_LINE,
        marker="o",
        linewidth=2.5,
        label="Cumulative song releases"
    )
    ax2.set_ylabel("Cumulative Number of Songs")

    bars, bar_labels = ax1.get_legend_handles_labels()
    lines, line_labels = ax2.get_legend_handles_labels()
    ax1.legend(
        bars + lines,
        bar_labels + line_labels,
        loc="upper left"
    )

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "exercise2_song_release_trend.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()
    plt.close(fig)


# ============================================================
# EXERCISE 3: ANIMATED DENSITY MAP OF DURATION VS POPULARITY
# ============================================================
def exercise_3(df):
    print("\n" + "=" * 72)
    print("EXERCISE 3 - ANIMATED DENSITY MAP")
    print("=" * 72)

    years = sorted(df["year"].unique())

    if len(years) < 2:
        raise ValueError(
            "At least two different years are needed for the animated "
            "density map."
        )

    # Use common axis limits so each frame can be compared fairly.
    x_min = max(0, df["duration_min"].min() - 1)
    x_max = df["duration_min"].max() + 1
    y_min = max(0, df["popularity"].min() - 5)
    y_max = min(100, df["popularity"].max() + 5)

    fig, ax = plt.subplots(figsize=(11, 7))

    def update(frame_index):
        ax.clear()
        year = years[frame_index]
        yearly_data = df[df["year"] <= year]

        if len(yearly_data) >= 3:
            hb = ax.hexbin(
                yearly_data["duration_min"],
                yearly_data["popularity"],
                gridsize=25,
                cmap=CMAP_COLOR,
                mincnt=1,
                extent=(x_min, x_max, y_min, y_max)
            )
        else:
            hb = ax.hexbin(
                yearly_data["duration_min"],
                yearly_data["popularity"],
                gridsize=10,
                cmap=CMAP_COLOR,
                mincnt=1,
                extent=(x_min, x_max, y_min, y_max)
            )

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel("Duration (minutes)")
        ax.set_ylabel("Popularity")
        ax.set_title(
            personalized_title(
                f"Animated Density Map: Duration vs Popularity\n"
                f"Songs released up to {year}"
            )
        )
        ax.grid(alpha=0.2)

        return (hb,)

    animation = FuncAnimation(
        fig,
        update,
        frames=len(years),
        interval=800,
        repeat=True,
        blit=False
    )

    gif_path = OUTPUT_DIR / "exercise3_animated_density_map.gif"
    animation.save(
        gif_path,
        writer=PillowWriter(fps=1.25),
        dpi=120
    )

    # Also save a static final-year image for easy viewing/submission.
    update(len(years) - 1)
    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "exercise3_density_map_final_year.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()
    plt.close(fig)

    print(f"Animated GIF saved as: {gif_path}")


# ============================================================
# MAIN PROGRAM
# ============================================================
def main():
    if STUDENT_NAME == "PENA" or STUDENT_ID == "REPLACE_WITH_ID":
        print(
            "REMINDER: Edit STUDENT_NAME and STUDENT_ID at the top "
            "of this script before submitting."
        )

    OUTPUT_DIR.mkdir(exist_ok=True)

    try:
        df, csv_path = load_and_prepare_data()

        print("=" * 72)
        print("COMPROG 1 - PYTHON LAB 8: DATA VISUALIZATION")
        print(f"Student: {STUDENT_NAME}")
        print(f"Student ID: {STUDENT_ID}")
        print(f"Dataset: {csv_path.name}")
        print(f"Valid records: {len(df)}")
        print("=" * 72)

        exercise_1(df)
        exercise_2(df)
        exercise_3(df)

        print("\n" + "=" * 72)
        print("ALL THREE ADDITIONAL EXERCISES COMPLETED.")
        print(f"Check the output files in: {OUTPUT_DIR.resolve()}")
        print("=" * 72)

    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
