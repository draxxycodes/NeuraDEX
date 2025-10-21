```
git clone <your-github-repo-url>
```
Set Up the Python Environment:
In the same PowerShell window, navigate into the aiml directory of your newly cloned project:
```
cd .\NeuraDEX\aiml\
```
Install pipx, the tool we will use to safely install Poetry:
```
python -m pip install --user pipx
python -m pipx ensurepath
```
CRITICAL: Close and re-open PowerShell for the path change to take effect.
In the new PowerShell window, navigate back to your aiml directory.
```
pipx install poetry
```
Configure Poetry to create the virtual environment inside your project folder. This makes management easy.
```
poetry config virtualenvs.in-project true
```
Finally, install all project dependencies. This will read the pyproject.toml, create a .venv folder, and install everything needed (including hyperon).
```
poetry install
```
Your environment is now perfect.


Terminal 1 (PowerShell):
```
.\scripts\start_agents.bat
```
Terminal 2 (PowerShell):
Open a new PowerShell window and navigate to the aiml directory.
Wait about 10 seconds for the agents to initialize.
Run the final, end-to-end test script:
```
poetry run python acceptance/test_end_to_end.py
```
Observe: The test will run without port conflicts. It will communicate with the live agents.
This is the moment. It will succeed. You will see:

SUCCESS: All acceptance criteria met.
