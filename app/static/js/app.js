// =========================================================
// MEDICORE HOSPITAL MANAGEMENT SYSTEM
// MAIN JAVASCRIPT
// =========================================================


// =========================================================
// SQL LABORATORY
// =========================================================

function setSQL(query) {

    const editor = document.getElementById("sqlQuery");

    if (!editor) {
        return;
    }

    editor.value = query;

    editor.focus();
}


// =========================================================
// CLEAR SQL
// =========================================================

function clearSQLQuery() {

    const editor = document.getElementById("sqlQuery");

    if (!editor) {
        return;
    }

    editor.value = "";

    const result = document.getElementById("queryResult");
    const status = document.getElementById("queryStatus");

    if (result) {

        result.innerHTML = `
            <div class="empty-query">

                <div class="empty-query-icon">
                    ⌘
                </div>

                <h3>No query executed</h3>

                <p>
                    Enter a SQL query or choose a quick query above.
                </p>

            </div>
        `;
    }

    if (status) {

        status.textContent = "Ready";
        status.className = "query-status";
    }

}


// =========================================================
// RUN SQL QUERY
// =========================================================

async function runSQLQuery() {

    const editor = document.getElementById("sqlQuery");
    const result = document.getElementById("queryResult");
    const status = document.getElementById("queryStatus");

    if (!editor || !result) {
        return;
    }

    const query = editor.value.trim();

    if (!query) {

        result.innerHTML = `
            <div class="query-error">
                ⚠ Please enter a SQL query.
            </div>
        `;

        if (status) {
            status.textContent = "Error";
            status.className = "query-status error";
        }

        return;
    }


    // Loading state

    result.innerHTML = `
        <div class="query-loading">
            <div class="loading-spinner"></div>
            <p>Executing query...</p>
        </div>
    `;

    if (status) {

        status.textContent = "Running...";
        status.className = "query-status running";
    }


    try {

        const response = await fetch("/api/query", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query: query
            })

        });


        const data = await response.json();


        // ERROR

        if (!data.success) {

            result.innerHTML = `
                <div class="query-error">

                    <strong>⚠ Query Error</strong>

                    <p>
                        ${escapeHTML(data.error || "Something went wrong.")}
                    </p>

                </div>
            `;

            if (status) {

                status.textContent = "Error";
                status.className = "query-status error";
            }

            return;
        }


        // NO RESULTS

        if (!data.rows || data.rows.length === 0) {

            result.innerHTML = `
                <div class="empty-query">

                    <div class="empty-query-icon">
                        ✓
                    </div>

                    <h3>Query executed successfully</h3>

                    <p>
                        The query returned no rows.
                    </p>

                </div>
            `;

            if (status) {

                status.textContent = "Success";
                status.className = "query-status success";
            }

            return;
        }


        // BUILD TABLE

        const rows = data.rows;

        const columns = Object.keys(rows[0]);

        let tableHTML = `
            <div class="result-count">
                ${rows.length} record${rows.length === 1 ? "" : "s"} returned
            </div>

            <div class="result-table-wrapper">

                <table class="sql-result-table">

                    <thead>
                        <tr>
        `;


        columns.forEach(column => {

            tableHTML += `
                <th>${escapeHTML(column)}</th>
            `;

        });


        tableHTML += `
                        </tr>
                    </thead>

                    <tbody>
        `;


        rows.forEach(row => {

            tableHTML += `<tr>`;

            columns.forEach(column => {

                let value = row[column];

                if (value === null || value === undefined) {
                    value = "NULL";
                }

                tableHTML += `
                    <td>${escapeHTML(String(value))}</td>
                `;

            });

            tableHTML += `</tr>`;

        });


        tableHTML += `
                    </tbody>

                </table>

            </div>
        `;


        result.innerHTML = tableHTML;


        if (status) {

            status.textContent = "Success";
            status.className = "query-status success";
        }


    } catch (error) {

        result.innerHTML = `
            <div class="query-error">

                <strong>⚠ Connection Error</strong>

                <p>
                    Could not communicate with the server.
                </p>

            </div>
        `;

        if (status) {

            status.textContent = "Connection Error";
            status.className = "query-status error";
        }

    }

}


// =========================================================
// HTML ESCAPE
// =========================================================

function escapeHTML(value) {

    return value
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// =========================================================
// KEYBOARD SHORTCUT
// CTRL + ENTER → RUN QUERY
// =========================================================

document.addEventListener("keydown", function(event) {

    if (
        event.ctrlKey &&
        event.key === "Enter"
    ) {

        const editor = document.getElementById("sqlQuery");

        if (editor) {

            event.preventDefault();

            runSQLQuery();
        }

    }

});