import gradio as gr
import duckdb
import pandas as pd
from agent import build_agent

def handle_file_upload(file):
    """Handle the uploaded CSV file."""
    if file is None:
        return "No file uploaded yet."
    return f"File uploaded: {file.name}"


def handle_csv_submit(file):
    if file is None:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
        )
    # In memory duck db
    conn = duckdb.connect(":memory:")
    # Load csv data to duckdb
    df = pd.read_csv(file.name)
    conn.register("data", df)


    # Hide upload, show description, keep chat hidden
    return (
        conn,
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
    )


def handle_description_submit(description, db_conn):
    agent = build_agent(db_conn)
    # Hide description, show chat
    return description, agent, gr.update(visible=False), gr.update(visible=True)    


def add_user_message(user_message, history):
    """Add user message to chat history."""
    if not user_message:
        return history, ""
    history = history or []
    history.append({"role": "user", "content": user_message})
    return history, ""


def generate_response(history, agent, description):
    """Generate bot response and add to history."""
    if not history:
        return history
    
    # Get the last user message
    user_message = history[-1]["content"]
    
    # TODO: Add your agent logic here
    agent_response = agent.invoke({"messages": [("user", user_message)]})
    
    print(agent_response["messages"][-1])

    bot_response = agent_response["messages"][-1].content
    
    history.append({"role": "assistant", "content": bot_response})
    return history


def main():
    with gr.Blocks(title="Ephemeral CSV Query AI") as app:
        gr.Markdown("# Ephemeral CSV Query AI")
        gr.Markdown(
            "Upload your CSV file and ask questions about your data in plain English. Your data stays private and is never stored."
        )

        db_state = gr.State()
        description_state = gr.State()
        agent_state = gr.State()

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
            chatbot = gr.Chatbot(label="Chat")
            user_input = gr.Textbox(
                placeholder="Ask something about your data...", label="Your message"
            )
            send_button = gr.Button("Send")

        # Wire up navigation
        upload_btn.click(
            fn=handle_csv_submit,
            inputs=[csv_file],
            outputs=[db_state, step_upload, step_description, step_chat],
        )

        desc_btn.click(
            fn=handle_description_submit,
            inputs=[description_input, db_state],
            outputs=[description_state, agent_state, step_description, step_chat],
        )

        # Chat handlers - chain user message then bot response
        send_button.click(
            fn=add_user_message,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input],
        ).then(
            fn=generate_response,
            inputs=[chatbot, agent_state, description_state],
            outputs=[chatbot],
        )

        # Also trigger on Enter key
        user_input.submit(
            fn=add_user_message,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input],
        ).then(
            fn=generate_response,
            inputs=[chatbot, agent_state, description_state],
            outputs=[chatbot],
        )

    app.launch()


if __name__ == "__main__":
    main()
