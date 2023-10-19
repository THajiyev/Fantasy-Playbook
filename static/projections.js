var table = document.getElementById('data-table');
var customSearchDiv = document.getElementById("autocompleteDiv");
var tableBody = table.getElementsByTagName('tbody')[0];
var addRowButton = document.getElementById('addRowButton');
var searchBar = document.getElementById('searchBar');
var loadingOverlay = document.getElementById('loading-overlay');
var searchModeOn = false;
var knownList = [];

const sortIndex = 2;
initialize();

function showLoadingOverlay(show) {
    if(show){
        loadingOverlay.style.display = 'flex';
    }
    else{
        loadingOverlay.style.display = 'none';
    }
}

function customAdditionMode(){
    if(searchModeOn){
        customSearchDiv.style.display = "flex";
        searchBar.style.display = "none";
        setOptionsStyle();
        addRowButton.textContent = "Stop Adding";
    }
    else{
        customSearchDiv.style.display = "none";
        searchBar.style.display = "flex";
        addRowButton.textContent = "Add Players";
    }
}

function insert_rows(rows) {
    for (var i = 0; i < rows.length; i++) {
        var newRow = tableBody.insertRow();
        remove_from_knownlist(rows[i][0]);
        for (var j = 0; j < rows[i].length; j++) {
            var newCell = newRow.insertCell(j);
            newCell.textContent = rows[i][j];
        }
    }
}

function add_projections() {
    showLoadingOverlay(true);
    fetch_data('projections').then(function (data) {
        var rows = data.rows;
        insert_rows(rows);
        sortTable(sortIndex);
        showLoadingOverlay(false);
    })
    .catch(function (error) {
        console.error('Error:', error);
        showLoadingOverlay(false);
    });
}

function sortTable(columnIndex) {
    var rows = tableBody.getElementsByTagName('tr');
    var rowsArray = Array.prototype.slice.call(rows);
    rowsArray.sort(function (a, b) {
        var aValue = parseFloat(a.getElementsByTagName('td')[columnIndex].textContent);
        var bValue = parseFloat(b.getElementsByTagName('td')[columnIndex].textContent);
        return bValue - aValue;
    });
    for (var i = 0; i < rowsArray.length; i++) {
        tableBody.appendChild(rowsArray[i]);
    }
}

function filterRows() {
    var searchText = searchBar.value.toLowerCase();
    var rows = tableBody.getElementsByTagName('tr');
    for (var i = 0; i < rows.length; i++) {
        var firstColumn = rows[i].getElementsByTagName('td')[0];
        if (firstColumn) {
            var cellText = firstColumn.textContent.toLowerCase();
            rows[i].style.display = cellText.includes(searchText) ? '' : 'none';
        }
    }
}

document.addEventListener("DOMContentLoaded", function (){
    customAdditionMode();
    add_projections();
    fetch_data('names-fp').then((data) => {
        knownList = data.array;
      })
      .catch((error) => {
        console.error('Error:', error);
    });
})

addRowButton.addEventListener('click', function () {
    searchModeOn = !searchModeOn;
    customAdditionMode();
});

searchBar.addEventListener('input', filterRows);

document.getElementById('autocompleteResults').addEventListener('click', (event) => {
    if (event.target.tagName.toLowerCase() === 'div') {
        const selectedName = event.target.textContent;
          fetch_data("projection:"+selectedName).then((data) => {
            if(data.rows.length==0){
                remove_from_knownlist(selectedName);
            }
            else{
                insert_rows(data.rows);
                sortTable(sortIndex);
            }
          })
          .catch((error) => {
            console.error('Error:', error);
          });
        clear_input()
    }
});