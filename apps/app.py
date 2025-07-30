import streamlit as st

st.set_page_config(page_title="Cecilia - The Cuban Language Model", page_icon="logo.png", layout="wide")


patterns = {
    "Download Model from HuggingFace": lambda l,u: st.link_button(label=l, url=u, type="primary", icon="🌟"),
    "Read the Technical Report": lambda l,u: st.link_button(label=l, url="./report", type="secondary", icon="📑"),
    "Help us improve Cecilia": lambda l,u: st.link_button(label=l, url="./training", type="secondary", icon="💝"),
}

left_col, right_col = st.columns([1,2], gap="large")
left_col.image("logo.png", use_column_width=True)

with open("README.md", "r") as f:
    readme_content = f.readlines()

fragment = []

for line in readme_content:
    if line.startswith("- [") and "https" in line:
        if fragment:
            right_col.markdown("".join(fragment))
            fragment.clear()

        left, right = line.split("](")
        left = left.strip().removeprefix("- [").removesuffix("]")
        right = right.strip().removeprefix("(").removesuffix(".").removesuffix(")")

        if left in patterns:
            patterns[left](left, right)
        else:
            right_col.link_button(left, right)

    else:
        fragment.append(line)


if fragment:
    right_col.markdown("".join(fragment))
    fragment.clear()
