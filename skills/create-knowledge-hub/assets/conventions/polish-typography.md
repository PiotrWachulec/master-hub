# Convention: Polish typography — dash character

This hub uses a plain hyphen "-" (U+002D, the one on a standard
keyboard) as its dash/pauza character in Polish-language content,
wherever a reader would expect a parenthetical or interruptive dash —
with a space on both sides, e.g.: "To jest - mój - przykładowy tekst."

Don't use the Unicode en dash "–" (U+2013) or em dash "—" (U+2014) for
this purpose, even though an en dash is common, arguably more
"correct," editorial typography in Polish publishing. This is a
deliberate style choice for this project, not an error correction to
make — a plain keyboard hyphen is what this hub's content actually
uses, confirmed against a real, hand-written example from the person
who owns this hub.

This applies everywhere a dash like this can appear: ordinary prose,
list items, headings, and blockquotes alike. A naive line-by-line fix
pass can miss blockquote lines (the ones starting with `>`), since
they're easy to skip when scanning for "normal" paragraph text — check
those explicitly if retrofitting existing content.

`scripts/validate_hub.py` backs this convention with a non-blocking
warning: an en dash or em dash found in `10-silver`/`20-gold` body text
is flagged, but it never blocks validation — this stays a style
reminder, not a structural rule.
