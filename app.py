import streamlit as st
from PyPDF2 import PdfReader
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="API Advisor from RFP", layout="wide")
st.title("API Advisor from RFP")

uploaded_file = st.file_uploader("Upload RFP (PDF/Text)", type=["pdf", "txt"])

if uploaded_file:
    # Step 1: Extract text
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages])
    else:
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    st.subheader("Extracted RFP Text:")
    st.text_area("Content", text, height=200)

    # Step 2: Explain API
    st.subheader("What is an API?")
    st.write("""
    An **API (Application Programming Interface)** defines how two systems talk.
    It describes **endpoints**, **methods** (GET/POST/etc), and **data formats** (JSON/XML).
    """)

    # Step 3: Suggest API type (rule-based)
    suggestion = "REST API (most common and simple)."
    if "real-time" in text.lower():
        suggestion = "WebSocket or gRPC API (for real-time streaming)."
    elif "analytics" in text.lower() or "data" in text.lower():
        suggestion = "GraphQL API (flexible queries over structured data)."
    elif "legacy" in text.lower() or "enterprise" in text.lower():
        suggestion = "SOAP API (enterprise integrations, older systems)."

    st.subheader("Suggested API Type for this RFP:")
    st.success(suggestion)

    # Step 4: Base OpenAPI spec
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Generated API from RFP",
            "version": "1.0.0",
            "description": "Auto-generated from uploaded RFP text."
        },
        "paths": {
            "/": {
                "get": {
                    "summary": "Root endpoint",
                    "responses": {
                        "200": {
                            "description": "Welcome message",
                            "content": {"application/json": {"example": {"message": "Hello, this is your API!"}}}
                        }
                    }
                }
            },
            "/status": {
                "get": {
                    "summary": "Check API status",
                    "responses": {
                        "200": {
                            "description": "API is healthy",
                            "content": {"application/json": {"example": {"status": "OK"}}}
                        }
                    }
                }
            }
        }
    }

    # Step 5: Let user add custom endpoints
    st.subheader("Add Custom Endpoint")
    with st.form("add_endpoint_form"):
        path = st.text_input("Endpoint Path (e.g., /users)")
        method = st.selectbox("HTTP Method", ["get", "post", "put", "delete"])
        summary = st.text_input("Summary", "Custom endpoint")
        example_key = st.text_input("Example Key", "result")
        example_value = st.text_input("Example Value", "success")
        add_btn = st.form_submit_button("Add Endpoint")

        if add_btn and path:
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}
            openapi_spec["paths"][path][method] = {
                "summary": summary,
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "example": {example_key: example_value}
                            }
                        }
                    }
                }
            }
            st.success(f"✅ Endpoint `{method.upper()} {path}` added!")

    # Step 6: Show OpenAPI spec
    st.subheader("Generated OpenAPI Spec (Swagger JSON):")
    st.json(openapi_spec)

    # Step 7: Download option
    spec_json = json.dumps(openapi_spec, indent=2)
    st.download_button("Download OpenAPI Spec", spec_json, file_name="openapi.json")

    # Step 8: Swagger UI live preview
    st.subheader("Live Swagger UI Preview:")
    swagger_ui_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        const spec = {json.dumps(openapi_spec)};
        SwaggerUIBundle({{
          spec: spec,
          dom_id: '#swagger-ui',
        }});
      </script>
    </body>
    </html>
    """
    components.html(swagger_ui_html, height=600, scrolling=True)
