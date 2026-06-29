from fastapi import FastAPI, UploadFile, File
import pandas as pd
import zipfile
import io

app = FastAPI()

@app.get("/")
def root():
    return {"status": "API running ✅"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()

    # unzip
    z = zipfile.ZipFile(io.BytesIO(contents))
    dataframes = []

    for name in z.namelist():
        if name.endswith(".csv"):
            with z.open(name) as f:
                df = pd.read_csv(f)

                # ✅ your core logic (simplified version)
                df["StartTime"] = pd.to_datetime(df["StartTime"], unit="s")

                df["Hour"] = df["StartTime"].dt.floor("H")

                det_cols = [c for c in df.columns if c.startswith("DET")]

                df["phase_total"] = df[det_cols].sum(axis=1)

                grouped = df.groupby("Hour")["phase_total"].sum().reset_index()

                dataframes.append(grouped)

    if not dataframes:
        return {"error": "No CSV found"}

    master = pd.concat(dataframes)

    # convert to JSON
    result = master.to_dict(orient="records")

    return {"data": result}