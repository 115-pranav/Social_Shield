document.addEventListener("DOMContentLoaded", function () {

    const messageInput = document.getElementById("messageInput");
    const charCount = document.getElementById("charCount");
    const analyzeBtn = document.getElementById("analyzeBtn");

    const resultBox = document.getElementById("resultBox");
    const resultIcon = document.getElementById("resultIcon");
    const resultTitle = document.getElementById("resultTitle");
    const resultMessage = document.getElementById("resultMessage");

    const categoryResult = document.getElementById("categoryResult");
    const riskResult = document.getElementById("riskResult");
    const confidenceResult = document.getElementById("confidenceResult");

    const urlWarning = document.getElementById("urlWarning");


    // Character counter
    messageInput.addEventListener("input", function () {

        const length = messageInput.value.length;

        charCount.textContent = length + " / 1000";

    });


    // Analyze button
    analyzeBtn.addEventListener("click", async function () {

        const message = messageInput.value.trim();


        // Check empty message
        if (!message) {

            alert("Please enter a message first.");

            return;
        }


        // Change button while analyzing
        analyzeBtn.disabled = true;

        analyzeBtn.textContent = "Analyzing...";


        // Hide previous URL warning
        urlWarning.classList.add("hidden");

        urlWarning.textContent = "";


        try {

            // Get CSRF token
            const csrfToken = getCookie("csrftoken");


            // Send message to Django
            const formData = new FormData();

            formData.append("message", message);


            const response = await fetch("/analyze/", {

                method: "POST",

                headers: {
                    "X-CSRFToken": csrfToken
                },

                body: formData

            });


            const data = await response.json();


            // Handle backend error
            if (!response.ok) {

                throw new Error(
                    data.error || "Something went wrong."
                );

            }


            // Show result box
            resultBox.classList.remove("hidden");


            // Get prediction
            const category = data.category;
            const risk = data.risk;
            const confidence = data.confidence;


            // Display result
            categoryResult.textContent = category;

            riskResult.textContent = risk;

            confidenceResult.textContent =
                confidence + "%";


            /*
             * Category-specific messages
             */

            if (category === "Safe") {

                resultIcon.textContent = "SAFE";

                resultTitle.textContent =
                    "Message Appears Safe";

                resultMessage.textContent =
                    "No major threat was detected in this message.";

            }

            else if (category === "Spam") {

                resultIcon.textContent = "SPAM";

                resultTitle.textContent =
                    "Spam Message Detected";

                resultMessage.textContent =
                    "This message may contain unwanted promotional or misleading content.";

            }

            else if (category === "Phishing") {

                resultIcon.textContent = "PHISH";

                resultTitle.textContent =
                    "Possible Phishing Message";

                resultMessage.textContent =
                    "Be careful. This message may attempt to collect sensitive information.";

            }

            else if (category === "Suspicious") {

                resultIcon.textContent = "CHECK";

                resultTitle.textContent =
                    "Suspicious Message";

                resultMessage.textContent =
                    "This message contains patterns that may require additional caution.";

            }

            else if (category === "Abusive") {

                resultIcon.textContent = "ABUSE";

                resultTitle.textContent =
                    "Abusive Content Detected";

                resultMessage.textContent =
                    "This message contains potentially abusive language.";

            }

            else {

                resultIcon.textContent = "INFO";

                resultTitle.textContent =
                    "Analysis Complete";

                resultMessage.textContent =
                    "The message has been analyzed.";

            }


            /*
             * URL warning
             */

            if (data.has_url) {

                urlWarning.textContent =
                    "This message contains a URL. Be careful before opening unknown links.";

                urlWarning.classList.remove("hidden");

            }

            else {

                urlWarning.textContent = "";

                urlWarning.classList.add("hidden");

            }


        }

        catch (error) {

            console.error("Analysis error:", error);

            alert(
                error.message ||
                "Unable to analyze the message."
            );

        }

        finally {

            // Restore button
            analyzeBtn.disabled = false;

            analyzeBtn.textContent =
                "Analyze Message";

        }

    });


    /*
     * Get CSRF cookie
     */

    function getCookie(name) {

        let cookieValue = null;


        if (document.cookie && document.cookie !== "") {

            const cookies =
                document.cookie.split(";");


            for (let i = 0; i < cookies.length; i++) {

                const cookie =
                    cookies[i].trim();


                if (
                    cookie.substring(
                        0,
                        name.length + 1
                    ) ===
                    (name + "=")
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;

                }

            }

        }


        return cookieValue;

    }

});