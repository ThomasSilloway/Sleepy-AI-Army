# Debugging Google Generative AI API 500 INTERNAL Error

## Core Problem

The key line:

```python
google.genai.errors.ServerError: 500 INTERNAL. {'error': {'code': 500, 'message': 'An internal error has occurred. Please retry or report in https://developers.generativeai.google/guide/troubleshooting', 'status': 'INTERNAL'}}
```

This indicates the issue originates from the Google Generative AI API server, not from the ADK application code. It occurred during a request to the `gemini-2.5-pro-exp-03-25` model. A 500 error typically means something went wrong on Google's backend.

---

## Breakdown of the Log

* **AFC is enabled...**: Confirms Automatic Function Calling (tool use) is active.
* **HTTP Request: POST ... "HTTP/1.1 500 Internal Server Error"**: Confirms Gemini API call failed with HTTP 500.
* **ERROR - fast\_api.py:637 - Error in event\_generator**: ADK's FastAPI layer is catching the propagated error.
* **Traceback through ADK**: Error path through ADK components like Runner, LlmAgent, BaseLlmFlow, google\_llm.py.
* **google.genai library**: Error raised by `google-genai` after receiving 500 from `_api_client.py`.
* **GeneratorExit & OpenTelemetry Error**: Likely side-effects during async cleanup after initial 500 error.

---

## Possible Causes & Troubleshooting

### 1. **Transient Google Backend Issue (Most Likely)**

* **Cause**: Temporary glitch.
* **Action**: Retry after a few minutes.

### 2. **Experimental Model Instability**

* **Cause**: `gemini-2.5-pro-exp-03-25` is an experimental model.
* **Action**: Switch to a stable model (e.g., `gemini-1.5-flash-001`, `gemini-1.5-pro-latest`).

### 3. **Problematic Request Payload**

* **Cause**: Rarely, a complex request could trigger a bug.
* **Action**:

  * Try a simple prompt without tools.
  * Gradually reintroduce complexity.
  * Log the `llm_request` via `before_model_callback` for inspection.

### 4. **Google Cloud Service Disruption**

* **Action**: Check [Google Cloud Status Dashboard](https://status.cloud.google.com/).

### 5. **Report the Issue**

* **Action**:

  * Use [Google's troubleshooting link](https://developers.generativeai.google/guide/troubleshooting).
  * Include model name, timestamp, and full error details.

---

## Summary

This is most likely a temporary Google backend issue, especially given the use of an experimental model. First retry, then try switching to a stable model to confirm root cause.
