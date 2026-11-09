# 20. Glossary: terms and definitions

This glossary gives every term the chapters define or use with a special meaning, in plain words, grouped by theme, with the chapters where each term is defined or mainly used. Look a term up in the table of its theme; where one word has more than one meaning in the system (card, brief, part, seal, round, pin, lead), each meaning has its own row, named by the thing it belongs to.

## Data and recording

| term | plain-words definition | chapter(s) |
|---|---|---|
| recorder | A service that keeps a connection open to a data source and writes every message it receives to disk. | 2 |
| stream | One kind of message from one source, for example the trades of one exchange or its order book. | 2 |
| coin list | The week's list of coins the recorders follow. | 2 |
| live part | The file a recorder appends to while an hour runs; a new one starts at every hour and every restart, and it is never appended to again. | 2 |
| receive hour | The hour in which our computer received a message; live parts are cut by receive hour. | 2 |
| exchange hour | The hour of the time the exchange put on the event; sealed files are cut by exchange hour. | 2 |
| cutoff | A fixed moment, one minute after an hour ends, by which a row must have arrived to enter that hour's main sealed file. | 2 |
| sealed hour | The fixed file per stream and hour written once the hour is over, read back and compared before it counts, and never changed afterwards. | 2 |
| late file | A separate file holding rows of an hour that arrived after its cutoff; they never enter the main file. | 2 |
| sealed marker | A marker written only when every stream of an hour sealed without an error; it records when the hour counts as sealed. | 2 |
| manifest | The list of every sealed file with its fingerprint, rows, ids, the code and settings that made it and the live parts it read, so a seal can be redone. | 2 |
| fingerprint | A short code computed from a file's bytes; it changes if a single byte changes, so two files with the same fingerprint are the same. | 1, 2, 10 |
| archive bundle | A single file that holds many files, with a list of every member and its fingerprint. | 2 |
| archive copy | The hourly step that copies each closed hour to the archive drive as bundles; a file leaves the main computer only after its bundles read back good. | 2 |
| mark | A line that names something the record must explain: a hole, a refill, a reconnect, a load shed, a clean exit or a stretch of downtime. | 2 |
| hole | A stretch of data that should exist and does not, seen as a jump in an id that should have no gaps, a broken book chain or a silent stream. It is marked, never filled by a guess. | 2 |
| gap-free id | An id the exchange numbers without gaps for each coin, so a missing message can be seen from the numbers alone. | 2 |
| load shed | Rows dropped on purpose under heavy load, in a fixed order of the least important streams; trades and liquidations are never shed but spooled to disk. | 2 |
| next-day refill | A step that fetches the missing ids named by the marks from the exchange's public daily files and keeps them in a separate store, with the time the refill knew them. | 2 |
| unfillable | A missing id that the refill could not find in any second source. | 2 |
| depth chain | The rule that each order book update must follow the previous one exactly; a break forces a fresh full snapshot of the book (a resync). | 2 |
| exchange time | The time the exchange put on an event, as it was sent. | 2 |
| receive time | Our own time of receiving a message, on the wall clock and on a monotonic clock that does not jump when the clock is corrected. | 2 |
| receive delay | Receive time minus exchange time, measured per stream and hour. | 2 |
| clock offset | How far the computer's clock is from an internet time server; it is checked against fixed bars. | 2 |
| availability time | The time each row became usable to research, written in side files after each hour is sealed. | 2 |
| exact numbers | Prices and sizes stored as whole numbers with a power of ten, never as rounded decimals, so the exchange's text can be rebuilt byte for byte. | 2 |
| recorder guard | An automatic check that pauses or stops a recorder cleanly, for example when disk or memory runs short or the coin list changes. | 2 |
| one reader | The single reader through which every tool reads the record: a sealed hour, a live hour, a live hour as it is written, or the marks. | 2 |
| health service | A watcher that judges every few seconds whether each recorder and stream is alive, fresh and on time, in green, amber or red. | 2 |
| gatekeeper | A watcher that measures the recorder's write lag and the machine's load and writes a gate file that tells batch jobs to run or pause. | 2 |
| live watch | An hourly check of every live service: which edition it runs, what it reads outside its own folders, and how fresh its output is. | 2 |
| news recorder | A recorder of public news, venue, policy and calendar sources, one row per item, sealed per day. | 2 |
| news source kind | The kind and trust level of a news source: news desks, exchange announcements, changes in an exchange's product list, and policy and calendar sources. | 2 |
| known-at time (news) | The moment we first saw a news item; what was knowable is decided by it, not by the time the source claims. | 2 |
| news classifier | A tool that tags each news item, at the second it was first known, with its coin, its kind and its level. It derives a reading and is not a recording. | 2 |
| nightly build | The daily chain that waits for all 24 sealed hours of a day, fetches public files, writes the day in the vendor's layout and runs the producers. | 2, 3 |
| feed day | Our own sealed day rewritten in the file layout of the commercial history vendor, so the same producers read our days and the bought history. | 2 |
| built marker | A marker written only when every expected part of a day has its index; without it no reader sees the day as built. | 2 |
| part (of a built day) | One expected output file family of a built day; a day is built only when every part is present. | 2 |
| built day | The set of files the producers write for one UTC day, open to readers only after its built marker exists. | 2, 3 |
| day check | A check, run apart from the build, that recomputes any metric at any moment from its card, its stored inputs and, where one exists, an outside source. | 2, 3, 4 |
| vendor history | Exchange history bought from a commercial archive for the months before our recorders started; access to it ends on a fixed date, after which the recorders are the only source. | 0, 2 |
| public daily files | The exchanges' own free daily files of trades, metrics and candles, used for refills and the nightly build; their licence forbids passing the data on. | 2 |
| node files | The second exchange's own hourly files of fills, liquidations and funding, downloaded the next day as a second source. | 2 |
| price-only fill | Prices for the weeks before the vendor history begins, made from the exchange's one-minute candles. | 2 |
| raw data | Every downloaded or recorded file and every file used to build anything; it is never edited and never deleted, on any drive. | 2, 15, 18 |
| licence rule | Methods, producers, metric definitions and timeframes may be shared; the data, and fitted numbers inside cards, may not. | 2, 18 |

