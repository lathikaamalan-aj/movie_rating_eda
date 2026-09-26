from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# ============================================================
# 1. LOAD DATASET
# ============================================================

# Your CSV file should be in the same folder as app.py
# Example:
# movie-rating-eda/
# ├── app.py
# ├── movie_data.csv
# └── templates/
#     └── dashboard.html

CSV_FILE = "titles_dataset.csv"

df = pd.read_csv(CSV_FILE)


# ============================================================
# 2. CLEAN / PREPARE DATA
# ============================================================

# Remove completely empty rows
df = df.dropna(how="all")

# Make sure column names are correct
df.columns = df.columns.str.strip()

# Convert numeric columns
df["Release_Year"] = pd.to_numeric(
    df["Release_Year"],
    errors="coerce"
)

df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)

# Remove rows where important values are missing
df = df.dropna(
    subset=["Title", "Genre", "Release_Year", "Rating"]
)

# Convert year to integer
df["Release_Year"] = df["Release_Year"].astype(int)


# ============================================================
# 3. BUILD DASHBOARD DATA
# ============================================================

def build_analysis(data):

    # --------------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------------

    summary = {
        "total_movies": int(len(data)),
        "average_rating": round(
            float(data["Rating"].mean()), 2
        ),
        "highest_rating": round(
            float(data["Rating"].max()), 2
        ),
        "lowest_rating": round(
            float(data["Rating"].min()), 2
        )
    }


    # --------------------------------------------------------
    # RATING DISTRIBUTION
    # --------------------------------------------------------

    # Rating range in your dataset is approximately 4.5 - 8.9.
    # Create clean 1-point rating ranges.

    bins = [
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0
    ]

    labels = [
        "4.0-4.9",
        "5.0-5.9",
        "6.0-6.9",
        "7.0-7.9",
        "8.0-8.9",
        "9.0-9.9"
    ]

    rating_groups = pd.cut(
        data["Rating"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    rating_counts = (
        rating_groups
        .value_counts()
        .sort_index()
    )

    rating_distribution = {
        "labels": labels,
        "counts": [
            int(rating_counts.get(label, 0))
            for label in labels
        ]
    }


    # --------------------------------------------------------
    # MOVIES BY GENRE
    # --------------------------------------------------------

    genre_count_series = (
        data["Genre"]
        .value_counts()
        .sort_values(ascending=False)
    )

    genre_counts = {
        "labels": [
            str(x)
            for x in genre_count_series.index
        ],

        "counts": [
            int(x)
            for x in genre_count_series.values
        ]
    }


    # --------------------------------------------------------
    # AVERAGE RATING BY GENRE
    # --------------------------------------------------------

    genre_average_series = (
        data
        .groupby("Genre")["Rating"]
        .mean()
        .sort_values(ascending=False)
    )

    genre_avg_rating = {
        "labels": [
            str(x)
            for x in genre_average_series.index
        ],

        "values": [
            round(float(x), 2)
            for x in genre_average_series.values
        ]
    }


    # --------------------------------------------------------
    # AVERAGE RATING BY RELEASE YEAR
    # --------------------------------------------------------

    yearly_average_series = (
        data
        .groupby("Release_Year")["Rating"]
        .mean()
        .sort_index()
    )

    yearly_avg_rating = {
        "labels": [
            int(x)
            for x in yearly_average_series.index
        ],

        "values": [
            round(float(x), 2)
            for x in yearly_average_series.values
        ]
    }


    # --------------------------------------------------------
    # RATING VS RELEASE YEAR
    # SCATTER PLOT
    # --------------------------------------------------------

    scatter_points = []

    for row in data.itertuples():

        scatter_points.append({
            "x": int(row.Release_Year),
            "y": float(row.Rating),
            "title": str(row.Title)
        })


    # --------------------------------------------------------
    # TOP 10 HIGHEST-RATED MOVIES
    # --------------------------------------------------------

    top10_data = (
        data
        .sort_values(
            by="Rating",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )

    top10 = []

    for index, row in top10_data.iterrows():

        top10.append({
            "rank": int(index + 1),
            "title": str(row["Title"]),
            "genre": str(row["Genre"]),
            "year": int(row["Release_Year"]),
            "rating": float(row["Rating"])
        })


    # --------------------------------------------------------
    # EDA INSIGHTS
    # --------------------------------------------------------

    most_common_genre = (
        genre_count_series.idxmax()
    )

    most_common_genre_count = int(
        genre_count_series.max()
    )

    highest_average_genre = (
        genre_average_series.idxmax()
    )

    highest_average_genre_rating = round(
        float(genre_average_series.max()),
        2
    )

    lowest_average_genre = (
        genre_average_series.idxmin()
    )

    lowest_average_genre_rating = round(
        float(genre_average_series.min()),
        2
    )

    highest_rated_movie = (
        data
        .sort_values(
            by="Rating",
            ascending=False
        )
        .iloc[0]
    )

    highest_year = int(
        yearly_average_series.idxmax()
    )

    highest_year_rating = round(
        float(yearly_average_series.max()),
        2
    )

    lowest_year = int(
        yearly_average_series.idxmin()
    )

    lowest_year_rating = round(
        float(yearly_average_series.min()),
        2
    )

    first_year = int(
        data["Release_Year"].min()
    )

    last_year = int(
        data["Release_Year"].max()
    )


    insights = [

        f"The dataset contains {len(data)} movies "
        f"released between {first_year} and {last_year}.",

        f"The overall average movie rating is "
        f"{summary['average_rating']}.",

        f"Movie ratings range from "
        f"{summary['lowest_rating']} to "
        f"{summary['highest_rating']}.",

        f"{most_common_genre} has the highest number "
        f"of movies in the dataset, with "
        f"{most_common_genre_count} movies.",

        f"{highest_average_genre} has the highest "
        f"average rating among genres, at "
        f"{highest_average_genre_rating}.",

        f"{lowest_average_genre} has the lowest "
        f"average rating among genres, at "
        f"{lowest_average_genre_rating}.",

        f"\"{highest_rated_movie['Title']}\" is the "
        f"highest-rated movie with a rating of "
        f"{highest_rated_movie['Rating']}.",

        f"{highest_year} has the highest average "
        f"movie rating by release year, at "
        f"{highest_year_rating}.",

        f"{lowest_year} has the lowest average "
        f"movie rating by release year, at "
        f"{lowest_year_rating}.",

        "The visualizations help identify patterns "
        "in movie ratings, genres and release years."
    ]


    # ========================================================
    # FINAL JSON DATA
    # ========================================================

    return {

        "summary": summary,

        "rating_distribution": rating_distribution,

        "genre_counts": genre_counts,

        "genre_avg_rating": genre_avg_rating,

        "yearly_avg_rating": yearly_avg_rating,

        "scatter_points": scatter_points,

        "insights": insights,

        "top10": top10
    }


# ============================================================
# 4. DASHBOARD PAGE
# ============================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ============================================================
# 5. API
# ============================================================

@app.route("/api/data")
def api_data():

    analysis_data = build_analysis(df)

    return jsonify(analysis_data)


# ============================================================
# 6. RUN FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )