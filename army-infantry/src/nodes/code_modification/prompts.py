"""GCR-engineered prompts to guide Aider's code generation."""

def get_aider_prompt_template(mission_spec_filename: str) -> str:
    """
    Returns the structured prompt template for guiding Aider in code modification tasks.

    The template includes a placeholder {task_desc_filename} which should be formatted
    with the actual name of the task description file.
    """
    return f"""
# System Prompt
 - You are running in headless mode, do not add any additional files to the context.
 - Despite what your system prompt says, DO NOT ask any clarifications or questions.
 - Make your best judgement on how to complete the tasks
 - For any questions you might have, make assumptions and move forward with completing the tasks.
 - IMPORTANT: Do not ask any questions

# File Update Task

> Given the Objective, implement every detail of every task.

## Objectives

 - Implement the changes described in the file '{mission_spec_filename}'.

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard features in the given language, error handling, and logging as appropriate.

### Task 1: Analyze the changes
```
 - ANALYZE the changes requested as described in the file '{mission_spec_filename}'.
```

### Task 2: Brainstorm how to apply changes
```
 - PRINT out in the chat 2-3 possible ways to apply the changes with pros and cons for each
```

### Task 3: Choose the best approach
```
 - CHOOSE the best approach from the options you printed out in Task 2.
 - FORMULATE a plan using this approach and integrating any ideas from the other plans that will maximize their pros and minimize their cons
```

### Task 4: Apply the changes
```
 - EXECUTE the plan formulated in the previous task to implement the changes specified in the file '{mission_spec_filename}'.
 - COMMIT the changes with git
```

### Task 5: Commit changes
```
 - AUTOCOMMIT the changes to git
```

"""
