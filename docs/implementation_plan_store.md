# Implementation Plan Store

The Implementation Plan Store saves future implementation plans to JSON so they can be reviewed later. It is an audit-friendly record of planning work, not a system for changing strategy behavior.

Implementation plans are saved for future human-reviewed work only. A saved plan can describe the objective, proposed steps, required tests, risk checks, and rollback plan that a person should review before any separate implementation work begins.

Stored plans do not automatically change a strategy. The store does not edit strategy rules, update config, connect to a broker, create orders, or create trade signals. It only writes planning data to a local JSON file.

Final human approval is still required. Even when a plan comes from an accepted proposal review, it remains a plan until a separate human-controlled implementation process reviews the exact change, tests it, and approves it.

By default, plans are saved here:

```text
reports/implementation_plans.json
```

Each record includes the plan ID, source proposal ID, title, category, priority, objective, proposed steps, required tests, risk checks, rollback plan, status, safety flags, reasons, and blocking reasons. The safety fields keep `human_final_approval_required` set to `True` and `auto_implementation_allowed` set to `False`.

Future plan: main.py can show implementation plan output and support a final review workflow. That future workflow should still keep implementation separate from storage and require explicit human review before any strategy rule is changed.
