const uploadForm =
    document.getElementById("uploadForm");

const fileInput =
    document.getElementById("file");

const fileName =
    document.getElementById("fileName");

const processButton =
    document.getElementById("processButton");

const message =
    document.getElementById("message");


fileInput.addEventListener(
    "change",
    function () {

        if (this.files.length > 0) {

            fileName.innerText =
                this.files[0].name;

        } else {

            fileName.innerText =
                "No file selected";

        }

    }
);



uploadForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const file =
            fileInput.files[0];

        const documentType =
            document.getElementById(
                "documentType"
            ).value;


        if (!file) {

            showMessage(
                "Please select a file.",
                true
            );

            return;
        }


        processButton.disabled = true;

        processButton.innerText =
            "Processing with AI...";

        showMessage(
            "Extracting and validating document..."
        );


        const formData =
            new FormData();


        formData.append(
            "document_type",
            documentType
        );


        formData.append(
            "file",
            file
        );


        try {

            const response =
                await fetch(
                    "/api/v1/documents/process",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Document processing failed."
                );

            }


            window.location.href =
                `/document-result?id=${data.id}`;


        } catch (error) {

            showMessage(
                error.message,
                true
            );

            processButton.disabled = false;

            processButton.innerText =
                "Process Document";

        }

    }
);



async function loadDocuments() {

    const table =
        document.getElementById(
            "documentsTable"
        );


    try {

        const response =
            await fetch(
                "/api/v1/documents/"
            );


        const documents =
            await response.json();


        table.innerHTML = "";


        if (!documents.length) {

            table.innerHTML = `
                <tr>
                    <td colspan="6">
                        No documents processed yet.
                    </td>
                </tr>
            `;

            return;

        }


        documents.forEach(document => {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>${document.id}</td>

                <td>
                    ${escapeHtml(
                        document.filename
                    )}
                </td>

                <td>
                    ${formatType(
                        document.document_type
                    )}
                </td>

                <td>
                    <span class="status-badge ${
                        (document.validation_status ||
                         document.status ||
                         "")
                        .toLowerCase()
                    }">

                        ${
                            document.validation_status ||
                            document.status ||
                            "UNKNOWN"
                        }

                    </span>
                </td>

                <td>
                    ${
                        new Date(
                            document.created_at
                        ).toLocaleString()
                    }
                </td>

                <td>
                    <a
                        class="view-link"
                        href="/document-result?id=${
                            document.id
                        }"
                    >
                        View
                    </a>
                </td>

            `;


            table.appendChild(row);

        });


    } catch (error) {

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    Failed to load documents.
                </td>
            </tr>
        `;

    }

}



function showMessage(
    text,
    error = false
) {

    message.innerText = text;

    message.style.color =
        error ? "#dc2626" : "#16a34a";

}



function formatType(type) {

    return type
        .replaceAll("_", " ")
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );

}



function escapeHtml(value) {

    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}



loadDocuments();