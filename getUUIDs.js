const fs = require("fs");
const csv = require("csv-parser");
const { parseAsync } = require("json2csv");
const fetch = require("node-fetch");

const fetchUUID = async username => {
  const response = await fetch(
    `https://api.ashcon.app/mojang/v2/user/${username}`,
    { method: "GET" }
  );
  const data = await response.json();
  return data;
};

let rsvps = [];
fs.createReadStream("data/final schedule.csv")
  .pipe(csv())
  .on("data", data => rsvps.push(data))
  .on("end", async () => {
    const withUUIDs = await Promise.all(
      rsvps.map(async c => {
        if (
          c[
            "I confirm I have a Minecraft Java Edition account or will get one before the ceremony"
          ] === "Yup, I got it!"
        ) {
          const data = await fetchUUID(c["Your Minecraft Username"]);
          c["UUID"] = data.uuid;
          if (data.textures) {
            c["Slim"] = data.textures.slim;
            c["Skin"] = data.textures.skin.url;
          } else {
            c["Slim"] = "";
            c["Skin"] = "";
          }

          return c;
        } else {
          c["UUID"] = "";
          c["Slim"] = "";
          c["Skin"] = "";
          return c;
        }
      })
    );

    const fields = Object.keys(withUUIDs[0]);
    const opts = { fields };

    parseAsync(withUUIDs, opts)
      .then(csv => {
        fs.writeFile(
          "data/final schedule with uuids.csv",
          csv,
          "utf8",
          function(err) {
            if (err) {
              console.log(
                "Some error occured - file either not saved or corrupted file saved."
              );
            } else {
              console.log("It's saved!");
            }
          }
        );
      })
      .catch(err => console.error(err));
  });
