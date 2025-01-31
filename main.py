import pandas as pd
import streamlit as st
import plotly.express as px
import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv(".env.local")

st.set_page_config(layout="wide")

cnn = snowflake.connector.connect(
    user=os.environ.get("SNOWFLAKE_USER"),
    password=os.environ.get("SNOWFLAKE_PASSWORD"),
    account=os.environ.get("SNOWFLAKE_ACCOUNT"),
    warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
    database=os.environ.get("SNOWFLAKE_DATABASE"),
    schema=os.environ.get("SNOWFLAKE_SCHEMA"),
)


def get_data_from_snowflake():
    cs = cnn.cursor()

    try:
        cs.execute("SELECT * FROM PRODUCT_VIEWS_AND_PURCHASES LIMIT 5")
        rows = cs.fetchall()
        df = pd.DataFrame(rows, columns=[col[0] for col in cs.description])
        return df
    finally:
        cs.close()
        cnn.close()


@st.cache_data
def load_data():
    df = pd.read_csv("Retail sites.csv")
    df["date"] = pd.to_datetime(
        "20" + df["YEAR"].astype(str) + "-" + df["MONTH"].astype(str) + "-01"
    )
    return df


data = load_data()
test_snowflake = get_data_from_snowflake()

if data is not None:
    st.title("Retail Data")
    st.subheader("Data Preview")
    st.write(data.head())

    st.subheader("Total Purchases by Site")

    col1, col2, col3 = st.columns(3)

    grouped_data = data.groupby("SITE")["TOTAL_PURCHASES"].sum().reset_index()

    fig = px.pie(
        grouped_data,
        values="TOTAL_PURCHASES",
        names="SITE",
        height=300,
        width=200,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
    )
    col1.plotly_chart(fig, use_container_width=True)

    # Filter data
    st.subheader("Filter Data")

    selected_site = st.pills(
        "Site", data["SITE"].unique().tolist(), default="amazon.com"
    )

    # Filter by category
    categories = data["MAIN_CATEGORY"].unique().tolist()
    selected_categories = st.multiselect("Select category", categories)

    # Display metric data and chart
    col1, col2 = st.columns(2)

    total_views = round(data["TOTAL_VIEWS"].sum() / 1_000_000, 2)
    total_purchases = round(data["TOTAL_PURCHASES"].sum() / 1_000_000, 2)
    chart_data = (
        data[["date", "TOTAL_VIEWS", "TOTAL_PURCHASES"]]
        .groupby("date")
        .sum()
        .reset_index()
    )

    top10 = (
        data[["MAIN_CATEGORY", "TOTAL_PURCHASES"]]
        .groupby("MAIN_CATEGORY")
        .sum()
        .sort_values("TOTAL_PURCHASES", ascending=False)
        .head(10)
        .reset_index()
    )

    if selected_site is not None:
        if len(selected_categories) > 0:
            total_views = round(
                data.loc[
                    (data["SITE"] == selected_site)
                    & (data["MAIN_CATEGORY"].isin(selected_categories)),
                    "TOTAL_VIEWS",
                ].sum()
                / 1_000_000,
                2,
            )
            total_purchases = round(
                data.loc[
                    (data["SITE"] == selected_site)
                    & (data["MAIN_CATEGORY"].isin(selected_categories)),
                    "TOTAL_PURCHASES",
                ].sum()
                / 1_000_000,
                2,
            )

            chart_data = (
                data.loc[
                    (data["SITE"] == selected_site)
                    & (data["MAIN_CATEGORY"].isin(selected_categories)),
                    ["date", "TOTAL_VIEWS", "TOTAL_PURCHASES"],
                ]
                .groupby("date")
                .sum()
                .reset_index()
            )

        else:
            total_views = round(
                data.loc[data["SITE"] == selected_site, "TOTAL_VIEWS"].sum()
                / 1_000_000,
                2,
            )
            total_purchases = round(
                data.loc[data["SITE"] == selected_site, "TOTAL_PURCHASES"].sum()
                / 1_000_000,
                2,
            )

            chart_data = (
                data.loc[
                    data["SITE"] == selected_site,
                    ["date", "TOTAL_VIEWS", "TOTAL_PURCHASES"],
                ]
                .groupby("date")
                .sum()
                .reset_index()
            )

        top10 = (
            data.loc[
                data["SITE"] == selected_site, ["MAIN_CATEGORY", "TOTAL_PURCHASES"]
            ]
            .groupby("MAIN_CATEGORY")
            .sum()
            .sort_values("TOTAL_PURCHASES", ascending=False)
            .head(10)
            .reset_index()
        )

    else:
        if len(selected_categories) > 0:
            total_views = round(
                data.loc[
                    data["MAIN_CATEGORY"].isin(selected_categories),
                    "TOTAL_VIEWS",
                ].sum()
                / 1_000_000,
                2,
            )

            total_purchases = round(
                data.loc[
                    data["MAIN_CATEGORY"].isin(selected_categories),
                    "TOTAL_PURCHASES",
                ].sum()
                / 1_000_000,
                2,
            )

            chart_data = (
                data.loc[
                    data["MAIN_CATEGORY"].isin(selected_categories),
                    ["date", "TOTAL_VIEWS", "TOTAL_PURCHASES"],
                ]
                .groupby("date")
                .sum()
                .reset_index()
            )

    col1.metric("Total Views", total_views)
    col2.metric("Total Purchase", total_purchases)

    col1.write("Total Views and Purchases")
    if chart_data.empty:
        col1.write("Selected Site has not sold any of the selected categories")
    else:
        col1.line_chart(
            chart_data,
            x="date",
            y=["TOTAL_VIEWS", "TOTAL_PURCHASES"],
            color=["#B7FFFA", "#FFC067"],
            height=400,
        )

    col2.write("Top 10 Most Purchased Categories")
    col2.bar_chart(
        top10,
        x="MAIN_CATEGORY",
        y="TOTAL_PURCHASES",
        horizontal=True,
        height=400,
        color="#B7FFFA",
    )

    if test_snowflake is not None:
        st.title("Snowflake Data")
        st.subheader("Data Preview")
        st.write(test_snowflake)

else:
    st.write("No data to display")
