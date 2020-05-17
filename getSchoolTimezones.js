const fs = require("fs");
const csv = require("csv-parser");
const { parseAsync } = require('json2csv');

const roundHalf = num => Math.round(num*2)/2;
const round2Dec = num => Math.round((num + Number.EPSILON) * 100) / 100;

let rsvps = []
fs.createReadStream("MASTER RSVP with schools.csv")
  .pipe(csv())
  .on("data", (data) => rsvps.push(data))
  .on("end", () => {
    const map = {};
    rsvps.forEach(c => {
      if (parseInt(c['Time Zone'])) {
        if (map.hasOwnProperty(c['School'])) {
          map[c['School']].push(parseInt(c['Time Zone']));
        } else {
          map[c['School']] = [parseInt(c['Time Zone'])];
        }
      }
    });

    const schools = [];

    for (let [key, value] of Object.entries(map)) {
      schools.push({
        School: key,
        'Average Timezone': value.reduce((sum, val) => {
          return sum + val;
        }, 0) / value.length,
        Students: value.length,
        Seconds: round2Dec(value.length * 20),
        Minutes: round2Dec(value.length * 20 / 60),
        Hours: round2Dec(value.length * 20 / 60 / 60),
      });
    }

    const fields = Object.keys(schools[0]);
    const opts = { fields };
    
    parseAsync(schools, opts)
      .then(csv => {
        fs.writeFile('school timezones.csv', csv, 'utf8', function (err) {
          if (err) {
            console.log('Some error occured - file either not saved or corrupted file saved.');
          } else{
            console.log('It\'s saved!');
          }
        });
      })
      .catch(err => console.error(err));
  });