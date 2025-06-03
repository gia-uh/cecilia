import streamlit as st

st.set_page_config(page_title="Cecilia - The Cuban Language Model", page_icon="logo.png")

st.markdown(
    """
    ## Technical Report
    ### Cecilia - The Cuban Language Model
    #### Version 0.1
    """
)

st.markdown(
    """
    This report provides an overview of the development and capabilities of Cecilia, a language model
    specifically designed for the Cuban Spanish language. The model is based on the Salamandra 2B architecture
    and has been fine-tuned with a diverse dataset to enhance its understanding and generation of Cuban Spanish.

    You can download the technical report in PDF format from the following link.
    """
)

st.download_button(
    label="Download Technical Report",
    icon="📑",
    data=open("report/report.pdf", "rb").read(),
    file_name="cecilia_2b_technical_report.pdf",
    mime="application/pdf",
    help="Click to download the technical report in PDF format.",
    type="primary"
)