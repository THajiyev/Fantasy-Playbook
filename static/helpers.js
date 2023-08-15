const baseUrl = 'http://127.0.0.1:5000/'
const searchInput = document.getElementById('searchInput');
const autocompleteResults = document.getElementById('autocompleteResults');

function hide_suggestions_div(hide){
  autocompleteResults.style.display=hide?"none":"block";
}

function remove_from_knownlist(player_name){
  indexToRemove = knownList.indexOf(player_name);
  knownList.splice(indexToRemove, 1);
}

hide_suggestions_div(true);

searchInput.addEventListener('input', () => {
  const searchText = searchInput.value.trim().toLowerCase();
  var filteredOptions = searchText==""?[]:knownList.filter(option =>
    option.toLowerCase().includes(searchText)
  );
  displayAutocompleteResults(filteredOptions);
});

function clear_input(){
  searchInput.value = '';
  hide_suggestions_div(true);
}

function displayAutocompleteResults(options) {
  autocompleteResults.innerHTML = '';
  const maxResults = Math.min(options.length, 5);
  for (let i = 0; i < maxResults; i++) {
    const option = document.createElement('div');
    option.textContent = options[i];
    option.addEventListener('click', () => {
      searchInput.value = options[i];
      autocompleteResults.innerHTML = '';
    });
    autocompleteResults.appendChild(option);
  }
  hide_suggestions_div(options.length==0)
}

async function fetch_data(input){
    try {
      const response = await fetch(`${baseUrl}/data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain',
        },
        body: input 
      });
      if (!response.ok) {
        throw new Error('Failed to fetch.');
      }
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
}

function roundUp(number, places) {
    const powerOf10 = Math.pow(10, places)
    if (Math.floor(number * powerOf10) !== number * powerOf10) {
        const roundedNumber = Math.ceil(number * powerOf10) / powerOf10;
        return roundedNumber.toFixed(places);
    } else {
        return number.toString();
    }
}

function setOptionsStyle(){
  var inputBottom = searchInput.getBoundingClientRect().bottom;
  autocompleteResults.style.marginTop = inputBottom+"px"
}