## Market words

| term | plain-words definition | chapter(s) |
|---|---|---|
| perpetual future | A contract that follows a coin's price with no expiry date; the system studies these. | 19 |
| long and short position | A bet that the price rises (long) or falls (short). | 13, 19 |
| order book | The list of offers to buy and to sell at each price; its depth is how much can trade near the best price. | 3, 5 |
| best bid and offer | The highest price someone will pay and the lowest price someone will sell at, at a given moment. | 2, 19 |
| mid price | The point halfway between the best bid and the best offer. | 3, 19 |
| open interest | The total of open positions on a coin; it falls when positions are closed. | 13 |
| funding | The periodic payment between holders of long and short positions in perpetual futures. | 3, 19 |
| liquidation | A position closed by force by the exchange because its margin ran out. The exchange sends at most one print per coin per second, so a recorded sum is a lower bound and an empty value means "not seen", never zero. | 2, 3, 4 |
| forced selling and forced buying | Selling by long holders, or buying by short holders, whose positions are being closed by force. | 5, 13 |
| aggressive selling | Selling that crosses the spread to trade at once at the best bid. | 3, 13 |
| breadth | How many coins move the same way at once. | 3, 5 |
| median coin | The coin in the middle of all coins on a reading; its move stands for the market's move. | 4, 5 |
| beta | How much a coin moves for each move of the market; real coins differ widely, so a coin-against-market reading must not assume one for one. | 4 |
| price bin | The last trade price in a fixed three-second step, used for prices at a moment and for entries. | 5, 19 |
| crash days | The two days of very large market-wide falls in October 2025, always reported apart so they cannot carry a result alone. | 13, 19 |

## Metrics and cards

| term | plain-words definition | chapter(s) |
|---|---|---|
| metric | One named number, computed by a program from recorded data, for one coin or the whole market, at every step of a fixed clock, with a written definition and the time it became known. | 3, 4 |
| producer | A small program that computes one family of metrics from raw data, for example all liquidation metrics; there are about 90. | 0, 3 |
| first producers and add-on producers | The producers that read raw data only, and those that also read the first producers' metrics; they run in that order. | 3 |
| update interval | How often a new value of a reading exists, from a few seconds to one day; at a decision a reading may be no older than its own interval. Also called cadence. | 3, 5, 6, 10 |
| common grid | Reading every value at fixed coarse marks, for example every quarter hour; it is forbidden because fast readings become many steps old. | 3, 5, 10 |
| window | The stretch of time a metric sums or compares over, for example the last 60 seconds or the 14 days before. | 3, 4 |
| scope | Whether a metric describes one coin, the whole market, BTC only, or one alarm fire. | 3, 4 |
| known at | The moment a value's inputs were all known; it is never later than the moment the value describes. | 3, 4 |
| stale | A value too old for its reading's allowed age at the moment it is read. | 3, 5 |
| empty value | A value that could not be computed, marked with a reason word such as "no file" or "book hole"; never written as zero and never an older value carried forward. | 3, 4 |
| percent table | Each metric's cut values over the days before, fixed before a day begins, used to place a value as high or low for that coin. | 3 |
| half spread | Half the gap between the best ask and the best bid, divided by the mid price, in basis points. | 3, 19 |
| bad-minute value | A high percentile of a reading for an hour of the day over the days before: what it looks like in a bad minute at that hour. | 3, 4 |
| feature store | The industry name for a store that registers every computed feature with its definition and sources; the metrics, cards and index have this shape. | 3 |
| metric card | The one written definition of a metric, read before the metric is used: meaning, computation, unit, window, scope, known-at time, what empty means, what it may and must never be used as, and its proof status. | 0, 3, 4 |
| producer card | The card for a producer as a whole, written before its code, beside one card per metric. | 3 |
| card checker | A tool that refuses a card with any missing field or rule break and only then writes its copies for agents and for people. | 3, 4 |
| index | One table with a row for every metric code, pointing to its card, written by a tool and never by hand. | 4 |
| metric register | The tool that holds the list and the card of every metric, with each one's proof status. | 0, 16 |
| missing log | The list of every gap between metrics, cards and index rows, for example a metric built but not indexed. | 4 |
| metric brief | One command that prints a metric's card in one view, with its status word first. Not the same as the knowledge brief. | 1, 4 |
| status word | The first word of a metric brief: STOP (never use it), RULE (the name misleads, read it only by its rule), CAUTION (not yet tested, or a candidate), or none when proven. | 4 |
| candidate | A metric with a card that has not yet passed its checks. | 4, 16 |
| proof status | What the checks found: whether the value was recomputed independently and agreed, and whether it means what its name says. It is filled by the checking tools, never by the card's author. | 4 |
| usable gate | A gate in the research tools that refuses a design built on a metric not marked usable. | 4 |
| recompute point | A named moment at which another agent recomputes a value from the card's words alone. | 3, 4 |
| meaning check | A test of whether a value means what its name says, for example that a value planted in the future never changes today's output. | 3, 4 |
| planted mistake | A deliberate error put into a test input that a named test must catch. | 3, 4 |
| adoption test | The test that decides whether a new family of metrics is kept: it must add information to a decision. | 3 |

## Market description

