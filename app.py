import streamlit as st
from positioning import get_positioning

st.set_page_config(page_title="Positioning", layout="centered")

st.title("Graduate Positioning App")
st.write(
    "Paste what you have already done, and the opportunity you are "
    "aiming at. Every claim it makes must quote your own words."
)

have = st.text_area(
    "What you have done",
    height=300,
    placeholder="Your CV, a project write up, anything in your own words.",
)

opportunity = st.text_area(
    "The opportunity",
    height=200,
    placeholder="A job advert, a company, a grant, a person you want to work with.",
)

if st.button("Position me"):
    if not have.strip() or not opportunity.strip():
        st.warning("Fill in both boxes.")
    else:
        with st.spinner("Working..."):
            result = get_positioning(have, opportunity)

        if result is None:
            st.error("No valid response after 3 attempts. Try again.")
        else:
            st.subheader("Positioning")
            st.write(result["positioning"])

            st.metric("Strength", result["strength"])

            st.subheader("Evidence")
            for e in result["evidence"]:
                st.markdown("**" + e["claim"] + "**")
                st.caption('"' + e["their_words"] + '"')

            st.subheader("Gaps")
            for g in result["gaps"]:
                st.markdown("- " + g)

            st.subheader("Next artefact")
            st.write(result["next_artefact"])
            st.caption(result["why_this_artefact"])