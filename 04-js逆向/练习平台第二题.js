Function.prototype.constructor = function () {

}
Function.prototype.constructor_bc = Function.prototype.constructor

Function.prototype.constructor = function () {
    if (arguments === 'debugger'){

    }else {
        return Function.prototype.constructor_bc.apply(this,arguments)
    }
}