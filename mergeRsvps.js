const fs = require("fs");
const csv = require("csv-parser");
const { parseAsync } = require("json2csv");

let rsvps = [];
let rsvpsNew = [];
fs.createReadStream("data/rsvpsWithTZ.csv")
  .pipe(csv())
  .on("data", data => rsvps.push(data))
  .on("end", () => {
    fs.createReadStream("data/rsvpsnew.csv")
      .pipe(csv())
      .on("data", data => rsvpsNew.push(data))
      .on("end", () => {
        const emailSet = new Set();
        console.log("rsvps", rsvps.length);
        console.log(rsvps[0]);
        rsvps.forEach(c => emailSet.add(c["Email Address"]));

        rsvpsNew = rsvpsNew.filter(
          c => c["Are you coming to the ceremony on May 22nd?"] === "Yes"
        );
        console.log("rsvpsNew", rsvpsNew.length);
        console.log(rsvpsNew[0]);
        rsvpsNew.forEach(c => emailSet.add(c["Email Address"]));

        console.log("emailSet", emailSet.size); // set size === (rsvps.length + rsvpsNew.length) so we already gucci

        const fields = Object.keys(rsvps[0]);
        const opts = { fields };
        const masterRsvps = rsvps.concat(rsvpsNew);

        parseAsync(masterRsvps, opts)
          .then(csv => {
            fs.writeFile("data/MASTER RSVP.csv", csv, "utf8", function(err) {
              if (err) {
                console.log(
                  "Some error occured - file either not saved or corrupted file saved."
                );
              } else {
                console.log("It's saved!");
              }
            });
          })
          .catch(err => console.error(err));
      });
  });
