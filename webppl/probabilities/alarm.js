var isAlarm = function(burglary, earthquake) {
    if(burglary && flip(0.95)) return true
    if(earthquake && flip(0.3)) return true
    if(flip(0.001)) return true // false alarm
    return false
}
var generate = function () {
    var burglary = flip(0.001)
    var earthquake = flip(0.002)
    var alarm = isAlarm(burglary, earthquake)
    return alarm
}
Infer({method: 'enumerate', model: generate})
