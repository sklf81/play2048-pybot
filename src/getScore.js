var string = localStorage.getItem('gameState');
var wantedParameterName = 'score';
var indexOfString = string.indexOf(wantedParameterName);
var scoreString = '';
for(var i = indexOfString + wantedParameterName.length + 2; string[i] >= '0' && string[i] <= '9'; i++){
  scoreString += string[i];
}
return parseInt(scoreString);