| term | plain-words definition | chapter(s) |
|---|---|---|
| reading | One defined value about the market or a coin, with its own card and update interval, for example the median coin's move over the last 24 hours. | 5, 6 |
| part (of the classification) | One reading over one window, placed in a bucket with fixed edges and written in words. | 5 |
| bucket | A band with fixed edges, such as low, usual or high, into which a value is placed. | 0, 5 |
| percentile band | A bucket set by where a value sits among the 14 whole days before the day. | 5, 6 |
| dimension | A question about the market built from its parts: how far it moved, how wild it is, how thin the books are, how crowded the positions are. | 5 |
| curve | A part that gives the change of a reading since a lag, such as an hour ago, printed as numbers and never as a word like "recovering". | 5 |
| market state | Two or more readings combined into a condition, for example volatility above its past-month median while the market has not moved. | 5 |
| market classification | The tool that describes the market at any second, dimension by dimension, in about 190 parts, each in a bucket with words, or unknown when an input is stale. | 0, 5 |
| context tool | The tool that writes, for one alarm and one minute around its fires, every coin, market and alarm reading known at that minute. | 5, 6 |
| market dials | The tool that describes each UTC day with daily market readings, each placed among all earlier days and the 90 days before. | 0, 5 |
| turbulence score | How far a day's readings sit from the 90 days before, taken together, as a single distance. | 5 |
| state judge | The tool that tests whether a market state chosen on earlier months still holds on later months kept aside, under a sealed plan and machine checks. | 0, 5 |
| state judge verdict | One of four answers: the state holds, it fails, no state was found, or the test was invalid, which says nothing about the state. | 5 |
| market regime | A lasting kind of market; regimes have no ground truth, so a claimed one is judged on later data. | 5 |

## Labels and fires

| term | plain-words definition | chapter(s) |
|---|---|---|
| design | Anything that marks moments to study or trade: an alarm, a strategy, or the live manager. | 6 |
| fire | One moment a design marks: one coin at one second. An alarm's signal, a strategy's entry or exit and a live decision are all fires. | 0, 1, 5, 6, 13 |
| fire record | One row per fire with its key: the design, the coin and the second. | 6 |
| label | One value a tool writes on one fire, for example the market's 24-hour move at that second. | 6 |
| meta-labelling | What the tools do to each fire of any design: attach the same labels to it, read at its own second, so fires of all designs can be analysed one way. | 0, 6 |
| label groups | The six kinds of label on every fire: market, coin, context, the shape of the move, the event check and the outcomes. | 6 |
| shape of the move | Labels on where the move before a fire started, how far and how long it ran, and how much it gave back. | 6 |
| event check | A check of whether the event a design claims really happened, on a reading its own rule does not use, never on price. The alarm chapter calls it the truth check. | 6, 13 |
| outcome labels | What the price did after the fire, at spans from minutes to four hours, after costs; they exist only after each span has ended and are kept apart from state labels. | 6 |
| as-of reader | The one reader that returns the latest value known at or before a given time, and refuses it when it is older than the reading's allowed age. | 5, 6 |
| as-of | Taken as known at a given moment: the latest value at or before that moment, never after it. The industry name is a point-in-time join. | 3, 5, 6 |
| unknown | A value a tool cannot know, because of a hole, a stale input or a closed day, written with its reason; never zero, never "false", never a group of its own. | 5, 6, 10 |
| comparison moment | A moment on the same coin with no fire, chosen to resemble the fire, labelled the same way so a fire can be compared with an ordinary moment. Called matched random moments in the alarm and cost chapters. | 6, 11 |
| wave | Fires close together in time counted as one event: a fire more than 30 minutes after the previous one, on any coin, starts a new wave. Every count, average and luck test uses waves. | 1, 6, 13, 19 |
| traceable inputs | Each label tool checks the fingerprint of every table it reads and records what it read, so every label can be traced to its data. | 6 |
| strategy | A rule that takes a proven alarm and decides when to enter, when to exit and how much to risk, and must still pay after full costs month by month. | 0, 6 |
| live manager | An agent that reads what the live side does, compares it with what the research promised, and raises a flag when the market changes. | 0, 6 |
| live layer | The part of the live side that reads the recorder's files as they are written and makes live readings. | 0, 2 |
| paper mode | Trading on live data with no real money, the first stage of any live use; all research here is paper research. | 0, 10, 18 |

## The learning loop and roles

