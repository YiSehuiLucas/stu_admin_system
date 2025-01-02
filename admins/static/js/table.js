document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#dataTable tbody");
    const prevButton = document.querySelector("#prevPage");
    const nextButton = document.querySelector("#nextPage");
    const currentPageSpan = document.querySelector("#currentPage");
    const totalPagesSpan = document.querySelector("#totalPages");

    const data = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        name: `名称${i + 1}`,
        description: `描述信息${i + 1}`
    }));

    const rowsPerPage = 10;
    let currentPage = 1;

    const renderTable = () => {
        tableBody.innerHTML = ""; // 清空表格
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const pageData = data.slice(start, end);

        pageData.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${row.id}</td>
                <td>${row.name}</td>
                <td>${row.description}</td>
                <td>${row.id}</td>
            `;
            tableBody.appendChild(tr);
        });

        updatePagination();
    };

    const updatePagination = () => {
        const totalPages = Math.ceil(data.length / rowsPerPage);
        totalPagesSpan.textContent = totalPages;
        currentPageSpan.textContent = currentPage;

        prevButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage === totalPages;

        prevButton.classList.toggle("disabled", currentPage === 1);
        nextButton.classList.toggle("disabled", currentPage === totalPages);
    };

    prevButton.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
        }
    });

    nextButton.addEventListener("click", () => {
        const totalPages = Math.ceil(data.length / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
        }
    });

    renderTable(); // 初次渲染表格
});
