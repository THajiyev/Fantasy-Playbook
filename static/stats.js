const table = document.getElementById("statsTable");
const noDataAvailable = document.getElementById("no-data");

var players_list = [];
var knownList = [];

const abbreviations= {
  "Target Share":"tgt_sh",
  "Weighted Opportunity Rating":"wopr_y",
  "Receiving Yards Share":"ry_sh",
  "Receiving touchdowns share":"rtd_sh",
  "Receiving Yards Per Team Pass Attempt":"yptmpa"
}

document.addEventListener("DOMContentLoaded", function (){
  fetch_data('names').then((data) => {
    knownList = data.array;
  })
  .catch((error) => {
    console.error('Error:', error);
  });
})

function showTableDisplay(showTable){
  table.style.display = showTable?"table":"none";
}

function showNoDataAvailable(showSymbol){
  noDataAvailable.style.display = showSymbol?"block":"none";
}

function get_abbreviation(full_name){
  if(full_name in abbreviations){
    return abbreviations[full_name];
  }
  else{
    return full_name.toLowerCase().replace(' ','_');
  }
}

function addButtonToCell(cell, player_name) {
  if (cell.tagName.toLowerCase() === "th") {
    const closeButton = document.createElement("button");
    closeButton.classList.add("button-with-close");
    closeButton.addEventListener("click", function() {
      removeColumnByIndex(player_name);
    });
    cell.appendChild(closeButton);
  }
}

function addColumn(values, player_name) {
  const rows = table.getElementsByTagName("tr");
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (i === 0) {
      const newHeaderCell = document.createElement("th");
      newHeaderCell.textContent = player_name;
      addButtonToCell(newHeaderCell, player_name);
      row.appendChild(newHeaderCell);
    } else {
      const newDataCell = document.createElement("td");
      var stat = get_abbreviation(row.cells[0].textContent);
      newDataCell.textContent = roundUp(values[stat], 3);
      row.appendChild(newDataCell);
    }
  }
}

function removeColumnByIndex(player_name) {
  const columnIndex = players_list.indexOf(player_name)+1;
  const rows = table.getElementsByTagName("tr");
  for (let i = 0; i < rows.length; i++) {
    const cells = rows[i].getElementsByTagName(i === 0 ? "th" : "td");
    if (cells.length > columnIndex || (i==0 && cells.length>columnIndex-1)) {
      cells[columnIndex].remove();
    }
  }
  indexToRemove = players_list.indexOf(player_name);
  knownList.push(player_name);
  players_list.splice(indexToRemove, 1);
  showTableDisplay(players_list.length>0);
  showNoDataAvailable(players_list.length==0);
}

document.getElementById('autocompleteResults').addEventListener('click', (event) => {
  if (event.target.tagName.toLowerCase() === 'div') {
      const selectedName = event.target.textContent;
      if(players_list.indexOf(selectedName)==-1){
        fetch_data(selectedName).then((data) => {
          players_list.push(selectedName)
          showTableDisplay(true);
          addColumn(JSON.parse(data), selectedName);
          remove_from_knownlist(selectedName);
          showNoDataAvailable(players_list.length==0);
        })
        .catch((error) => {
          console.error('Error:', error);
          console.log(selectedName);
          console.log(data)
        });
      }
      clear_input();
      hide_suggestions_div(true);
  }
});