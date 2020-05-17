const fs = require("fs");
const csv = require("csv-parser");
const { parseAsync } = require('json2csv');

const rawdata = fs.readFileSync('university_map.json');
const university_map = JSON.parse(rawdata);

let rsvps = []
fs.createReadStream("data/MASTER RSVP.csv")
  .pipe(csv())
  .on("data", (data) => rsvps.push(data))
  .on("end", () => {
    rsvps = rsvps.map(c => {
      const domain = c['Email Address'].split('@')[1];
      return {
        ...c,
        School: university_map.hasOwnProperty(domain) ? university_map[domain] : ''
      }
    });


    const fields = Object.keys(rsvps[0]);
    const opts = { fields };
    
    parseAsync(rsvps, opts)
      .then(csv => {
        fs.writeFile('data/MASTER RSVP with schools.csv', csv, 'utf8', function (err) {
          if (err) {
            console.log('Some error occured - file either not saved or corrupted file saved.');
          } else{
            console.log('It\'s saved!');
          }
        });
      })
      .catch(err => console.error(err));
  });