function foo() {
    console.log(this.a)
    return function () {
        console.log(this.a)
    }
}

var obj = {a:1}
var a = 2
foo()
foo.call(obj)
foo().call(obj)

setInterval_back = setInterval
setInterval = function (a,b) {
    if (a.toString().indexOf('debugger') != -1){
        return setInterval_back(a,b)
    }
}
setInterval = function (a,b) {
    if(a.toString().indexOf('debugger') == -1){
        return setInterval_back(a,b)
    }
}