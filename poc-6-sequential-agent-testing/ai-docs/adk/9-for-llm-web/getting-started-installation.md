[Skip to content](https://google.github.io/adk-docs/get-started/installation/#installing-adk)

# Installing ADK [¶](https://google.github.io/adk-docs/get-started/installation/\#installing-adk "Permanent link")

## Create & activate virtual environment [¶](https://google.github.io/adk-docs/get-started/installation/\#create-activate-virtual-environment "Permanent link")

We recommend creating a virtual Python environment using
[venv](https://docs.python.org/3/library/venv.html):

```md-code__content
python -m venv .venv

```

Now, you can activate the virtual environment using the appropriate command for
your operating system and environment:

```md-code__content
# Mac / Linux
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1

```

### Install ADK [¶](https://google.github.io/adk-docs/get-started/installation/\#install-adk "Permanent link")

```md-code__content
pip install google-adk

```

(Optional) Verify your installation:

```md-code__content
pip show google-adk

```

## Next steps [¶](https://google.github.io/adk-docs/get-started/installation/\#next-steps "Permanent link")

- Try creating your first agent with the [**Quickstart**](https://google.github.io/adk-docs/get-started/quickstart/)

Back to top