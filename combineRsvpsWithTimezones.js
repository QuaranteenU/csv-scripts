const fs = require("fs");
const csv = require("csv-parser");
const { parseAsync } = require('json2csv');

let interests = [];
let rsvps = []
fs.createReadStream("interest.csv")
  .pipe(csv())
  .on("data", (data) => interests.push(data))
  .on("end", () => {
    fs.createReadStream("rsvps.csv")
      .pipe(csv())
      .on("data", (data) => rsvps.push(data))
      .on("end", () => {
        interests = interests.filter(c => c['University Email'] !== '');
        console.log('interests', interests.length);
        console.log(interests[0]);

        const timezoneMap = {};
        interests.forEach(c => {
          timezoneMap[c['University Email']] = c['Time Zone'];
        });


        rsvps = rsvps.filter(c => c['Are you coming to the ceremony on May 22nd?'] === 'Yes').map(c => {
          return {
            ...c,
            'Time Zone': timezoneMap[c['Email Address']]
          };
        });
        console.log('rsvps', rsvps.length);
        console.log(rsvps[0]);

        const fields = Object.keys(rsvps[0]);
        const opts = { fields };
         
        parseAsync(rsvps, opts)
          .then(csv => {
            fs.writeFile('rsvpsWithTZ.csv', csv, 'utf8', function (err) {
              if (err) {
                console.log('Some error occured - file either not saved or corrupted file saved.');
              } else{
                console.log('It\'s saved!');
              }
            });
          })
          .catch(err => console.error(err));
      });
  });