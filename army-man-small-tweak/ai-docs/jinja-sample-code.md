# Jinja Sample Code: Plain Text System Alert (Minimal Example)

**Goal:** Generate a brief, plain text system alert.

Let's assume this directory structure:

```
mini_jinja_example/
|-- generate_alert.py
|-- templates/
    |-- system_alert.txt.j2
```

### 1\. Python Script (`generate_alert.py`)

```python
from jinja2 import Environment, FileSystemLoader
import datetime

# Minimal Jinja Environment Setup
# 'templates' is where your .j2 file is.
env = Environment(
    loader=FileSystemLoader('templates'),
    trim_blocks=True,
    lstrip_blocks=True
)

# Very small, generic context data
alert_data = {
    "system_id": "SYS-ALPHA-007",
    "timestamp": datetime.datetime.now(datetime.timezone.utc),
    "severity": "WARNING",
    "component": "AuthService",
    "message": "High login failure rate detected.",
    "threshold_exceeded": True
}

# Function to render the alert
def create_system_alert(data):
    """Renders a plain text system alert."""
    template = env.get_template('system_alert.txt.j2')
    rendered_alert = template.render(alert=data) # Pass data clearly

    # In a real app, this might be logged, sent via email/slack, etc.
    print("--- Generated System Alert ---")
    print(rendered_alert)
    # To save to a file:
    # with open(f"alert_{data['system_id']}_{data['timestamp'].strftime('%Y%m%d%H%M%S')}.txt", "w") as f:
    #     f.write(rendered_alert)
    return rendered_alert

if __name__ == '__main__':
    create_system_alert(alert_data)
```

### 2\. Jinja Template (`templates/system_alert.txt.j2`)

This template is for plain text output.

```jinja
SYSTEM ALERT
------------
Timestamp: {{ alert.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') }}
System ID: {{ alert.system_id }}
Severity:  {{ alert.severity }}
Component: {{ alert.component }}
Message:   {{ alert.message }}
{% if alert.threshold_exceeded %}
ACTION: Threshold exceeded. Please investigate immediately.
{% else %}
INFO: Monitoring normal.
{% endif %}
```

**Explanation of this minimal example:**

  * **Python (`generate_alert.py`):**
      * Sets up the Jinja `Environment` to load templates from a `templates` subdirectory.
      * `trim_blocks` and `lstrip_blocks` are good general settings for cleaner output.
      * Defines a small `alert_data` dictionary with sample information.
      * The `create_system_alert` function loads `system_alert.txt.j2`, renders it with the `alert_data` (passed under the key `alert`), and prints the result.
  * **Jinja Template (`system_alert.txt.j2`):**
      * Uses `{{ alert.variable_name }}` to insert data from the Python context.
      * Includes a simple `{% if alert.threshold_exceeded %}` ... `{% else %}` ... `{% endif %}` conditional block.
      * Uses `strftime` to format the timestamp.
      * The output is a simple, readable plain text alert.
