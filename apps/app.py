import streamlit as st

st.set_page_config(page_title="Cecilia - The Cuban Language Model", page_icon="logo.png")

st.image("logo.png", width=300)

patterns = {
    "Download Model from HuggingFace": lambda l,u: st.link_button(label=l, url=u, type="primary", icon="🌟"),
    "Read the Technical Report": lambda l,u: st.link_button(label=l, url="./report", type="secondary", icon="📑"),
    "Help us improve Cecilia": lambda l,u: st.link_button(label=l, url="./training", type="secondary", icon="💝"),
}

with open("README.md", "r") as f:
    readme_content = f.readlines()

fragment = []

for line in readme_content:
    if line.startswith("- [") and "https" in line:
        if fragment:
            st.markdown("".join(fragment))
            fragment.clear()

        left, right = line.split("](")
        left = left.strip().removeprefix("- [").removesuffix("]")
        right = right.strip().removeprefix("(").removesuffix(".").removesuffix(")")

        if left in patterns:
            patterns[left](left, right)
        else:
            st.link_button(left, right)

    else:
        fragment.append(line)


if fragment:
    st.markdown("".join(fragment))
    fragment.clear()