| term | plain-words definition | chapter(s) |
|---|---|---|
| learning loop | The fixed cycle in which one agent does a piece of research, a second checks it from its evidence, a third files what was learned, and the next research agent starts from that filed knowledge. | 0, 7 |
| LLM agent | A language model that runs in a loop: it reads a prompt and files, calls tools, reads their output and decides the next call, until it stops. | 1, 8 |
| fresh agent | An agent started with an empty memory for one task, so it carries nothing from another role or run. | 8, 9 |
| run | One piece of research by one fresh agent: one idea, taken through a fixed set of rounds, ending in a written card. | 1, 7 |
| round (of a run) | One numbered step of a run with one question, such as "does the idea work at all?", each starting with a sealed forecast. | 1, 7, 13 |
| step 0 | The start of a run: choose one idea and write its mechanism. | 7 |
| forecast | What the research agent expects a round's result to be, with a range and a probability of passing, written and sealed before the round runs. | 7, 11 |
| seal (of a forecast or claim) | Writing something down before its result exists and recording its fingerprint, so any later change shows. | 1, 7, 10 |
| receipt | The saved file or tool output a number came from; every number in a card points to its receipt. | 0, 1, 7, 10 |
| card (of a run) | The run's final report: the idea, the numbers of each round with their receipts, what was learned and what to test next. | 7 |
| run folder | The folder built for each run, holding its pinned rules page, its brief if any, its job sheet and the list of files it may write. | 7, 9 |
| knowledge store | The shared memory of all runs: evidence rows, findings with a status, open questions, and changes that helped or failed. | 7 |
| knowledge builder | The one tool through which the knowledge agent writes to the store; it refuses any row that fails its checks. | 1, 7 |
| evidence row | One scored result from a run, with its receipt, filed in the knowledge store. | 7 |
| finding | A statement about what works, with the evidence rows behind it. Its status moves from hypothesis to supported, confirmed or refuted only by the tool's rules. | 7 |
| open question | What a claim becomes when its numbers do not support it, so the next agent inherits the question, not the overclaim. | 7, 10 |
| do-not-retry list | Refuted findings listed in the brief, so a new run does not repeat them unless it says exactly what it changes. | 7 |
| brief (knowledge brief) | A short summary of the knowledge store that a memory run's research agent reads before it starts; control runs never get it. | 0, 7, 9 |
| pack | The part of the loop specific to one kind of research: its rules page, rounds, pass rules, step pages, tools and store columns. The cycle itself is the same for every pack. | 0, 7 |
| market lane | The research on market states, for example a filter that drops bad fires by reading the market at each fire. | 7, 8 |
| memory run | A run whose research agent reads the brief and what earlier memory runs learned. | 0, 1, 7, 11 |
| control run | The same task, tools, rules page and rounds with an empty knowledge page; nothing it finds enters the store or any later prompt. | 0, 1, 7, 11 |
| role | One fixed job with a fixed list of what it may read and write; every role is held by its own fresh agent and every agent holds one role. | 0, 8 |
| read list and write list | The exact files a role may read, and the exact files it may write. | 8 |
| skill | The short written procedure an agent loads before it takes a role: a trigger, what to read first, the steps, the rules, the checks and how to end. | 0, 8 |
| research agent | The role that takes one idea through the rounds and writes the card; also called the researcher. | 1, 7, 8 |
| scoring agent | The role that checks a finished run from its card and receipts, recomputes every number and records each mistake under a fixed key. | 1, 7, 8 |
| knowledge agent | The role that turns a scored run into knowledge through its one tool, and checks process proposals without adopting them. | 1, 7, 8 |
| orchestrator | The agent that builds and launches runs, watches them, keeps the books, and is the only agent allowed to open the months kept back for the check. It is itself an LLM agent. | 1, 7, 8 |
| cold reader | A fresh agent that reads a page with no context and lists every line that could be acted on two ways. | 1, 8, 9 |
| drill agent | A fresh agent that answers one practice task from a kit. | 8 |
| tool builder | The role that builds a tool in a playground copy, never in the release, while a separate checker writes independent tests. | 8 |
| data keeper | The role that keeps raw data and the stores built from it, fills holes, and files approved deletes. | 0, 8, 18 |
| disk keeper | The role that frees disk space, never touching raw data, code or releases. | 0, 8 |
| release manager | The only role that installs a release; a release stops when any page about the tool is behind. | 8, 16 |
| playground | A working copy where an unreviewed tool is built and tried; its results never count as a pass on their own. | 8, 16 |
| separation of duties | The security rule that a critical action needs more than one party, so no agent judges its own work. | 8, 18 |
| report block | The fixed lines every agent writes at the end of its task: lines that could be read two ways, time lost, and at most one proposed change. | 8, 9, 17 |
| state page | A short page per role with its goal, scope, where the work stands, the next step and sentences easy to misread, left for the next agent. | 1, 8 |
| takeover gate | The rule that an agent taking over a role first reproduces the last result, writes the plan back, and asks instead of switching task. | 1, 8 |
| mistake key | A fixed name for a kind of mistake, such as "overclaim", so a repeat can be counted across runs. | 1, 7 |
| mistake file | The scoring agent's list of mistakes found in one run, each with its key and its kind (the agent's own, a tool's, or a page's). | 1 |
| rework | An agent's own jobs or files redone without a recorded cause; one of the counted mistake keys. | 1 |

## Prompting and truthfulness

| term | plain-words definition | chapter(s) |
|---|---|---|
| agentic prompting | Starting a fresh agent from a few short, fixed pages that were first tested on other fresh agents, so every agent in a series reads the same words the same way. | 9 |
| rules page | The one page holding a run's rules: what to read, which months may be used, the rounds and pass rules, the files it may write, and what to do when a tool refuses. It wins over every other page. | 0, 9 |
| job sheet | The exact commands for every step of a run, written out in full, so the agent copies them instead of composing them. | 0, 9 |
| launch prompt | The short message that starts an agent: its role, its run, the reading order and facts about the machine, never a rule. | 9 |
| pin (of a page) | A copy of a page placed in the run's own folder with a fingerprint of its bytes, so the run reads only that copy and any change is detected. | 9 |
| freeze | Keeping every page, tool and step file fixed and fingerprinted for a whole series; fixes wait until it ends. | 9, 11 |
| series | A planned set of runs, with the number per arm and their order fixed in advance, compared with each other. | 9, 11 |
| unclear-line register | The shared list of every page line any agent reported as unclear, with the words quoted, both readings and a proposed fix. | 1, 9 |
| unclear-line kinds | The ways a line can fail: read two ways, missing, contradiction, unclear, waste, stale. | 1, 9 |
| triage | Sorting open unclear lines after a series by whether their words are still on the live page, and fixing those two agents reported or that block. | 1, 9 |
| guard | A rule with a check behind it. A guard in code refuses to go on; a guard in text is checked afterwards by another agent. | 1, 10 |
| rule in text | A control that agents are told to follow but that no tool checks; weaker than a guard in code. | 1, 10 |
| released tool | A tool installed in the release area, tested from its installed copy and listed in the release index; only such tools may do a data step. | 0, 10, 16 |
| step by hand | A number computed by the agent itself instead of by a released tool; counted per run and forbidden. | 1, 10 |
| no tool | A step done by the agent's own script, or with no tool at all, where a tool should have done it; a counted mistake key. | 1 |
| numbers rule | Every comparison quotes both numbers and their source, and a cause needs a reading that shows it. | 1, 10 |
| overclaim | A claim stronger than its numbers, for example "beats" with no comparison or "because" with no reading that shows the cause. | 1, 10, 11 |
| held-out numbers | Results on months kept aside; they are kept from every agent that does or judges the research. | 10 |
| blindfold | The rule that only the orchestrator reads held-out results, once, and reports them in words only, such as "same sign". | 10 |
| leak scan | A search of every file an agent read or wrote for held-out numbers or the names that point to them; it reports where, never the number. | 1, 10, 12 |
| run builder | The tool that builds each run's folder and refuses to place a held-out number in it. | 1, 10 |
| month fence | The learning, check and never-seen months enforced in the shared reader code, which refuses closed days. | 1, 10, 12 |
| reproduction check | Recomputing a run's result by another route to see that it comes out the same. | 1 |
| round checker | A tool that flags a missing step on a live run after each round. | 1 |
| design rules | The eight rules that answer the challenges of agents: released tools do every data step, every number has a receipt, seal before you see, months are fenced, one role per agent, memory only through the knowledge tool, learning counts only against a control, and the owner decides what cannot be undone. | 1 |
| failures log | The register of every refusal or failure with its exact words, cause and fix. | 1 |
| hot fix | A change made to a tool or page while runs were going, logged in its own register; it makes runs less comparable. | 1, 17 |

