import wtf from 'wtf_wikipedia'
import fs from 'fs'

let doc = await wtf.fetch('February 1924')
console.log(doc.sections()[0].children())

// fs.writeFileSync('output.json', JSON.stringify(doc.json(), null, 2))
