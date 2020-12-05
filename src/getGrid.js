localStorageString = localStorage.getItem("gameState");

var stringOfGrid = localStorageString.slice(localStorageString.indexOf("[["), localStorageString.indexOf("]]"));
var gridIndex = 0, gridSize = 4, grid = new Array(gridSize);
for (var i = 0; i < gridSize; i++) {
  grid[i] = new Array(gridSize);
}
for (var i = 0; i < stringOfGrid.length; i++) {
  if(i == stringOfGrid.indexOf("null", i)){
    grid[gridIndex % gridSize][Math.floor(gridIndex / gridSize)] = 0;
    gridIndex++;
  }
  else if(i == stringOfGrid.indexOf('"value":', i)){
    grid[gridIndex % gridSize][Math.floor(gridIndex / gridSize)] = parseInt(stringOfGrid.slice(i + '"value":'.length ,stringOfGrid.indexOf("}", i)));
    gridIndex++;
  }
}

return grid;
