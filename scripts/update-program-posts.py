#!/usr/bin/env python3
"""Writes the tables of the program posts from the programs themselves.

Each program post names its program in <meta name="tp:program" content="fiveByFive"> and marks
where the tables go with pairs of comments; what stands between them is written here, from
the JSON the app repository exports (Branding/capture-blog.sh data writes
Branding/Blog/programs.json), so a post never says what the app doesn't do:

  <!-- program-facts -->     level, days a week, cycle, length, equipment, progression
  <!-- program-cycle -->     the cycle's days, sessions and rest days
  <!-- program-sessions -->  every session's exercises with their sets, rest and notes
  <!-- program-phases -->    the phases, their focus, cycles and deloads
  <!-- program-waves -->     the lifts whose sets change from week to week, week by week
  <!-- program-muscles -->   the work sets per muscle in a week

Everything else in a post is written by hand. Run it again whenever the programs change, in
_drafts/ and blog/ alike.

Usage: scripts/update-program-posts.py [path to the app repository, default ../Training Planner]
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "Training Planner")
DATA = os.path.join(APP, "Branding", "Blog", "programs.json")

EQUIPMENT = {
    "barbell": "Barbell, rack, bench and a pull-up bar",
    "gym": "A gym with machines and cables",
    "dumbbells": "Dumbbells and a bench",
    "bodyweight": "Little or none",
}
KIND_WORDS = {"Top set": "top set", "Back-off": "back-off", "Working": "", "Pyramid": "pyramid",
              "Drop set": "drop set", "Rest-pause": "rest-pause", "Myo-reps": "myo-reps"}
TECHNIQUES = {"Drop set": 0, "Rest-pause": 20, "Myo-reps": 15}


def esc(text):
    return html.escape(str(text), quote=False)


def number(value):
    """2.5 → "2.5", 3.0 → "3"."""
    return f"{value:g}"


def percent(share):
    return number(round(share * 100, 1)) + " %"


def counted(count, word, plural=None):
    return f"{count} {word if count == 1 else (plural or word + 's')}"


def reps_text(group, measure):
    unit = " s" if measure == "time" else (" min" if measure == "cardio" else "")
    reps = str(group["reps"]) + (f"–{group['repsTop']}" if group.get("repsTop") else "")
    return reps + unit


def group_text(group, measure, bodyweight):
    kind = group["kind"]
    count = group["count"]
    if kind == "Pyramid":
        step = group.get("repsStep") or 2
        reps = [group["reps"] - step * i for i in range(count)]
        text = " › ".join(str(max(r, 1)) for r in reps)
        weight = group.get("weightStep")
        more = f", +{number(weight)} kg a set" if weight else ""
        return f"Pyramid {text}{more}"
    if kind in TECHNIQUES:
        return f"+ {counted(count, KIND_WORDS[kind], KIND_WORDS[kind] if kind != 'Drop set' else 'drop sets')}" + (
            f" of {group['reps']}" if kind != "Drop set" else "")
    text = f"{count} × {reps_text(group, measure)}"
    if group.get("toFailure"):
        text += ", last set as many as you can" if count > 1 else ", as many as you can"
    if group.get("percentOfMax"):
        text += f" at {percent(group['percentOfMax'])}"
    words = KIND_WORDS.get(kind, "")
    return f"{words.capitalize()} {text}" if words else text


def target_text(target, exercise):
    parts = [group_text(g, exercise["measure"], exercise["bodyweight"]) for g in target["sets"]]
    text = " · ".join(parts)
    if target.get("rpe"):
        text += f" · RPE {target['rpe']}"
    return text


def rest_text(seconds):
    if seconds >= 120 and seconds % 60 == 0:
        return f"{seconds // 60} min"
    if seconds > 90:
        return f"{number(seconds / 60)} min"
    return f"{seconds} s"


def session_minutes(session):
    """About how long a session takes, the way the app's designer reckons it: warm-up, each
    set's work and rest (shared in a superset), a minute between exercises."""
    seconds = 8 * 60
    for exercise in session["exercises"]:
        paired = bool(exercise["superset"])
        for group in exercise["baseline"]["sets"]:
            middle = (group["reps"] + (group.get("repsTop") or group["reps"])) / 2
            if group["kind"] == "Pyramid":
                middle = group["reps"] - (group.get("repsStep") or 2) * (group["count"] - 1) / 2
            work = middle * 3.5 + 10 if exercise["measure"] == "reps" else middle + 10
            if exercise["measure"] == "cardio":
                work = middle * 60
            rest = TECHNIQUES.get(group["kind"], min(max(exercise["rest"], 30), 300) * (0.5 if paired else 1))
            seconds += group["count"] * (work + rest)
        seconds += 60
    return int(round(seconds / 60 / 5) * 5)


