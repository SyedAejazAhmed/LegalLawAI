document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const chatForm = document.getElementById("chat-form");

    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        sendMessage();
    });

    function sendMessage() {
        let message = userInput.value.trim();
        if (!message) return;

        appendMessage("user", message);
        userInput.value = ""; // Clear input field

        fetch("/query/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "query": message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("⚠️ Error fetching response");
            }
            return response.body.getReader(); // ✅ Read stream response
        })
        .then(async reader => {
            let botMessage = appendMessage("bot", ""); // Create empty bot message
            let decoder = new TextDecoder();
            let fullText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                let chunk = decoder.decode(value, { stream: true });
                fullText += chunk;
                botMessage.textContent = fullText; // Update bot message dynamically
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            appendMessage("bot", "⚠️ Unable to fetch response");
        });
    }

    function appendMessage(sender, text) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message", sender);

        // ✅ Create an image element for the icon
        const iconElement = document.createElement("img");
        iconElement.src = sender === "bot" ? "/static/images/bot.png" : "/static/images/user.webp";
        iconElement.classList.add(sender === "bot" ? "bot-icon" : "user-icon");

        // ✅ Append icon and message
        messageElement.appendChild(iconElement);
        const textElement = document.createElement("p");
        textElement.textContent = text;
        messageElement.appendChild(textElement);

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
        return textElement; // Return text element for streaming updates
    }
});
