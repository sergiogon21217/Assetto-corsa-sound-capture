// Kona N sound mod: probe script for FMOD Studio 1.08.12 (JavaScript, ES5 only).
//
// What it does: prints the structure of the event selected in the Events browser
// (tracks, instruments, parameters, modulators, automation) to the Console window.
// It changes nothing in the project.
//
// Why: FMOD 1.08's scripting object names are not documented online. The output of
// this probe, run on the Kunos template's engine_ext event, shows the exact names
// needed to write a script that builds the Kona N engine events automatically.
//
// Install: copy this file into the "Scripts" folder inside your FMOD project folder
// (next to the .fspro file), then Scripts > Reload in FMOD Studio.
// Use:     select the template's engine_ext event in the Events browser, then
//          Scripts > Kona N > Probe selected event. Window > Console shows the output;
//          select all of it, copy, and send it back.

var KONA_MAX_OBJECTS = 400;

function konaDescribe(obj) {
    var out = [];
    try { out.push("entity=" + obj.entity); } catch (e) {}
    var keys = ["name", "start", "length", "looping", "minimum", "maximum", "position",
                "value", "root", "minimumPitch", "volume", "pitch", "isAsync"];
    for (var i = 0; i < keys.length; i++) {
        try {
            var v = obj[keys[i]];
            if (v !== undefined && typeof v !== "function" && typeof v !== "object") {
                out.push(keys[i] + "=" + v);
            }
        } catch (e) {}
    }
    try { if (obj.audioFile) { out.push("audioFile=" + obj.audioFile.assetPath); } } catch (e) {}
    return out.join("  ");
}

function konaWalk(obj, depth, seen, lines) {
    if (!obj || lines.length > KONA_MAX_OBJECTS || depth > 6) { return; }
    var id;
    try { id = obj.id; } catch (e) { id = null; }
    if (id && seen[id]) { return; }
    if (id) { seen[id] = true; }
    var pad = new Array(depth + 1).join("    ");
    lines.push(pad + konaDescribe(obj));
    var rels;
    try { rels = obj.relationships; } catch (e) { rels = null; }
    if (!rels) { return; }
    for (var name in rels) {
        // don't climb back up to parents/folders/banks, only go down the event tree
        if (name === "folder" || name === "banks" || name === "event" || name === "parent" ||
            name === "mixerGroup" || (name === "masterTrack" && depth > 0)) { continue; }
        var dests;
        try { dests = rels[name].destinations; } catch (e) { dests = null; }
        if (!dests || !dests.length) { continue; }
        lines.push(pad + "  [" + name + "] x" + dests.length);
        for (var j = 0; j < dests.length; j++) {
            konaWalk(dests[j], depth + 1, seen, lines);
        }
    }
}

studio.menu.addMenuItem({
    name: "Kona N\\Probe selected event",
    execute: function () {
        var obj = studio.window.browserCurrent();
        if (!obj) {
            console.log("Kona probe: select an event in the Events browser first.");
            return;
        }
        var ver = "?";
        try { ver = studio.version; } catch (e) {}
        var lines = ["=== Kona probe: FMOD " + ver + " ==="];
        try { lines.push("--- dump() of selected object ---"); obj.dump(); } catch (e) {
            lines.push("dump() not available: " + e);
        }
        lines.push("--- tree ---");
        konaWalk(obj, 0, {}, lines);
        lines.push("=== end (" + lines.length + " lines) ===");
        for (var i = 0; i < lines.length; i++) { console.log(lines[i]); }
    }
});
