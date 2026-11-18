
import os
import streamlit as st
import pandas as pd

from dotenv import load_dotenv
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient

load_dotenv()

CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

TABLE_NAME = "ClothingReadings"
CONTAINER_NAME = "clothing-images"

st.set_page_config(
    page_title="Smart Wardrobe AI",
    page_icon="👕",
    layout="wide"
)

st.title("👕 Smart Wardrobe AI")
st.caption("Raspberry Pi 5 | TMP102 | Ollama | Azure")

if not CONNECTION_STRING:
    st.error("Missing Azure connection string in .env file.")
    st.stop()


@st.cache_data(ttl=30)
def get_scans():
    service = TableServiceClient.from_connection_string(
        CONNECTION_STRING
    )

    table = service.get_table_client(TABLE_NAME)

    records = list(table.query_entities(
        query_filter="PartitionKey eq 'ClothingScans'"
    ))

    records.sort(
        key=lambda x: x.get("TimestampUTC", ""),
        reverse=True
    )

    return records


@st.cache_data(ttl=300)
def get_photo(blob_name):
    service = BlobServiceClient.from_connection_string(
        CONNECTION_STRING
    )

    blob = service.get_blob_client(
        container=CONTAINER_NAME,
        blob=blob_name
    )

    return blob.download_blob().readall()


if st.button("🔄 Refresh Data"):
    get_scans.clear()
    get_photo.clear()
    st.rerun()


try:
    scans = get_scans()
except Exception as e:
    st.error(f"Azure error: {e}")
    st.stop()


if not scans:
    st.info("No clothing scans found in Azure yet.")
    st.stop()


latest = scans[0]
temp = latest.get("TemperatureF", 0)
analysis = latest.get("AIResult", "")
image_name = latest.get("ImageBlobName")


# Dashboard summary
col1, col2, col3 = st.columns(3)

col1.metric("🌡️ Temperature", f"{temp:.1f} °F")
col2.metric("📸 Total Scans", len(scans))
col3.metric("🤖 AI Engine", "Ollama")

st.divider()

st.subheader("Latest Clothing Analysis")

left, right = st.columns([1, 2])

with left:
    if image_name:
        try:
            st.image(
                get_photo(image_name),
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Image unavailable: {e}")

with right:
    st.markdown("### AI Recommendation")
    st.write(analysis)
    st.write("**Temperature:**", f"{temp:.1f} °F")
    st.write("**Captured:**", latest.get("TimestampUTC"))
    st.write("**Device:**", latest.get("Device"))


# Temperature history
st.divider()
st.subheader("Temperature History")

df = pd.DataFrame([
    {
        "Time": r.get("TimestampUTC"),
        "Temperature": r.get("TemperatureF")
    }
    for r in scans
])

df["Time"] = pd.to_datetime(
    df["Time"], utc=True, errors="coerce"
)
df["Temperature"] = pd.to_numeric(
    df["Temperature"], errors="coerce"
)

df = df.dropna().sort_values("Time")

if not df.empty:
    st.line_chart(df.set_index("Time")["Temperature"])


# Previous scans
st.divider()
st.subheader("Previous Clothing Scans")

for scan in scans[:10]:
    with st.expander(scan.get("TimestampUTC", "Unknown")):
        a, b = st.columns([1, 2])

        with a:
            name = scan.get("ImageBlobName")
            if name:
                try:
                    st.image(
                        get_photo(name),
                        use_container_width=True
                    )
                except Exception:
                    st.warning("Image unavailable")

        with b:
            st.write("**Temperature:**",
                     scan.get("TemperatureF"), "°F")
            st.write("**AI Analysis:**",
                     scan.get("AIResult"))