def notes_text(exercise):
    notes = exercise["notes"].strip()
    extras = []
    if exercise.get("tempo"):
        extras.append(f"Tempo {exercise['tempo']}")
    if exercise["unilateral"] and "per side" not in notes.lower() and "per leg" not in notes.lower():
        extras.append("One side at a time")
    return " ".join(filter(None, [notes] + [e + "." for e in extras]))


def progression_text(exercise):
    if exercise["incrementsBy"] == "reps":
        return f"{exercise['progression']}, +{number(exercise['increment'])} rep"
    if exercise["progression"] == "As planned":
        return "As planned (% of 1RM)"
    return f"{exercise['progression']}, +{number(exercise['increment'])} kg"


def facts(program):
    weeks = program["totalDays"] / 7
    per_week = program["sessionsPerWeek"]
    days = number(round(per_week, 1))
    phases = len(program["blocks"])
    length = f"{number(round(weeks, 1))} weeks"
    sessions = len(program["trainingDays"])
    cycle = f"{program['cycleLength']} days, {counted(sessions, 'session')}"
    items = [
        ("Level", program["level"]),
        ("Days a week", days),
        ("One cycle", cycle),
        ("Length", f"{length} in {counted(phases, 'phase')}"),
        ("Equipment", EQUIPMENT[program["equipment"]]),
        ("Goal", program["goal"]),
    ]
    rows = "".join(f"\n        <li><span>{esc(k)}</span><strong>{esc(v)}</strong></li>" for k, v in items)
    return f'\n      <ul class="facts-grid">{rows}\n      </ul>\n      '


def cycle(program):
    by_day = {d["day"]: d["session"] for d in program["schedule"]}
    items = []
    for day in range(1, program["cycleLength"] + 1):
        session = by_day.get(day)
        css = "" if session else ' class="rest"'
        items.append(f'\n        <li{css}><span>Day {day}</span>{esc(session or "Rest")}</li>')
    return f'\n      <ol class="cycle-strip" aria-label="One cycle, day by day">{"".join(items)}\n      </ol>\n      '


def sessions(program):
    blocks = program["blocks"]
    first = blocks[0]
    out = []
    for s_index, session in enumerate(first["sessions"]):
        rows = []
        for e_index, exercise in enumerate(session["exercises"]):
            # Lifts that change from phase to phase, by place in the session
            names = []
            for block in blocks:
                match = [x for x in block["sessions"] if x["name"] == session["name"]]
                if match and e_index < len(match[0]["exercises"]):
                    name = match[0]["exercises"][e_index]["name"]
                    if name not in names:
                        names.append(name)
            name = " › ".join(esc(n) for n in names)
            if len(names) > 1:
                name += "<small>A new lift each phase</small>"
            group = f'<span class="group">{esc(exercise["superset"])}</span>' if exercise["superset"] else ""
            notes = notes_text(exercise)
            sets = esc(target_text(exercise["baseline"], exercise))
            rows.append(
                f"\n            <tr><td>{group}{name}</td><td>{sets}</td>"
                f'<td class="num">{rest_text(exercise["rest"])}</td>'
                f"<td>{esc(progression_text(exercise))}{f'<small>{esc(notes)}</small>' if notes else ''}</td></tr>")
        minutes = session_minutes(session)
        out.append(
            f'\n      <div class="table-wrap">\n        <table>\n          <caption>{esc(session["name"])}'
            f' <span class="muted">· about {minutes} min</span></caption>'
            f'\n          <thead><tr><th scope="col">Exercise</th><th scope="col">Sets</th>'
            f'<th scope="col" class="num">Rest</th><th scope="col">Progression and notes</th></tr></thead>'
            f'\n          <tbody>{"".join(rows)}\n          </tbody>\n        </table>\n      </div>')
    return "".join(out) + "\n      "


def phases(program):
    rows = []
    week = 1
    for block in program["blocks"]:
        cycles = block["cycles"]
        days = cycles * program["cycleLength"]
        deloads = [c["number"] for c in block["cycleTargets"] if c["deload"]]
        start_week = week
        week += days / 7
        weeks = f"{number(round(start_week, 1))}–{number(round(week - 1 / 7, 1))}" if days > 7 else number(start_week)
        deload = f"Cycle {deloads[0]}, the last" if deloads and deloads[0] == cycles else (
            ", ".join(f"Cycle {d}" for d in deloads) if deloads else "None")
        rows.append(f"\n            <tr><td>{esc(block['name'])}</td><td>{esc(block['focus'])}</td>"
                    f'<td class="num">{cycles}</td><td class="num">{number(round(days / 7, 1))}</td><td>{esc(deload)}</td></tr>')
    return ('\n      <div class="table-wrap">\n        <table>\n          <thead><tr><th scope="col">Phase</th>'
            '<th scope="col">Focus</th><th scope="col" class="num">Cycles</th><th scope="col" class="num">Weeks</th>'
            f'<th scope="col">Deload</th></tr></thead>\n          <tbody>{"".join(rows)}\n          </tbody>\n'
            '        </table>\n      </div>\n      ')


