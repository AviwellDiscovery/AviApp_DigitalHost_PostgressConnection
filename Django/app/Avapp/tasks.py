# tasks.py
from celery import shared_task
import fireducks.pandas as fd

@shared_task
def process_csv_filter(csv_path, chunksize):
    # This is a simplified example. You might need to customize how you apply filtering.
    chunks = []
    for chunk in fd.read_csv(csv_path, decimal=",", chunksize=chunksize):
        if not chunk.empty:
            chunks.append(chunk)
    if chunks:
        df = fd.concat(chunks, ignore_index=True)
        return df.to_dict(orient="records")
    return []