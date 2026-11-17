"""
tables.py — Styled, clean dataframe displays that preserve original global rank
and clearly distinguish filtered views.
"""
import streamlit as st
import pandas as pd


def render_clean_table(df: pd.DataFrame, height: int = 395, hide_index: bool = True):
    st.dataframe(df, width='stretch', height=height, hide_index=hide_index)
