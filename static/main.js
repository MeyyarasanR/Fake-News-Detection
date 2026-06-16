console.log("FACTSHIELD JS CONNECTED");



document.addEventListener(
    "DOMContentLoaded",
    () => {




        const form =
            document.getElementById(
                "analyze-form"
            );


        const textarea =
            document.getElementById(
                "news-text"
            );


        const charCount =
            document.querySelector(
                ".char-count"
            );



        const resultsCard =
            document.getElementById(
                "results-card"
            );


        const loader =
            document.getElementById(
                "result-loader"
            );


        const resultContent =
            document.getElementById(
                "result-content"
            );




        const predictionBadge =
            document.getElementById(
                "prediction-badge"
            );


        const confidencePercentage =
            document.getElementById(
                "confidence-percentage"
            );


        const confidenceBar =
            document.getElementById(
                "confidence-bar"
            );





        const reportBox =
            document.getElementById(
                "report-box"
            );


        const reportIcon =
            document.getElementById(
                "report-icon"
            );


        const reportTitle =
            document.getElementById(
                "report-title"
            );


        const reportDesc =
            document.getElementById(
                "report-desc"
            );




        const clearBtn =
            document.getElementById(
                "clear-btn"
            );


        const copyBtn =
            document.getElementById(
                "copy-report"
            );


        const historyList =
            document.getElementById(
                "history-list"
            );


        const clearHistoryBtn =
            document.getElementById(
                "clear-history"
            );









        // =======================
        // CHARACTER COUNT
        // =======================


        textarea.addEventListener(
            "input",
            () => {


                charCount.textContent =
                    textarea.value.length
                    +
                    " characters";


            }
        );










        // =======================
        // CLEAR TEXT
        // =======================


        clearBtn.addEventListener(
            "click",
            () => {



                textarea.value =
                    "";



                charCount.textContent =
                    "0 characters";



                resultsCard.classList.add(
                    "hidden"
                );



            }
        );












        // =======================
        // ANALYZE
        // =======================


        form.addEventListener(
            "submit",
            async function (event) {



                event.preventDefault();


                event.stopPropagation();





                const text =
                    textarea
                        .value
                        .trim();




                console.log(
                    "TEXT SENT:",
                    text
                );




                if (
                    text.length === 0
                ) {


                    alert(
                        "Please enter news"
                    );


                    return;


                }






                resultsCard.classList.remove(
                    "hidden"
                );


                loader.classList.remove(
                    "hidden"
                );


                resultContent.classList.add(
                    "hidden"
                );








                try {



                    const response =
                        await fetch(
                            "/predict",
                            {


                                method:
                                    "POST",


                                headers:
                                {

                                    "Content-Type":
                                        "application/json"

                                },


                                body:
                                    JSON.stringify(
                                        {
                                            text: text
                                        }
                                    )


                            }
                        );






                    const data =
                        await response.json();




                    console.log(
                        data
                    );







                    if (
                        data.status === "success"
                    ) {



                        displayResult(

                            data.prediction,

                            data.confidence,

                            data.ai_verification,

                            data.verification_mode

                        );



                    }




                    else {


                        showError(
                            data.message
                        );


                    }



                }






                catch (error) {



                    console.log(
                        error
                    );



                    showError(
                        "Server connection failed"
                    );



                }




                return false;



            }
        );












        // =======================
        // DISPLAY RESULT
        // =======================



        function displayResult(
            prediction,
            confidence,
            aiText,
            mode
        ) {





            loader.classList.add(
                "hidden"
            );



            resultContent.classList.remove(
                "hidden"
            );





            predictionBadge.className =
                "badge";


            confidenceBar.className =
                "gauge-bar-fill";


            reportBox.className =
                "report-box";







            if (
                prediction === "Real"
            ) {



                predictionBadge.textContent =
                    "REAL NEWS";


                predictionBadge.classList.add(
                    "real"
                );


                confidenceBar.classList.add(
                    "real"
                );


                reportBox.classList.add(
                    "real"
                );



                setSvgIcon(
                    "real"
                );



            }




            else {



                predictionBadge.textContent =
                    "MISLEADING / FAKE";


                predictionBadge.classList.add(
                    "fake"
                );



                confidenceBar.classList.add(
                    "fake"
                );



                reportBox.classList.add(
                    "fake"
                );



                setSvgIcon(
                    "fake"
                );



            }








            if (aiText) {


                aiText =
                    aiText.replace(
                        "Verification Mode: Waiting...",
                        ""
                    );


            }






            reportTitle.innerText =

                "AI Verified Information\n"

                +

                "Verification Mode: "

                +

                (
                    mode ||
                    "Local Verification"
                );







            reportDesc.innerText =
                aiText;







            confidenceBar.style.width =
                confidence
                +
                "%";



            confidencePercentage.textContent =
                Number(
                    confidence
                )
                    .toFixed(1)
                +
                "%";







            saveHistory(
                prediction,
                confidence
            );





        }












        // =======================
        // COPY REPORT
        // =======================


        copyBtn.addEventListener(
            "click",
            () => {



                let report =

                    reportTitle.innerText

                    +

                    "\n\n"

                    +

                    reportDesc.innerText;





                navigator.clipboard.writeText(
                    report
                );




                copyBtn.innerText =
                    "Copied ✔";




                setTimeout(
                    () => {


                        copyBtn.innerText =
                            "Copy Report";


                    },
                    1500
                );



            }
        );









        // =======================
        // HISTORY SAVE
        // =======================



        function saveHistory(
            prediction,
            confidence
        ) {



            let history =
                JSON.parse(
                    localStorage.getItem(
                        "history"
                    )
                )
                ||
                [];





            history.unshift(
                {


                    prediction:
                        prediction,


                    confidence:
                        confidence,


                    date:
                        new Date()
                            .toLocaleString()


                }
            );






            localStorage.setItem(

                "history",

                JSON.stringify(
                    history
                )

            );



            showHistory();



        }









        // =======================
        // SHOW HISTORY
        // =======================



        function showHistory() {



            let history =
                JSON.parse(
                    localStorage.getItem(
                        "history"
                    )
                )
                ||
                [];





            if (
                history.length === 0
            ) {



                historyList.innerHTML =
                    "<p>No history yet</p>";



                return;


            }






            historyList.innerHTML =
                "";





            history.forEach(
                item => {



                    historyList.innerHTML +=

                        `

<div class="report-box">

<b>${item.prediction}</b>

<br>

Confidence:
${Number(item.confidence).toFixed(1)}%

<br>

${item.date}

</div>

`;



                }
            );



        }










        // =======================
        // CLEAR HISTORY
        // =======================


        clearHistoryBtn.addEventListener(
            "click",
            () => {



                localStorage.removeItem(
                    "history"
                );



                showHistory();



            }
        );









        function showError(
            message
        ) {



            loader.classList.add(
                "hidden"
            );



            resultContent.classList.remove(
                "hidden"
            );



            predictionBadge.textContent =
                "ERROR";



            reportTitle.textContent =
                "Failed";



            reportDesc.textContent =
                message;



        }









        function setSvgIcon(
            type
        ) {



            reportIcon.innerHTML =
                "";



            if (
                type === "real"
            ) {


                reportIcon.innerHTML =
                    `
✔
`;


            }



            else {


                reportIcon.innerHTML =
                    `
✖
`;


            }



        }








        showHistory();




    }
);