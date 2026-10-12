#!/usr/bin/env python3
"""Reconcile authoritative escalations against the hand-maintained watch list."""

import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "extracted" / "roll-call"
DB = ROOT / "case_file" / "intake.db"
CSV = ROOT / "case_file" / "watchlist.csv"


def main() -> None:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    # Confirm that the supplied hand-list export matches its database snapshot.
    with CSV.open(newline="") as f:
        csv_rows = list(csv.DictReader(f))
    db_rows = con.execute(
        "SELECT subject_id, handle, first_logged, assessed_level "
        "FROM watchlist ORDER BY subject_id"
    ).fetchall()
    assert [
        (r["subject_id"], r["handle"], r["first_logged"], r["assessed_level"])
        for r in csv_rows
    ] == [tuple(r) for r in db_rows]

    # Reconcile by person_id, as protocol.md requires.  This avoids falsely
    # treating the two alias handles as additional missing subjects.
    escalated_people = {
        r[0]
        for r in con.execute(
            "SELECT DISTINCT i.person_id "
            "FROM escalations e JOIN identities i ON i.handle = e.handle"
        )
    }
    listed_people = {
        r[0]
        for r in con.execute(
            "SELECT DISTINCT i.person_id "
            "FROM watchlist w JOIN identities i ON i.handle = w.handle"
        )
    }
    missing_people = sorted(escalated_people - listed_people)
    assert len(missing_people) == 2, missing_people

    qmarks = ",".join("?" for _ in missing_people)
    handles = [
        r[0]
        for r in con.execute(
            f"SELECT handle FROM identities WHERE person_id IN ({qmarks}) "
            "AND is_primary = 1",
            missing_people,
        )
    ]
    assert len(handles) == 2, handles

    normalized = sorted((h.lower() for h in handles), key=str.casefold)
    print("missing people:", ", ".join(missing_people))
    print("missing primary handles:", ", ".join(handles))
    payload = "_".join(normalized)
    print("payload:", payload)
    print("challenge.md spelling:", f"csaw{{{payload}}}")
    print("EVENT.md spelling:", f"csawctf{{{payload}}}")


if __name__ == "__main__":
    main()
