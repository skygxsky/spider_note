function foo() {
    console.log(this.a)
}
function doFoo(fn) {
    console.log(this)
    fn()
}
var obj = {a:1,
    foo:function foo() {
    console.log(this.a)
}
}
var a = 2
var obj2 = {a:3,
    doFoo:function doFoo(fn) {
    console.log(this)
    fn()
}}
obj2.doFoo(obj.foo)

Object.defineProperty(document,'cookie',{
    set:function (val) {
        debugger;
        return
    }
})