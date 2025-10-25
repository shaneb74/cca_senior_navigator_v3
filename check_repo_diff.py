#!/usr/bin/env python3
import os, sys, json, csv, zipfile, hashlib
from datetime import datetime

USAGE = """\
Usage:
  python check_repo_diff.py --init-golden <zip_or_dir>
      Create senior_navigator_golden_manifest.json next to this script.

  python check_repo_diff.py <zip_or_dir> [--golden <path_to_manifest_json>]
      Compare target against golden. If --golden is omitted, looks for
      ./senior_navigator_golden_manifest.json next to this script.

Outputs (written next to this script):
  repo_diff_added.csv
  repo_diff_removed.csv
  repo_diff_changed.csv
  repo_diff_summary.md
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GOLDEN = os.path.join(BASE_DIR, "senior_navigator_golden_manifest.json")

def sha256_file(fp):
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def build_manifest_from_dir(root):
    records = {}
    for base, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(base, fn)
            rel = os.path.relpath(p, root)
            size = os.path.getsize(p)
            records[rel] = {"size_bytes": int(size), "sha256": sha256_file(p)}
    return records

def build_manifest_from_zip(zip_path):
    records = {}
    with zipfile.ZipFile(zip_path, 'r') as z:
        for zi in z.infolist():
            if zi.is_dir():
                continue
            rel = zi.filename
            with z.open(zi) as f:
                data = f.read()
            size = len(data)
            sha = hashlib.sha256(data).hexdigest()
            records[rel] = {"size_bytes": int(size), "sha256": sha}
    return records

def write_csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def save_golden(manifest, out_path):
    payload = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "source": "local init",
        "total_files": len(manifest),
        "total_size_bytes": sum(m["size_bytes"] for m in manifest.values()),
        "files": manifest,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

def load_golden(path):
    with open(path, "r") as f:
        return json.load(f)["files"]

def manifest_from_target(target):
    if os.path.isdir(target):
        return build_manifest_from_dir(target)
    if zipfile.is_zipfile(target):
        return build_manifest_from_zip(target)
    print("Target must be a directory or a .zip file")
    sys.exit(3)

def do_init_golden(target, golden_path):
    cur = manifest_from_target(target)
    save_golden(cur, golden_path)
    print(f"Golden created: {golden_path}")
    print(f"Files: {len(cur)}  Total bytes: {sum(v['size_bytes'] for v in cur.values())}")

def do_compare(target, golden_path):
    if not os.path.exists(golden_path):
        print(f"Golden manifest not found: {golden_path}")
        sys.exit(2)
    golden = load_golden(golden_path)
    cur = manifest_from_target(target)

    golden_paths = set(golden.keys())
    cur_paths = set(cur.keys())

    added = sorted(cur_paths - golden_paths)
    removed = sorted(golden_paths - cur_paths)
    common = sorted(golden_paths & cur_paths)

    changed = []
    for p in common:
        g = golden[p]; c = cur[p]
        if g["sha256"] != c["sha256"] or g["size_bytes"] != c["size_bytes"]:
            changed.append((p, g["size_bytes"], c["size_bytes"], g["sha256"], c["sha256"]))

    write_csv(os.path.join(BASE_DIR, "repo_diff_added.csv"),
              [(p, cur[p]["size_bytes"], cur[p]["sha256"]) for p in added],
              ["path","size_bytes","sha256"])
    write_csv(os.path.join(BASE_DIR, "repo_diff_removed.csv"),
              [(p, golden[p]["size_bytes"], golden[p]["sha256"]) for p in removed],
              ["path","size_bytes","sha256"])
    write_csv(os.path.join(BASE_DIR, "repo_diff_changed.csv"),
              changed, ["path","old_size_bytes","new_size_bytes","old_sha256","new_sha256"])

    summary_path = os.path.join(BASE_DIR, "repo_diff_summary.md")
    with open(summary_path, "w") as f:
        f.write(f"# Repo Diff Summary\n\n")
        f.write(f"- Generated: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"- Target: {target}\n")
        f.write(f"- Golden: {golden_path}\n\n")
        f.write(f"## Counts\n")
        f.write(f"- Added: {len(added)}\n")
        f.write(f"- Removed: {len(removed)}\n")
        f.write(f"- Changed: {len(changed)}\n\n")

        def sample(lst, n=20):
            return lst[:n]

        if added:
            f.write("## Added (sample)\n")
            for p in sample(added):
                f.write(f"- {p}\n")
            f.write("\n")
        if removed:
            f.write("## Removed (sample)\n")
            for p in sample(removed):
                f.write(f"- {p}\n")
            f.write("\n")
        if changed:
            f.write("## Changed (sample)\n")
            for p, old_sz, new_sz, *_ in sample(changed):
                f.write(f"- {p} | {old_sz} → {new_sz}\n")
            f.write("\n")

    print("Diff complete.")
    print("Outputs written next to this script:")
    print("  repo_diff_added.csv")
    print("  repo_diff_removed.csv")
    print("  repo_diff_changed.csv")
    print("  repo_diff_summary.md")

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return

    if argv[0] == "--init-golden":
        if len(argv) != 2:
            print(USAGE); sys.exit(1)
        target = argv[1]
        do_init_golden(target, DEFAULT_GOLDEN)
        return

    # Compare mode
    target = argv[0]
    if len(argv) >= 3 and argv[1] == "--golden":
        golden_path = argv[2]
    else:
        golden_path = DEFAULT_GOLDEN

    do_compare(target, golden_path)

if __name__ == "__main__":
    main(sys.argv[1:])