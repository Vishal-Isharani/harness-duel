# harness-duel: one page

**Concepts.** A **harness** is everything the team changes around the model (AGENTS.md, skills,
MCP config, model, agent). It's a folder whose `files/` are copied into the repo before the agent
runs, so "the change" is something you can diff. A **task** is a request written like a ticket,
plus **hidden tests** that decide whether it was done; the agent never sees them. A **run** is one
harness attempting one task in a fresh git workspace. Everything it produced is kept on disk. A
**duel** is one task, 3 runs per side, won by the first clear difference: hidden tests, then new
lint issues (the team's conventions as ruff rules), then cost. The **verdict** is a sign test over
the duels: if the change did nothing, each decisive task would be a coin flip.

**The five hardest decisions**
1. **Count wins, not scores.** Averaging four metrics into one number needs an exchange rate
   between "a test passes" and "ten cents" that doesn't exist. A fixed order (correctness first,
   conventions, then cost) puts that judgment in the open. The price is that the size of a win is
   ignored.
2. **The task is the unit, not the run.** Three runs of one task share the same difficulty, so they
   aren't independent evidence. Runs are averaged into one duel per task, and the statistics are
   done on tasks.
3. **A sign test instead of anything fancier.** It can be explained in one sentence, needs no
   assumptions about the data, and is conservative. The cost: 6 tasks need 6 wins, and 4 tasks can
   never produce a verdict. I chose "often says NO CLEAR DIFFERENCE" over "sometimes says BETTER
   by luck".
4. **Hidden tests are the business requirements, with no LLM judge.** Tests written from the ticket
   check "did what was asked" deterministically. A judge would add cost, noise and a second thing
   to trust.
5. **Only new lint issues count, and a test regression blocks BETTER.** Pre-existing issues
   shouldn't be blamed on a harness, and a change that breaks one task shouldn't be rolled out
   because it helped five others.

**What I cut and why.** An LLM judge (see 4). Bootstrap or Bayesian statistics (see 3). Parallel
runs, caching and a dashboard, since the tool is small enough to read end to end. Isolation from the
user's own `~/.claude` config: a real confounder, noted but not solved. Adapters beyond Claude Code.

**A result I didn't trust.** _[Write this from your own real run. Look for a number in your report
that surprised you, check it against that run's `diff.patch`, `hidden_tests.txt` and
`result.json`, and describe what you found and what you did about it.]_
