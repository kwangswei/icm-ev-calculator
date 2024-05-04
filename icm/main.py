import streamlit as st
from icm_ev import ICMEVCalculator

st.set_page_config(layout="wide", page_title="ICM EV Calculator")
st.title("ICM EV Calculator")

with st.container():
    st.subheader("Settings", divider="rainbow")

    st.caption('Equity ref: https://openpokertools.com/range-equity.html')

    col1, col2, col3 = st.columns(3)
    with col1:
        p_win = st.number_input("% of win", min_value=0.0, max_value=1.0, format="%.3f", value=0.55)
    with col2:
        p_tie = st.number_input("% of tie", min_value=0.0, max_value=1.0, format="%.3f", value=0.0)
    with col3:
        p_lose = st.number_input("% of lose", min_value=0.0, max_value=1.0, format="%.3f", value=0.45)

    col1, col2 = st.columns(2)
    with col1:
        prizes = st.text_input("prizes", value="100/30/10").split("/")
    with col2:
        stacks = st.text_input("stacks", value="20/10/5").split("/")

    col1, col2 = st.columns(2)
    with col1:
        idx_hero = st.number_input("index of hero", min_value=0, help="zero-based numbering")
    with col2:
        idx_villain = st.number_input("index of villain", min_value=1, help="zero-based numbering")


if st.button("Calculate"):
    icm = ICMEVCalculator(
        p_win=p_win,
        p_tie=p_tie,
        p_lose=p_lose,
        stacks=stacks[:],
        prizes=prizes[:],
        hero=idx_hero,
        villain=idx_villain,
    )

    st.subheader("Result", divider="rainbow")

    ev_win, ev_tie, ev_lose, ev_call, ev_fold = icm.get()

    st.markdown(
        f'''##### ICM EV of Call
> *%win x ICM EV of Win + %tie x ICM EV of Tie + %lose x ICM EV of Lose <> ICM EV of Fold*

    {p_win:.3f} * {ev_win:.3f} + {p_tie:.3f} * {ev_tie:.3f} + {p_lose:.3f} * {ev_lose:.3f} = {ev_call:.3f}
'''
    )

    st.markdown(
        f'''##### ICM EV of Fold
        {ev_fold:.3f}
        '''
    )

    if ev_call > ev_fold:
        st.info("Call", icon=":material/check:")
    else:
        st.error("Fold", icon=":material/cancel:")
