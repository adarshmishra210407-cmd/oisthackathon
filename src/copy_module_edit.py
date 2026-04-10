import streamlit as st

class ModuleEditor:
    @staticmethod
    def render_copy_button(text_to_copy):
        st.write("Alternatively, copy text directly from below:")
        st.code(text_to_copy, language="markdown")
