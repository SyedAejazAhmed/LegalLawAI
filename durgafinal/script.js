document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chatbox");
    const userInput = document.getElementById("userInput");
    const chatForm = document.getElementById("chat-form");
    const chatList = document.getElementById("chatList"); // Stores chat history
    let chatHistory = [];

    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        sendMessage();
    });

    function sendMessage() {
        let message = userInput.value.trim();
        if (!message) return;

        // Append user message
        appendMessage("User", message);
        userInput.value = ""; // Clear input field

        // Save message in chat history
        chatHistory.push({ sender: "User", message });

        // ✅ Send request to Django API with CSRF token
        fetch("/query_deepseek_r1/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // Get CSRF token for Django security
            },
            body: JSON.stringify({ query: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("⚠️ Error fetching response");
            }
            return response.body.getReader(); // ✅ Read response as stream
        })
        .then(async reader => {
            let botMessage = appendMessage("AI", ""); // Create empty bot message
            let decoder = new TextDecoder();
            let fullText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                let chunk = decoder.decode(value, { stream: true });
                fullText += chunk.replace(/data: /g, ""); // ✅ Remove unwanted "data: " prefix
                botMessage.textContent = fullText; // ✅ Dynamically update bot response
                chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
            }

            // ✅ Save AI response in chat history & update UI
            chatHistory.push({ sender: "AI", message: fullText });
            updateChatList();
        })
        .catch(error => {
            console.error("Fetch error:", error);
            appendMessage("AI", "⚠️ Unable to fetch response.");
        });
    }

    function appendMessage(sender, text) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender === "AI" ? "bot-message" : "user-message");

        const messageContent = document.createElement("div");
        messageContent.classList.add("message-content");

        const iconElement = document.createElement("img");
        iconElement.src = sender === "AI" ? "/static/images/bot.png" : "/static/images/user.webp";
        iconElement.classList.add("logo");

        const textElement = document.createElement("span");
        textElement.textContent = text;

        messageContent.appendChild(iconElement);
        messageContent.appendChild(textElement);
        messageElement.appendChild(messageContent);

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
        return textElement; // ✅ Return for dynamic updates
    }

    function updateChatList() {
        chatList.innerHTML = ""; // Clear existing chat list

        chatHistory.forEach((chat, index) => {
            const chatDiv = document.createElement("div");
            chatDiv.classList.add("chat-entry");
            chatDiv.textContent = `${chat.sender}: ${chat.message.substring(0, 20)}...`; // Show preview
            chatDiv.addEventListener("click", () => loadChat(index));
            chatList.appendChild(chatDiv);
        });
    }

    function loadChat(index) {
        chatBox.innerHTML = ""; // Clear current chatbox

        chatHistory.slice(0, index + 1).forEach(chat => {
            appendMessage(chat.sender, chat.message);
        });

        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
