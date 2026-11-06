NGF COLLEGE PROJECT 04: SOLAR ENERGY SELF-CONSUMPTION ANALYTICS
GROUP SIZE: THREE STUDENTS. Level: introductory Python, Pandas and Matplotlib.
Question: Which buildings use generated solar power locally, and when is grid dependence highest?
Plan: four 2-3 hour sessions: inspect/plan, implement, integrate, present.

FILES IN NUMBER ORDER
01 README; 02 raw CSV; 03 A notebook; 04 B notebook; 05 C notebook;
06 group runner; 07-09 student modules; 10 dependency list; 11 public checks;
12 data dictionary and exact contracts; 13 verification and numeric controls.
All notebook explanations are plain raw-text cells. No instructor solution is
included. TODO functions deliberately raise NotImplementedError. Initially
RUN_MY_CHECKS=False lets scaffolds run; it does NOT mean the project is finished.

SETUP - WINDOWS CMD AND POWERSHELL (IDENTICAL COMMANDS)
Extract to a short location such as Downloads. Open a terminal in NGF_P04.
Install 64-bit Python 3.10 first. Run these commands without activating venv:
  py -3.10 -m venv .venv
  .venv\Scripts\python.exe -m pip install -r 10_requirements.txt
  .venv\Scripts\python.exe -m notebook
Internet is needed for that install. If py is absent and python is 3.10, use
python -m venv .venv. Explicit executable paths avoid PowerShell policy issues.

OFFLINE INSTALLATION
Wheels/installers are not included. On a connected Windows computer with the
same Python 3.10 and 64-bit architecture, run inside a project folder:
  py -3.10 -m venv .download_env
  .download_env\Scripts\python.exe -m pip download --only-binary=:all: --dest wheelhouse -r 10_requirements.txt
Copy that complete wheelhouse and the project to the offline computer. Install
Python there using an official installer prepared separately. Then run:
  py -3.10 -m venv .venv
  .venv\Scripts\python.exe -m pip install --no-index --find-links=wheelhouse -r 10_requirements.txt
  .venv\Scripts\python.exe -m notebook
Missing wheel? Prepare it on the connected computer; do not remove --no-index.
All 19 projects use the same dependency list; a teacher can reuse one wheelhouse.

INDIVIDUAL RESPONSIBILITIES AND DELIVERABLES
A owns 03 and 07: CSV parsing, audit, repair policies, validation and quarantine.
Submit notebook, module, cleaning audit and coverage explanation.
B owns 04 and 08: the defined KPIs, safe ratios, grouped summaries and applicable
balance checks. Submit notebook, module, metric outputs and one hand-worked row.
C owns 05 and 09: three charts, numerical findings and recommendations. Submit
notebook, module, PNGs and report; explain one visual design decision.
Each student must use a function, explain a condition, and show one added test.
A uses an audit loop/mapping; B uses grouping and safe arithmetic; C uses a
chart/annotation loop. Each notebook needs name, two decisions and one bug fixed.

INTEGRATION PROTOCOL
Read file 12 together BEFORE coding. Implement only your assigned 07/08/09 file.
These .py modules are the executable source; notebooks import them. The group
runner uses explicit importlib loading and never pretends to import .ipynb.
Preserve function signatures and column names; agree before changing contracts.
B and C can practice on small invented fixtures while waiting for A; never use
toy numbers as final findings. Save modules then restart and run all notebook cells.
Set RUN_MY_CHECKS=True in each notebook before submitting. From this folder:
  .venv\Scripts\python.exe 06_group_main.py
  .venv\Scripts\python.exe 11_checks.py
  .venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace 03_student_A.ipynb
  .venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace 04_student_B.ipynb
  .venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace 05_student_C.ipynb
06 saves five CSVs, three PNGs and a TXT report in results; reruns overwrite them.
Do not edit raw data or tests to force a pass. Public tests are not exhaustive.
Submit the folder with executed notebooks and results; omit .venv, wheelhouse,
.download_env and checkpoints. Present a five-minute team demonstration.

GRADING - 100 POINTS
A 25: valid parsing 10, duplicate/conflict handling 8, traceable audit 7.
B 25: correct KPIs 10, weighted aggregation 8, boundary handling 7.
C 25: readable accurate charts 10, findings/actions 10, limitations 5.
Team 15: fresh reproducible run 8, contracts and integration checks 7.
Individual interview 10: each student earns their own explanation score.
Final individual mark = A+B+C+team shared scores plus own interview score.
Hard-coded totals receive no calculation credit, even if a test passes.

INTERVIEW TRAPS TO UNDERSTAND
Why is a duplicate key different from an identical duplicate row?
Why must an undefined ratio stay missing rather than become zero?
Why can a mean of percentages differ from a ratio of summed quantities?
Which metrics here are flows, snapshots, rates or non-causal proxies?
How does the missing key affect coverage and interpretation?
What does this project NOT let you conclude? Daily netting hides within-day imports and exports. These simplified meters cannot support tariff savings or battery sizing.
Explain your own module and one failed check you fixed without reading a script.
After completion, describe the project as synthetic-data analytics on your resume;
do not claim real organizational savings or production deployment.

TROUBLESHOOTING
Module missing: install into the same .venv used to run. File not found: open
Jupyter from this folder. PROJECT INCOMPLETE: implement the named function.
Assertion failure: compare contract, audit and controls before changing code.
Stale imports: save .py, restart kernel and run all. Blank plots: save then close.
