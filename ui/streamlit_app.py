"""Streamlit UI — a thin client over the same service APIs the CLI uses.

Run: ``uv run streamlit run ui/streamlit_app.py``
"""

import sys
from pathlib import Path

# Ensure src/ is on the path when running standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st

from myapp.services.example.api import ExampleService
from myapp.services.example.schemas import ItemCreate
from myapp.services.example.storage import ExampleJsonStore, ExampleSqliteStore
from myapp.shared.config import ensure_data_dirs

ensure_data_dirs()

st.set_page_config(page_title="myapp", layout="wide")
st.title("myapp — Example Service")

# ── sidebar: backend picker ───────────────────────────────────────────

backend = st.sidebar.radio("Storage backend", ["sqlite", "json"], index=0)
store = ExampleSqliteStore() if backend == "sqlite" else ExampleJsonStore()
svc = ExampleService(store=store)

# ── create item ───────────────────────────────────────────────────────

with st.expander("Add new item", expanded=False):
    with st.form("add_item"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        tags_raw = st.text_input("Tags (comma-separated)")
        submitted = st.form_submit_button("Create")
        if submitted and name:
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            resp = svc.create(ItemCreate(name=name, description=description, tags=tags))
            if resp.success:
                st.success(f"Created item {resp.data['id']}")
                st.rerun()
            else:
                st.error(resp.message)

# ── list items ────────────────────────────────────────────────────────

st.subheader("Items")
resp = svc.list_items()
items = resp.data or []

if not items:
    st.info("No items yet. Create one above.")
else:
    for item in items:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item['name']}** (`{item['id']}`)")
            if item.get("description"):
                st.caption(item["description"])
            if item.get("tags"):
                st.caption(f"Tags: {', '.join(item['tags'])}")
        with col2:
            if st.button("Delete", key=f"del_{item['id']}"):
                svc.delete(item["id"])
                st.rerun()

# ── export / import ───────────────────────────────────────────────────

st.divider()
col_exp, col_imp = st.columns(2)
with col_exp:
    if st.button("Export to JSON"):
        resp = svc.export_json()
        st.info(resp.message)
with col_imp:
    if st.button("Import from JSON"):
        resp = svc.import_json()
        st.info(resp.message)
        st.rerun()