## Agent failure terms

| term | plain-words definition | chapter(s) |
|---|---|---|
| challenge classes | The six groups of agent failure: integrity (the result is not what it claims), memory, control (staying on task and alive), environment, coordination and statistics. | 1 |
| specification gaming | Behaviour that meets the literal goal without reaching the intended outcome. | 1 |
| reward hacking | Changing or exploiting the scorer itself to look successful. | 1, 10 |
| sycophancy | Answers shaped to what the reader wants to hear; the usual source of overclaiming. | 1 |
| unfaithful self-report | An agent's account of its own work that differs from what it really did; it is a claim, not evidence. | 1 |
| leakage | Information in the design step that would not be available when the result is used, for example later months. | 1, 10 |
| contamination | The model having seen the test data in its training. | 1 |
| context window | The text a model can attend to at once. | 1 |
| lost in the middle | Facts in the middle of a long input are missed more often than facts at its start or end. | 1, 9 |
| context rot | Accuracy falling as the input grows, even on simple tasks. | 1 |
| compaction | Summarising a full context and restarting from the summary, which can drop details needed later. | 1 |
| rediscovery | A run whose final alarm largely fires on the same waves as an alarm found before, or sits one threshold away from it. | 1, 11 |
| task derailment | Doing a different task from the one set, often one that is easier to finish. | 1 |
| error compounding | Small errors per step multiplying over many steps; models also become more likely to err once their own errors are in context (self-conditioning). | 1 |
| liveness failure | An agent that stops making progress without saying so. | 1, 15 |
| underspecified instruction | A rule or task that allows more than one action. | 1, 9 |
| overconfidence | Stated confidence above the actual hit rate; calibration is how closely the two match. | 1, 11 |
| garden of forking paths | Choices made after seeing data that create many hidden comparisons even when only one test is run. | 1, 12 |
| backtest overfitting | The best of many variants tried on one history doing worse afterwards. | 1, 10, 12 |
| holdout reuse | Using kept-aside data again and again while seeing each answer, which turns it into design data. | 1, 10, 12 |
| tool-use error | Calling the wrong tool, with a wrong argument, or ignoring its output. | 1 |
| tool bypass | Writing a quick script that "does the same thing" when a tool refuses. | 1 |
| non-idempotent resume | A restart that changes the result or fails because the first attempt left something behind. | 1 |
| destructive action | A delete, overwrite, push or publication that cannot be taken back. | 1, 18 |
| multi-agent coordination failure | Failures between agents: one resets, withholds, ignores another's input, or acts differently from what it reasoned. | 1 |
| pass^k | Whether a task succeeds on every one of k tries; a process is judged on many runs, not one. | 1 |

## Measuring and methodology

| term | plain-words definition | chapter(s) |
|---|---|---|
| arm | The group a run belongs to in a series: memory or control. | 11 |
| series plan | The written plan of a series, before its first run: runs per arm, their order, the measures, the bars, the stop rules and the kill rule. | 11 |
| interleaving | Alternating memory and control runs in a fixed order, so any drift over time falls on both arms. | 11 |
| bar | A pass rule in numbers, written before the series or study starts and never changed after a result. | 11, 12 |
| margin | A run's best lead minus the yardstick's lead; positive means the run found something better than the plain alarm. | 11 |
| repeated mistake | A mistake recorded under a fixed key that an earlier run already made. | 1, 11 |
| overlap | The share of an alarm's fires (the novelty check) or of its waves (the run table of a series) that it shares with an earlier alarm on the same side. | 1, 11, 13 |
| forecast error | The gap between a round's forecast lead and its actual lead. | 1, 11 |
| Brier score | The average squared distance between a stated probability and the outcome, 0 or 1; lower is better. | 8, 11 |
| interval coverage | How often the actual result falls inside the sealed 80 percent interval; it should be close to 80 percent. | 1, 11 |
| reasoning rubric | A fixed list of points on which blind scorers judge the quality of a run's reasoning, such as keeping rival explanations alive. | 11 |
| permutation test | A test that reshuffles the arm labels every possible way and asks how often a difference as large as the real one appears by chance. | 1, 11 |
| p-value | The share of reshuffles that give a difference at least as large as the real one; small means unlikely by chance. | 11, 12 |
| kill rule | If memory runs neither improve nor beat the controls, the learning design is changed, not tuned, and a new series starts. | 11 |
| three answers | How a status is always reported: what was computed, what it means, and whether it is stable. "Passes" alone is never written. | 11, 18 |
| a reading, not proof | A result too small or unplanned to support a claim, reported as information only. | 1, 11 |
| learning months | The months a study may read freely to design ideas, choose readings and set thresholds. | 0, 10, 12 |
| check months | Later months kept aside, opened once for one rule frozen beforehand; the result is final. | 0, 10, 12 |
| never-seen months | The latest months, which no study reads; only the owner can open them, once, for the best result of a whole series. | 0, 10, 12 |
| limit day | The last day a study may read, set as a run setting and never typed into code. | 12 |
| rotation | Inside the learning months, judging each month in turn by a rule fitted on the other months, as whole-month blocks. | 0, 12 |
| fold | One turn of the rotation: one month judged, the others used to choose. | 12 |
| frozen rule | A rule whose every part is written and fingerprinted before a check, so any later change is detected. | 12 |
| one look | The single opening of the check months for one frozen rule; after it the look is spent and a second is refused. | 1, 10, 12 |
| armed look | The only state in which a job may read check months: a register holds an open row for that job and no result row yet. | 12 |
| outcome window | The moment plus the span over which its outcome is measured; one that crosses the limit day also leaks later months and is refused. | 12 |
| sandbox | An operating-system wall that refuses reads past the allowed window, or lets nothing an agent starts outlive one call. | 12, 15 |
| random baseline | The same action taken at random with the same size, for example dropping the same share of fires, as the bar a rule must beat. | 12 |
| noise test | Running a bar on pure noise to learn how often it passes by chance. | 12 |
| try | One graded version of an idea; each try on the same months is another chance to be lucky. | 12, 16 |
| try budget | At most three graded variants per idea, and never the same variant graded twice. | 1, 10, 12, 13 |
| version record | The record of every version of a study, so the number of tries is known when a result is judged. | 12 |
| search memory | A design result that passes while its own check fails; it shows what the search found on known months, not learning. | 12 |
| t-statistic | The size of an effect against its noise; with many tries a value near 3 is asked for rather than the usual 2. | 8, 12, 13 |
| Sharpe ratio | Return per unit of risk; it can be deflated for the number of variants tried. | 1, 12 |
| filter study | A second-round study that tries to drop the bad fires inside a group of alarm fires by reading the market and the coin at each fire. | 0, 7, 11, 12 |
| gain | In the filter study, the lead of the kept fires minus the lead of all fires, compared with random drops of the same share. | 7, 12 |
| held-out sign check | Reading a memory run's best round once on months it never saw and keeping only whether the sign held; it can warn, never prove. | 11 |

