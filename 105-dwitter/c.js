const fs = require('fs')

const b = fs.readFileSync("test.js")

let s = ""
b.forEach(c=>{
  let hx = Number(c).toString(16)
  if (hx.length == 1) {
    hx = "0" + hx
  }
  s += "%" + hx
})

s = s.replace(/%0a/g,'')
s = s.replace(/%(..)%(..)/g, '%u$1$2')
s = unescape(s)

s = "eval(unescape(escape`" + s + "`.replace(/u(..)/g,'$1%')))"

console.log(s)



