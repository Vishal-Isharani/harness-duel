# harness-duel: one page

**Concepts.** A **harness** is everything the team changes around the model (AGENTS.md, skills,
MCP config, model, agent). It's a folder whose `files/` are copied into the repo before the agent
runs, so "the change" is something you can diff. A **task** is a request written like a ticket,
plus **hidden tests** that decide whether it was done; the agent never sees them. A **run** is one
harness attempting one task in a fresh git workspace. Everything it produced is kept on disk. A
**duel** is one task, N runs per side, won by the first clear difference: hidden tests, then new
lint issues (the team's conventions as ruff rules), then cost. The **verdict** is a sign test over
the duels: if the change did nothing, each decisive task would be a coin flip.

**The five hardest decisions**
1. **Count wins, not scores.** Averaging metrics into one number needs an exchange rate between "a
   test passes" and "ten cents" that doesn't exist. A fixed order (correctness, conventions, cost)
   puts that judgment in the open. The price is that the size of a win is ignored.
2. **The task is the unit, not the run.** Runs of one task share its difficulty, so they aren't
   independent evidence. Runs are averaged into one duel per task, and the statistics are done on
   tasks.
3. **A sign test instead of anything fancier.** It can be explained in one sentence, needs no
   assumptions about the data, and is conservative: 6 tasks need 6 wins, and 4 tasks can never
   produce a verdict. I chose "often says NO CLEAR DIFFERENCE" over "sometimes says BETTER by luck".
4. **Hidden tests are the business requirements, with no LLM judge.** Tests written from the ticket
   check "did what was asked" deterministically. A judge would add cost, noise and a second thing
   to trust.
5. **Only new lint issues count, and a test regression blocks BETTER.** Pre-existing issues
   shouldn't be blamed on a harness, and a change that breaks one task shouldn't be rolled out
   because it helped five others.

**What I cut and why.** An LLM judge (see 4). Bootstrap or Bayesian statistics (see 3). Parallel
runs, caching and a dashboard, since the tool is small enough to read end to end. Isolation from
the user's own `~/.claude` config: a real confounder, noted but not solved. Adapters beyond Claude
Code.

**A result I didn't trust.** I ran the offline demo with one run per task. The candidate harness
produces the good solution 90% of the time and the baseline 30%, so the right answer is obvious,
yet the tool said NO CLEAR DIFFERENCE: the candidate won 4 tasks and lost 2. I didn't believe it
and opened the lost tasks' files. In both, the candidate had simply drawn the sloppy solution by
chance. The tool was correct about the evidence it had; one run per task just isn't enough
evidence when agents are random. With 3 runs per task the same comparison is a clear BETTER (6 of
6). So the default is 3 runs, `--runs 1` is documented as a cheap first look only, and the README
shows both results side by side. Separately, while adding `--tasks`, Claude Code pointed out that
input errors exited with code 1, the same as WORSE, so a CI gate could read a typo as a verdict.
They now exit with code 3.