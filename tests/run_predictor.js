/*
 * static/js/predictor.js dosyasını Node'da çalıştırır (tests/test_app.py kullanır).
 *
 * Kullanım: node tests/run_predictor.js <model.json>  < başvurular.json
 * Girdi: [{"lang": "tr", "payload": {...}}, ...] (JSON).
 * Çıktı: her biri için predict() sonucu (JSON).
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const model = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const payloads = JSON.parse(fs.readFileSync(0, "utf8"));

const context = { window: { KREDI_MODEL: model } };
const source = fs.readFileSync(path.join(__dirname, "..", "static", "js", "predictor.js"), "utf8");
vm.runInNewContext(source, context);

(async () => {
  const results = [];
  for (const { lang, payload } of payloads) results.push(await context.window.KrediPredictor.predict(payload, lang));
  process.stdout.write(JSON.stringify(results));
})();
