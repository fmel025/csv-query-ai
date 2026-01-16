import gradio as gr
import duckdb


def handle_file_upload(file):
    """Handle the uploaded CSV file."""
    if file is None:
        return "No file uploaded yet."
    return f"File uploaded: {file.name}"


def main():
    with gr.Blocks(title="Ephemeral CSV Query AI") as app:
        gr.Markdown("# Ephemeral CSV Query AI")
        gr.Markdown("### Upload a CSV file to get started.")

        db_state = gr.State()
        description_state = gr.State()

        with gr.Tab("Upload CSV", visible=True):
            csv_file = gr.File(label="Upload CSV", file_types=[".csv"], type="filepath")
            button = gr.Button("Submit")

        # with gr.Row():
        #     file_input = gr.File(
        #         label="Upload CSV File", file_types=[".csv"], type="filepath"
        #     )

        # output = gr.Textbox(label="Status", interactive=False)

        # file_input.change(fn=handle_file_upload, inputs=[file_input], outputs=[output])

    app.launch()


if __name__ == "__main__":
    main()
