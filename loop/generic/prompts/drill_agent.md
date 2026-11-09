# Drill agent prompt (generic; fill {TASK_FILE}, {ID})
Drill for the owner's lab (paper research). Follow this task file exactly; your id is {ID}: {TASK_FILE}
Read only the files it names (use the Read tool). Write only the one file it names. Reply with one line: done, and how many tool calls you used.

Always end your output with three sections: "## MESSY" (any line of the pages you read that contradicts another, is out of date, unclear or reads two ways: quote it, name the file), "## WASTE" (where time was lost: minutes, what, why) and "## PROPOSE" (at most one change: the part or file, the change, the score it should move, the evidence); "none" where empty.
