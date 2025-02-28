document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // ✅ Add single event listener for sending messages
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        // ✅ Append user's message
        appendMessage("user", message);
        userInput.value = ""; // ✅ Clear input field

        // ✅ Send query to Django API
        fetch("/query/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({"query": message})
        })
        .then(response => response.json())
        .then(data => {
            const responseText = data.response;
            appendMessage("bot", responseText); // ✅ Append bot's response
        })
        .catch(error => {
            console.error("Error:", error);
            appendMessage("bot", "⚠️ Error fetching response.");
        });
    }

    function appendMessage(sender, text) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message", sender);

        // ✅ Create an image element for the icon
        const iconElement = document.createElement("img");
        iconElement.src = sender === "bot" ? "bot.png" : "user.webp";
        iconElement.classList.add(sender === "bot" ? "bot-icon" : "user-icon");

        // ✅ Add icon and message
        messageElement.appendChild(iconElement);
        const textElement = document.createElement("p");
        textElement.textContent = text;
        messageElement.appendChild(textElement);

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
