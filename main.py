import gradio as gr
import duckdb
import pandas as pd


def handle_file_upload(file):
    """Handle the uploaded CSV file."""
    if file is None:
        return "No file uploaded yet."
    return f"File uploaded: {file.name}"


def handle_csv_submit(file):
    if file is None:
        return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    # In memory duck db
    conn = duckdb.connect(":memory:")
    # Load csv data to duckdb
    df = pd.read_csv(file.name)
    conn.register("data", df)

    columns_query = "SELECT column_name FROM (DESCRIBE data)"
    columns = conn.execute(columns_query).fetchdf()["column_name"].tolist()
    print(columns)

    # Hide upload, show description, keep chat hidden
    return conn, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)


def handle_description_submit(description):
    # Hide description, show chat
    return description, gr.update(visible=False), gr.update(visible=True)


def main():
    with gr.Blocks(title="Ephemeral CSV Query AI") as app:
        gr.Markdown("# Ephemeral CSV Query AI")
        gr.Markdown(
            "Upload your CSV file and ask questions about your data in plain English. Your data stays private and is never stored."
        )

        db_state = gr.State()
        description_state = gr.State()

        # Step 1: Upload CSV
        with gr.Column(visible=True) as step_upload:
            gr.Markdown("### Step 1: Upload a CSV file to get started.")
            csv_file = gr.File(label="Upload CSV", file_types=[".csv"], type="filepath")
            upload_btn = gr.Button("Submit")

        # Step 2: Description
        with gr.Column(visible=False) as step_description:
            gr.Markdown("### Step 2: Describe your dataset")
            description_input = gr.TextArea(
                label="Describe your dataset",
                lines=5,
                placeholder="What is this data about?",
            )
            desc_btn = gr.Button("Continue")

        # Step 3: Chat
        with gr.Column(visible=False) as step_chat:
            gr.Markdown("### Step 3: Chat with your data")
            # Chat UI will go here

        # Wire up navigation
        upload_btn.click(
            fn=handle_csv_submit,
            inputs=[csv_file],
            outputs=[db_state, step_upload, step_description, step_chat],
        )

        desc_btn.click(
            fn=handle_description_submit,
            inputs=[description_input],
            outputs=[description_state, step_description, step_chat],
        )

    app.launch()


if __name__ == "__main__":
    main()
