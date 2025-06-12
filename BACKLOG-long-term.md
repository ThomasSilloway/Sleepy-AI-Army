## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## Aider questions hang the process

Aider fails to commit changes when it identifies new files to add without a clear directive of what to do.

Not really sure how to solve this, but one idea would be to have a separate thread listen for these kinds of questions and tell it to just do the best with what it has and apply the changes.

## Update cost calculation to use more decimal places

Mission report - LLM Usage Cost seems to get rounded to the nearest penny, but I want to see the full cost

## Update mission report summary to have actual file changes

Mission report - the Execution Summary is wrong if Aider decides to ask a question and not commit the changes, the summary includes the changes Aider would have made, but not changes that were actually committed.

Let's rework the Execution Summary and rename that to `Aider Summary` and also pull more details out about if it asked any questions.  Aider Summary should go all the way at the end of the template.

Then re-add the Execution Summary to actually be a summary of the commits that Aider made.  So we already have that information in the Aider summary that we gather from `army-infantry\src\services\aider_service\aider_service.py` in the `get_summary()` function, it includes the commit hashes.  So we can use those commit hashes to get a diff of all of the changes, compile that into one big prompt and then use the `army-secretary\src\services\llm_prompt_service.py` to summarize the changes with a similar prompt to what we have now in `army-infantry\src\services\aider_service\prompts.py` in the `Changes Made` section. Which that file also would need to be updated to remove the `Changes Made` section.