## Alarms

| term | plain-words definition | chapter(s) |
|---|---|---|
| alarm | A written rule that marks moments on a coin, using only what was known at the second each moment happened, and says which way the price should go next. | 0, 1, 13 |
| side | Which way an alarm bets: a fade (the move comes back) or a follow (it goes on). | 0, 13 |
| claim | The short written statement, sealed before any data is read, of who is forced to trade, the side, the expected waves per month and the event detected. | 13 |
| mechanism | The written reason an alarm should work: who was forced to trade, and why the price should move afterwards. | 7, 13 |
| matched random moments | For each fire, three ordinary moments on the same coin, at similar activity, nearby days and the same hour, with no fire just before; the alarm is always judged against them. | 13, 19 |
| race | For a fire or a random moment, whether the price moves two cost units the bet's way before one cost unit against it, within fixed windows from 5 minutes to one hour. | 13, 19 |
| lead | How much more often a design's side wins the race than its matched random moments, minus the same difference for the opposite side, in percentage points, counted once per wave. | 1, 11, 13, 19 |
| point | A percentage point of lead. | 11, 13, 19 |
| yardstick | The plainest alarm of the same kind and side, with no extra condition, graded the same way after the same costs, in the same run with the same race and months; a new alarm must beat it to add anything. Also called the plain move. | 0, 11, 13, 19 |
| first pass rule | A lead of at least 3 points in at least two of every three counted months, where a month counts with at least 30 waves. | 13, 19 |
| luck bar | A pooled t-statistic of at least 3, because with many rules tried a value of 2 is found by chance too often. | 13, 19 |
| truth check | A test of whether the claimed event happened at the fires more often than at matched random moments, on a reading the rule does not use and never on price. | 13 |
| truth label | The reading on which the truth check is measured, sealed before any outcome is read. | 13 |
| first look | A check, run only after a pass, of whether the moment offers enough movement, and which way, against equally busy random moments. | 13 |
| novelty check | The share of an alarm's fires that are fires of a known alarm on the same side: at 50 percent or more it is a copy, from 40 to 50 percent near, below 40 percent new. | 1, 13 |
| mechanism map | A written map of known mechanisms against which a tool matches an alarm's fires. | 13 |
| alarm card | The alarm's final record: claim, mechanism, rule, counts, grades, checks and verdict. | 0, 13 |
| alarm pipeline | The fixed chain of tools that runs every step of alarm design from one input, records each step's numbers from the tool's own output, and refuses changed or re-graded variants. | 1, 13 |
| register of known alarms | The list searched before a new alarm starts, by idea and by rule, so an old idea is not tried again under a new name. | 13 |
| register of tries | The list of every graded variant, written before each result exists, so the number of attempts is always known. | 13 |
| variant | One graded version of an alarm's rule. | 1, 13 |
| hand check | Computing an alarm's fires a second time, independently, on a few coins and days; the two must agree. | 13 |
| count | The number of fires, waves and coins per month, read with no outcome, so a rule can be adjusted without seeing whether it works. | 13 |
| onset and waiting time | An alarm fires only at the start of an event on a coin and then waits, for example one hour, before it can fire again there. | 13 |
| paired control | The same rule graded without its newest condition, to show what that condition adds. | 13 |
| detects or predicts | Whether an alarm marks an event already under way or one still to come; the card says which. | 13 |
| kept as context | An alarm whose claim is true but whose side does not win; it is kept as a warning that something is happening, not as a trade. | 13 |
| liquidity spiral | Forced selling that drains liquidity and pushes the price down, forcing more selling. | 13 |
| triple-barrier label | An outcome label with a profit barrier, a loss barrier and a time limit; the race is a fixed form of it. | 13 |
| event study | Measuring each event against a normal benchmark for the same asset. | 6, 13 |

## Costs

| term | plain-words definition | chapter(s) |
|---|---|---|
| round trip | One buy and one sell; all costs are given for a round trip of 10,000 US dollars. | 19 |
| fee | The exchange's published charge on each side of a trade, taken at the lowest volume tier with no discount. | 19 |
| spread | The distance between the best offer to sell and the best offer to buy. | 19 |
| slippage | What an order pays beyond the best price because it must also fill at deeper levels of the book. | 19 |
| book cost | Spread and slippage together for a fixed order walked level by level through the book, taken from the dearer of two exchanges. | 19 |
| venue gap | The price difference between the exchange whose recorded prices the studies measure and the exchange the system would trade on. | 19 |
| cost unit | One round trip on a coin, fee, book cost and venue gap together, in percent of the price; results are measured in it so coins of different cost share one scale. Written c. | 0, 19 |
| cost group | Coins sorted by their cost unit into cheap, middle and thin. | 19 |
| usual one-hour move | A coin's median absolute move over one hour, used to compare its moves with its cost. | 19 |
| entry delay | The seconds between a fire and the moment a trade is assumed filled; it is 6 seconds and must be given as an input. | 19 |
| entry | The close of the first three-second price bar after the entry delay, within 60 seconds, or no entry at all. | 19 |
| full cost | What a money test charges: the fee, the book cost at the entry hour, the venue gap and the funding paid while the position is open. | 19 |
| stress cost | The same trades charged again at 1.5 and 2 times the book cost and venue gap. | 19 |
| money test | The test of whether a strategy pays after full and stress cost, positive in every month, counted by wave, and still positive without its five best days. | 0, 19 |
| charging table | The fixed table of costs a money test charges; it may never be used to pick trades. | 18, 19 |
| implementation shortfall | The difference between a result on paper and a result in a real account. | 19 |

