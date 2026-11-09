# CLAIMS <run>
## R0 step 0 (form: RULES_TEMPLATE Step 0; one item a line)
R0 pro <1-5> | <line>
R0 stuck <n> | <answer naming a file, a number or a test; one line for each STUCK_CHECK question, numbered as there>
R0 candidate <k> | <test> | could move: <F or Q id, or new finding> to <status> if <result>
R0 pick | without step 0: <test> | now: <test> | why: <which result can change which status>
R<n> | <UTC> | change: <one field: old -> new> | why: <one line: why it should work here and not there> | ids: <F or Q ids it builds on, or none> | moves: <which result moves which finding or move>
