"""GCR-engineered prompts to guide Aider's code generation."""

# TODO: Cleanup this example prompt and call it via function like get_aider_prompt(vars)
aider_prompt = f"""

# File Update Task

> Given the Objective, implement every detail of every task.

## Objectives

 - Implement the changes described in the file '{task_desc_filename}'.

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard features in the given language, error handling, and logging as appropriate.

### Task 1: Analyze the changes
```
 - ANALYZE the changes requested as described in the file '{task_desc_filename}'.
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
 - EXECUTE the plan formulated in the previous task to implement the changes specified in the file '{task_desc_filename}'.
```

### Task 5: Critique the changes
```
 - CRITIQUE the changes you made in Task 4 listing the pros and cons of the approach
```

### Task 6: Improve the changes
```
    - IMPROVE the changes you made in Task 4 based on the critique you made in Task 5.
    - If you think the changes are already perfect, print out `No changes needed`
```

"""