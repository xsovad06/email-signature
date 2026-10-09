#!/usr/bin/env python3
"""Install the HTML signature into Apple Mail.

Writes the signature into every Apple Mail signature store (the iCloud container is the
source of truth; the local ~/Library/Mail/V*/ copy is a mirror Mail restores from iCloud
on launch, so both must be written).

Usage:  quit Mail, then  python3 install-apple-mail.py [SignatureName ...]
Requires Full Disk Access for the terminal or editor running this script.
"""
import plistlib
import quopri
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parent
HTML = REPO / "damian-sova-signature.html"
DEFAULT_TARGETS = ["Redhat", "Damian"]

MIME_HEADERS = (
    "Content-Transfer-Encoding: quoted-printable\n"
    "Content-Type: text/html;\n"
    "\tcharset=utf-8\n"
    "Message-Id: <{msgid}>\n"
    "Mime-Version: 1.0 (Mac OS X Mail 16.0 \\(3864.700.51.1.1\\))\n"
)


def signature_stores():
    stores = [HOME / "Library/Mobile Documents/com~apple~mail/Data/V4/Signatures"]
    stores += sorted((HOME / "Library/Mail").glob("V*/MailData/Signatures"))
    return [s for s in stores if s.is_dir()]


def build_body():
    html = HTML.read_text(encoding="utf-8").strip()
    body = '<head><meta charset="UTF-8"></head><body dir="auto">' + html + "</body>"
    # Mail's parser requires LF line endings; CRLF makes it read the signature as empty.
    return quopri.encodestring(body.encode("utf-8")).decode("ascii")


def main():
    if subprocess.run(["pgrep", "-x", "Mail"], capture_output=True).returncode == 0:
        sys.exit("Mail is running. Quit Mail first, or it will overwrite these changes.")
    if not HTML.is_file():
        sys.exit(f"Signature HTML not found: {HTML}")

    wanted = sys.argv[1:] or DEFAULT_TARGETS
    encoded = build_body()
    stores = signature_stores()
    if not stores:
        sys.exit("No Apple Mail signature stores found (is Full Disk Access granted?)")

    for store in stores:
        index_path = store / "AllSignatures.plist"
        if not index_path.is_file():
            print(f"skip (no AllSignatures.plist): {store}")
            continue
        index = plistlib.loads(index_path.read_bytes())

        changed = False
        for entry in index:
            name = entry.get("SignatureName")
            if name not in wanted:
                continue
            uuid = entry["SignatureUniqueId"]
            path = store / f"{uuid}.mailsignature"
            if not path.is_file():
                print(f"  skip (file missing): {name} -> {path.name}")
                continue
            path.write_bytes((MIME_HEADERS.format(msgid=uuid) + "\n" + encoded).encode("utf-8"))
            # HTML signatures must be flagged rich, or Mail renders them as empty plain text.
            if not entry.get("SignatureIsRich"):
                entry["SignatureIsRich"] = True
                changed = True
            print(f"  wrote {name:10} {path.name[:8]}  {path.stat().st_size} bytes")

        if changed:
            index_path.write_bytes(plistlib.dumps(index))
            print("  updated SignatureIsRich flags")
        print(f"[done] {store}")

    print("\nNow start Mail and check the signature in a new compose window.")


if __name__ == "__main__":
    main()
