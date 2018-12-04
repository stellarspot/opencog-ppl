// P( x and y )
var generateProb = function () {
    var x = flip(0.5)
    var y = flip(0.5)
    return x & y
}

Infer({method: 'enumerate', model: generateProb})

// P( x and y | x or y)
var generateCondProb = function () {
    var x = flip(0.5)
    var y = flip(0.5)
    condition(x || y)
    return x & y
}

Infer({method: 'enumerate', model: generateCondProb})
