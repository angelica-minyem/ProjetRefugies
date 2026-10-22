# %%
import plotly.express as px
import pandas as pd

overview = pd.read_csv("overview.csv")

fig = px.scatter(
    overview,
    x="mean_destination_countries",
    y="asylum_seekers",
    hover_name="region_origin",
    hover_data={
        "mean_destination_countries": ":.1f",
        "asylum_seekers": ":,"
    },
    labels={
        "mean_destination_countries": "Mean number of destination countries",
        "asylum_seekers": "Total asylum seekers"
    }
)

fig.update_layout(
    title="Asylum seekers and destination diversity by region"
)

fig.show()
# %%
