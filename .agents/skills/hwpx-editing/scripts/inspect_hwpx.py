#!/usr/bin/env python3
"""
inspect_hwpx.py — dump the structure of an HWPX so you can plan an edit safely.

Usage:
    python inspect_hwpx.py FILE.hwpx [--text] [--breaks]

Shows, per section: paragraph/table/pic/equation/field counts, linesegarray
count, and paragraphs carrying pageBreak/columnBreak (the usual culprit behind
"a heading split off from its content" — see §6-A). With --text it prints the
real body text (endnotes/memos excluded via own()); with --breaks it lists every
paragraph that carries a page/column break plus its paraPrIDRef.

Breaks hide in TWO places: the paragraph's own pageBreak attribute AND its paraPr's
<hh:breakSetting pageBreakBefore="1"> in header.xml. Both are listed. (2026-10-12: a
docx->hwpx conversion put pageBreakBefore on a paraPr; a build cloned it for every
caption, so each table and each figure caption started a new page. The attribute-only
listing showed nothing wrong, and four blind layout fixes were tried before the header
was read.)
"""
import argparse
import sys
import zipfile

# Force UTF-8 console output so non-ASCII glyphs in our messages (—, «», 한글)
# never crash on a Windows cp949 console (UnicodeEncodeError). No-op where the
# stream is already UTF-8, or where reconfigure() is unavailable (Python <3.7,
# or a redirected/replaced stream) — hence the broad guard.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError, OSError):
    pass

import hwpxlib as H


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect HWPX structure.")
    ap.add_argument("file", help="the .hwpx to inspect")
    ap.add_argument("--text", action="store_true", help="print real body text per paragraph")
    ap.add_argument("--breaks", action="store_true", help="list paragraphs with page/column breaks")
    args = ap.parse_args()

    try:
        H.ensure_hwpx(args.file)
        z = zipfile.ZipFile(args.file)
    except H.NotHwpxError as e:
        print(str(e))
        return 2
    except zipfile.BadZipFile:
        print("This is not a valid HWPX (a zip archive). "
              "이 파일은 올바른 HWPX(zip)가 아닙니다. (이 도구는 HWPX 전용입니다.)")
        return 2
    names = H.section_names(z)
    hdr = H.etree.fromstring(z.read("Contents/header.xml"))
    pbb = {pp.get("id") for pp in hdr.iter("{http://www.hancom.co.kr/hwpml/2011/head}paraPr")
           for bs in pp.iter("{http://www.hancom.co.kr/hwpml/2011/head}breakSetting")
           if bs.get("pageBreakBefore") in ("1", "true")}
    print(f"{args.file}")
    print(f"  entries: {len(z.namelist())}  sections: {len(names)}  "
          f"BinData: {sum(1 for n in z.namelist() if n.startswith('BinData/'))}")
    print()

    for name in names:
        root = H.etree.fromstring(z.read(name))
        c = H.structural_counts(root)
        print(f"== {name} ==")
        print(f"   p={c['p']} tbl={c['tbl']} pic={c['pic']} equation={c['equation']} "
              f"fieldBegin={c['fieldBegin']} endNote={c['endNote']} "
              f"footNote={c['footNote']} linesegarray={c['linesegarray']}")
        n_style = sum(1 for p in root.findall(f".//{H.P}p") if p.get("paraPrIDRef") in pbb)
        print(f"   paragraphs w/ pageBreak={c['pageBreak_paras']}  "
              f"columnBreak={c['columnBreak_paras']}  "
              f"style pageBreakBefore={n_style} (paraPr {sorted(pbb) or '-'})")

        if args.breaks:
            for para in root.findall(f".//{H.P}p"):
                pb = para.get("pageBreak") in ("1", "true")
                cb = para.get("columnBreak") in ("1", "true")
                sb = para.get("paraPrIDRef") in pbb
                if pb or cb or sb:
                    flags = ",".join(f for f, on in
                                     (("pageBreak", pb), ("columnBreak", cb),
                                      ("style:pageBreakBefore", sb)) if on)
                    snippet = H.own(para)[:40].replace("\n", " ")
                    print(f"     [{flags}] paraPr={para.get('paraPrIDRef')} "
                          f"id={para.get('id')}  «{snippet}»")

        if args.text:
            for para in root.findall(f".//{H.P}p"):
                txt = H.own(para).strip()
                if txt:
                    print(f"     {txt[:100]}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
