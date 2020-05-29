const fs = require("fs");
const csv = require("csv-parser");
const { parseAsync } = require("json2csv");

const roundHalf = num => Math.round(num * 2) / 2;
const round2Dec = num => Math.round((num + Number.EPSILON) * 100) / 100;

let rsvps = [];
fs.createReadStream("data/HS - Master RSVPs.csv")
  .pipe(csv())
  .on("data", data => rsvps.push(data))
  .on("end", () => {
    const map = {};
    const counter = {};
    rsvps.forEach(c => {
      if (c["Your school"] === "") c["Your school"] = "Unknown";

      if (!Number.isNaN(parseInt(c["Time Zone"]))) {
        if (map.hasOwnProperty(c["Your school"])) {
          map[c["Your school"]].push(parseInt(c["Time Zone"]));
        } else {
          map[c["Your school"]] = [parseInt(c["Time Zone"])];
        }
      }
      if (counter.hasOwnProperty(c["Your school"])) {
        counter[c["Your school"]] += 1;
      } else {
        counter[c["Your school"]] = 1;
      }
    });

    const schools = [];
    const SEC_PER_PERSON = 30;

    for (let [key, value] of Object.entries(map)) {
      const students = counter[key];
      schools.push({
        School: key,
        "Average Timezone": Math.round(
          value.reduce((sum, val) => {
            return sum + val;
          }, 0) / value.length
        ),
        Students: students,
        Seconds: round2Dec(students * SEC_PER_PERSON),
        Minutes: round2Dec((students * SEC_PER_PERSON) / 60),
        Hours: round2Dec((students * SEC_PER_PERSON) / 60 / 60)
      });
    }

    const fields = Object.keys(schools[0]);
    const opts = { fields };

    parseAsync(schools, opts)
      .then(csv => {
        fs.writeFile("data/school timezones.csv", csv, "utf8", function(err) {
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
