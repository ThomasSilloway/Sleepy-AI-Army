## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## General operate on existing mission

Add support for general commandline to operate on an already created mission

## Weird error message in Mission Report
```
## Errors and Issues

- E- r- r- o- r-  - i- n-  - c- o- d- e- _- m- o- d- i- f- i- c- a- t- i- o- n- _- n- o- d- e- :-  - A- i- d- e- r-  - d- i- d-  - n- o- t-  - m- a- k- e-  - a- n- y-  - c- o- m- m- i- t- s-  - d- u- r- i- n- g-  - i- t- s-  - e- x- e- c- u- t- i- o- n- .
```

Note: Can repro this by running in on this repo and reverting the change to delete the backlog

## Aider questions hang the process

Aider fails to commit changes when it identifies new files to add without a clear directive of what to do.

Not really sure how to solve this, but one idea would be to have a separate thread listen for these kinds of questions and tell it to just do the best with what it has and apply the changes.