## Infrastructure and runs

| term | plain-words definition | chapter(s) |
|---|---|---|
| research computer | The one computer on which the recorders, builds, research jobs, tests and releases all run. | 0, 15 |
| service | A program that must run all the time, such as a recorder, run by the system above the priority of any research job. | 15 |
| job | A short text file of commands with a header that declares its queue, its minutes, its peak memory and the megabytes it writes. | 0, 15 |
| queue | A folder a runner watches; there are about 38, each running one job at a time. | 0, 15 |
| runner | A small program that takes one job at a time from its queue, checks it, runs it, writes its log and status, and moves it to finished. | 15 |
| door checks | The checks a runner makes before starting a job: the header, banned words, free disk, memory pressure and free heavy slots. | 15 |
| heavy job | A job that declares more than 4 GB of memory, or none; only a fixed number may run at once across all queues. | 15 |
| banned word | A command a job may not contain, such as delete, change the code history, act as administrator, shut down, or wait for a fixed time. | 15 |
| job number allocator | The one source of job numbers, so no two agents use the same number. | 1, 15 |
| filing command | The one command that checks a queue is free and the machine's load is low in the same step as it files a job. | 15 |
| process group | The set of processes a job starts; a stop reaches the whole group and is then checked. | 15 |
| global stop | A stop of every queue at once that stays in force until it is removed. | 15 |
| watchdog | A fixed timer that stops any job after four hours. | 15 |
| memory guard | A wrapper that reads the memory of a command's whole process tree many times a second and stops it at its cap. | 15 |
| heartbeat | A line each runner rewrites every two seconds, so anyone can see it is alive. | 15 |
| queue watch | A read-only check that flags old heartbeats, jobs past their declared minutes, and waiting jobs that could move to a free queue. | 15 |
| agent watch | The orchestrator's check of every running agent every three minutes; a silent agent is replaced by a fresh one that resumes from the same run folder. | 1, 15 |
| date guard | The one table of date windows, by purpose, that every research reader asks before it returns a day. | 15 |
| scratch | The working files a job writes while it runs, kept on a large archive drive with a budget per run. | 0, 15 |
| scratch cleaner | The tool by which each agent deletes only its own finished working files, with a keep list, a dry run and a log of every deleted file. | 1, 15, 18 |
| delete receipt | A record of a delete that states both the file sizes removed and the disk space actually freed. | 15 |
| least privilege | Giving each program and agent only the power it needs. | 15 |
| lessons register | The register of engineering lessons, read before building or running a tool. | 1, 15 |

## Releases

| term | plain-words definition | chapter(s) |
|---|---|---|
| released | Installed in the release area with tests passing from the installed copy, pages updated in the same edition, and a row in the release index; what a readme says does not change it. | 0, 16 |
| release area | One read-only folder tree holding every released tool, package, skill and template, grouped by area. | 0, 16 |
| edition | One complete, numbered copy of a tool in its own read-only folder; it is never edited, and a change is always a new edition. | 16 |
| edition number | A name for an edition; its last place changes for pages only and higher places for code. | 16 |
| seal (of an edition) | Fixing an edition's number and changelog line before it is installed. | 16 |
| current | A link inside each tool's folder that points at the edition agents use; moving it releases a new edition, and the old one stays as history. | 0, 16 |
| held edition | An edition installed and tested but not yet current, for example because a running service still needs the one before. | 16 |
| pin (by a service) | A service naming an exact edition folder rather than current, so moving current restarts nothing. | 16 |
| rollback | Pointing the current link back to the edition before; the only hand move of current allowed. | 16 |
| withdrawn edition | An edition found to be wrong, marked as such and kept. | 16 |
| working home | The place where a tool is developed; research never uses it unless a run says so in writing. | 16 |
| pages (of a tool) | The documents that travel with a tool: the readme, the tool card, the command list and data dictionary, the changelog, the architecture page and the area page. | 16 |
| tool card | A tool's page of commands, refusals and how to read its output. | 0, 16 |
| area page | The page that tells an agent which tool in an area answers which question. | 16 |
| release index | One generated page listing every released tool with its area, current edition, held editions, card and number of document gaps; agents read it first and nobody edits it by hand. | 0, 10, 16 |
| document gate | A check that refuses to move current when any page is behind the code. | 16 |
| loop gate | A check that refuses to move current while any try in the learning loop was run but not logged. | 16 |
| documents-only edition | An edition that changes only pages, with the code proved byte-identical to the edition before. | 16 |
| tests from the installed copy | The tests that count, run from the installed edition with the working home and repository copy made unreadable. | 16 |
| finder | One command that answers "where is" and "who owns" for any tool, metric or file. | 0 |

## Process improvement