def waves(program):
    """The lifts whose sets the program changes cycle by cycle: a table per phase, and one for the
    phases that repeat the same wave ("Base wave, Build wave and Peak wave")."""
    tables = []
    for block in program["blocks"]:
        changing = {}
        for cyc in block["cycleTargets"]:
            for name, target in cyc["targets"].items():
                changing.setdefault(name, {})[cyc["number"]] = target
        if not changing:
            continue
        exercises = {e["name"]: e for s in block["sessions"] for e in s["exercises"]}
        names = [n for n in exercises if n in changing]
        if not names:
            continue
        # One table per phase: a column per cycle, a row per lift
        numbers = [c["number"] for c in block["cycleTargets"]]
        deloads = {c["number"] for c in block["cycleTargets"] if c["deload"]}
        unit = "Week" if program["cycleLength"] == 7 else "Cycle"
        head = "".join(f'<th scope="col">{"Deload" if n in deloads else f"{unit} {n}"}</th>' for n in numbers)
        rows = []
        for name in names:
            cells = []
            for n in numbers:
                target = changing[name].get(n)
                if target:
                    cells.append(f"<td>{esc(target_text(target, exercises[name]))}</td>")
                elif n in deloads:
                    cells.append("<td>Half the sets, about 10 % lighter</td>")
                else:
                    cells.append(f"<td>{esc(target_text(exercises[name]['baseline'], exercises[name]))}</td>")
            rows.append(f"\n            <tr><th scope=\"row\">{esc(name)}</th>{''.join(cells)}</tr>")
        body = f'\n          <thead><tr><th scope="col">Lift</th>{head}</tr></thead>\n          <tbody>{"".join(rows)}\n          </tbody>'
        if tables and tables[-1][1] == body:
            tables[-1][0].append(block)
        else:
            tables.append(([block], body))
    out = []
    for blocks, body in tables:
        names = [b["name"] for b in blocks]
        title = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        focuses = sorted({b["focus"].lower() for b in blocks})
        # The focus only where the name doesn't say it already ("Power", not "Power · power")
        focus = "" if all(f in title.lower() for f in focuses) else f' <span class="muted">· {esc(" and ".join(focuses))}</span>'
        out.append(f'\n      <div class="table-wrap">\n        <table>\n          <caption>{esc(title)}{focus}</caption>'
                   f'{body}\n        </table>\n      </div>')
    return ("".join(out) + "\n      ") if out else "\n      "


def muscles(program):
    per_week = 7 / program["cycleLength"]
    items = []
    for m in program["muscles"]:
        sets = m["setsPerCycle"] * per_week
        if sets < 0.5 or m["muscle"] in ("", "Other"):
            continue
        items.append(f"\n            <tr><td>{esc(m['muscle'])}</td><td class=\"num\">{number(round(sets, 1))}</td></tr>")
    return ('\n      <div class="table-wrap">\n        <table>\n          <thead><tr><th scope="col">Muscle</th>'
            f'<th scope="col" class="num">Work sets a week</th></tr></thead>\n          <tbody>{"".join(items)}'
            '\n          </tbody>\n        </table>\n      </div>\n      ')


WRITERS = {"program-facts": facts, "program-cycle": cycle, "program-sessions": sessions, "program-phases": phases,
           "program-waves": waves, "program-muscles": muscles}


def main():
    programs = {p["id"]: p for p in json.load(open(DATA, encoding="utf-8"))}
    written = 0
    for folder in ("_drafts", "blog"):
        path = os.path.join(ROOT, folder)
        if not os.path.isdir(path):
            continue
        for name in sorted(os.listdir(path)):
            if not name.endswith(".html"):
                continue
            file = os.path.join(path, name)
            text = open(file, encoding="utf-8").read()
            found = re.search(r'<meta name="tp:program" content="([^"]+)"', text)
            if not found:
                continue
            program = programs.get(found.group(1))
            if not program:
                print(f"{folder}/{name}: no program {found.group(1)} in {DATA}")
                continue
            for marker, writer in WRITERS.items():
                pattern = r"(<!-- %s -->).*?(<!-- /%s -->)" % (marker, marker)
                text = re.sub(pattern, lambda m: m.group(1) + writer(program) + m.group(2), text, flags=re.S)
            open(file, "w", encoding="utf-8").write(text)
            written += 1
    print(f"{written} program posts written from {os.path.relpath(DATA, ROOT)}")


if __name__ == "__main__":
    main()
