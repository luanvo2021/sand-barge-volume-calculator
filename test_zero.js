
const { tinhTheTichCatXaLan } = require('./MultiTierBargeEngine.js');

const layers = [
    { name: "P1", type: "Đáy bằng", L: 50.0, B: 10.0, H: 2.0 }
];

// Test case with do_hut_cat = 0 (Full barge: 50 * 10 * 2 = 1000 m3)
const resZero = tinhTheTichCatXaLan(layers, 1, { do_hut_cat: 0 });
console.log("JS with do_hut_cat = 0:", resZero);

if (Math.abs(resZero.the_tich_m3 - 1000.0) < 1e-3) {
    console.log("SUCCESS: JS correctly handled do_hut_cat = 0!");
} else {
    console.log("FAILURE: JS still fell back to default!");
    process.exit(1);
}