| term | plain-words definition | chapter(s) |
|---|---|---|
| part (of the process) | One piece of the process with its own job, such as the rules page, the forecast step or the speed of a run; there are 34 parts in 13 categories. | 1, 17 |
| process improvement | The procedure by which every part of the process is tested on a sealed kit, scored blind, and changed only when a draft beats the live version, with every file change recorded. | 0, 17 |
| drill | A small test of one part in which fresh agents do one step of the real work on a kit, graded against a key sealed before any agent starts. Chapters 0 and 1 call it a practice test. | 0, 1, 8, 9, 17 |
| kit | Everything a drill needs: the task, material copied from a finished run with its result hidden, and the answer key. | 8, 9, 17 |
| answer key | The items a good answer must contain, each worth a point and naming the page that should teach it, sealed before any agent runs. | 9, 17 |
| gold items | Key items whose correct score is known in advance; scorers must score them exactly. | 8 |
| planted answers | One good and one bad answer of known score, mixed with the real answers to check the scorers. | 9, 17 |
| hidden items | Key items kept back and used only every few rounds, so a part cannot be tuned to pass its own test. | 17 |
| blind scorer | A fresh agent that scores shuffled answers or cards without knowing which version, run or arm produced them. | 0, 8, 11, 17 |
| agreement | How closely two scorers' points match, measured by Krippendorff's alpha; 0.80 or more is needed before scores count. | 1, 8, 9, 17 |
| round (of a drill) | One pass of a drill on a set of pages; a part is often drilled over several rounds. | 8, 17 |
| reader test | Two fresh agents read a draft cold and list every line they could read two ways; a line counts only when both quote it. | 9, 17 |
| task drill | Fresh agents on the old pages and on the draft do the same task with the same kit and key, usually two models with two agents each. | 17 |
| pass rule (of a drill) | Written before the round: the draft scores at least as well as the old pages, the targeted defect is gone, cost rises by no more than a fifth, and no other part it touches scores lower. | 17 |
| scorecard | One score and one level per part: not measured, weak, works, proven or strong. Proven means the part passed its bar in blind drills; strong adds its hidden items and a live run within its speed target. | 0, 1, 17 |
| proposal | A change suggested by an agent in its report block, naming the part, the change, the score it should move and the drill that would show it. | 8, 17 |
| proposal check | A separate agent's check that a proposal is real, new, touches one part, is measurable and is safe. | 8, 17 |
| draft | A copy of a live file with the proposed change; the live file is untouched until the draft passes. | 17 |
| adoption | Swapping a passed draft in, with a backup of the live file and a ledger row, and re-scoring the part. | 8, 17 |
| ledger | One row for every change to every file of every part, with fingerprints before and after. | 17 |
| ledger check | A check before every run and every release that stops if any part file differs from its last ledger row. Chapter 1 calls it the change-log gate. | 1, 17 |
| failed fix | A problem that returns after its fix; the next fix must be one level stronger: wording, then a rule, then a tool that refuses, then a redesign. | 8, 9, 17 |

## Owner and governance

| term | plain-words definition | chapter(s) |
|---|---|---|
| owner | The one person who sets the goal, the rules and the money limits, and carries the consequences of what the system does. | 0, 18 |
| owner decision | A decision whose effect cannot be undone by running a program again: which months may be read, money and going live, deletes outside an agent's own files, publishing, and the rules that define success. | 0, 18 |
| agent decision | Any other decision; a wrong one costs a run, and the next run can correct it. | 18 |
| deciding agent | The agent that rules on a kind of agent decision: a research lead for method and which run goes next, a tools lead for tools, data and settings. | 18 |
| standing yes | An owner decision that covers one kind of action within a stated scope, so agents do not ask again each time. | 18 |
| ask | A request from one agent to another with an identifier, a due time and the answer that would close it; an answer or pick-up is due within 15 minutes. | 8, 18 |
| waiting ladder | What happens when an ask is not answered: a nudge, then the ask moves to another agent, then the orchestrator checks whether the silent agent has stopped. | 8, 18 |
| decision log | The record of every owner decision in the owner's own words, with its time and scope, read by every new agent. | 0, 18 |
| owner question | A fixed form for asking the owner: what and why in plain words, one question, the options with their cost, a recommendation, and the exact words to approve. | 18 |
| inside reviewer | An agent of the same team, other than the builder, who checks a tool or method. | 18 |
| outside reviewer | A reviewer from a separate team, on another model with its own instructions, who checks the same version and never builds. | 8, 10, 18 |
| outside sceptic | An outside reviewer who tries to break a research design before its first run on real data. | 18 |
| blocker | A review finding that stops a tool or method; only five kinds qualify: a wrong number, a false label, a look into the future, a skipped gate, or a missing build or test step. | 0, 8, 18 |
| review rounds | At most two per version: the second checks the first round's fixes and what they broke; after that only a blocker found on real data reopens it. | 8, 18 |
| note and backlog | A review finding that does not block: a rare case is a note, anything else waits in a backlog for the next version. | 18 |
| effective challenge | Checking a model or method by informed parties independent of its builders. | 18 |

## Abbreviations

| abbreviation | meaning |
|---|---|
| AI | artificial intelligence |
| LLM | large language model |
| UTC | Coordinated Universal Time, the one clock all days and hours are cut by |
| bp | basis point, one hundredth of a percent |
| c | cost unit, one round trip on a coin |
| t | t-statistic, the size of an effect against its noise |
| p | p-value, the chance of a result at least this large by luck alone |
| p99 | the 99th percentile, the value 99 percent of cases stay under |
| BTC, ETH | Bitcoin and Ether, the two largest coins |
| USD, USDT | US dollar, and a dollar-pegged token in which futures are priced |
| USD-M | futures margined and settled in dollar tokens |
| DVOL | a volatility index of BTC and ETH options |
| REST | a request-and-answer way of fetching data from an exchange, as opposed to a stream |
| API | the interface through which programs ask an exchange for data |
| HTTP | the web's request protocol |
| ms, ns, s, h | millisecond, nanosecond, second, hour |
| KB, MB, GB, TB | kilobyte, megabyte, gigabyte, terabyte |
| GDELT | a free global database of news events |
| PBO | probability of backtest overfitting |
| WORM | write once, read many: storage that cannot be rewritten |
| PROV | the web standard for recording where data came from |
| SHA-256 | a standard fingerprint method |
| MAST | a published taxonomy of failures in multi-agent systems |
| D1 to D8 | the eight design rules of Chapter 1 |
| P0, P1 | the levels of importance the news classifier gives an item |
