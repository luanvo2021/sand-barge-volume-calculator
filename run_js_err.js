
const { tinhTheTichCatXaLan } = require('./MultiTierBargeEngine.js');
try {
    tinhTheTichCatXaLan([{"name": "P1", "type": "Đáy chữ V", "L": 60.0, "B": 10.0, "C": 4.0}], 1, {do_hut_cat: 0.5});
    console.log("FAIL");
} catch(e) {
    console.log("SUCCESS:" + e.message);
}
