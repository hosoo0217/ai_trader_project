# Main Approved Change Proposal Output

`main.py` can create and save a future change proposal when a generated Human
Approval Request receives an `APPROVE` decision.

This is proposal output only. It does not connect to a broker, Sierra Chart,
CME, OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically change strategy rules.

## How It Works

When `--show-session-trend` and `--approval-decision APPROVE` are used together,
`main.py` safely runs this flow:

1. Generate session trend output.
2. Generate strategy improvement suggestions.
3. Create Human Approval Requests.
4. Record the approval decision with `HumanApprovalWorkflow`.
5. Save the approval decision with `HumanApprovalLogStore`.
6. Create a future proposal with `ChangeProposalEngine`.
7. Save the proposal with `ChangeProposalStore`.

The proposal is printed in the `Approved Change Proposal` section.

## APPROVE Example

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --approval-decision APPROVE --approval-decided-by Hosoo --approval-notes "Approved as future proposal only, review before implementation"
```

## REJECT And NEEDS_REVIEW

`REJECT` and `NEEDS_REVIEW` do not create proposals. The CLI prints:

```text
No change proposal created because decision was not approved
```

This keeps rejected or uncertain ideas out of the proposal queue.

## Proposal File Location

By default, proposals are saved to:

```text
reports/change_proposals.json
```

Use `--proposal-dir` to choose another output folder.

## Why Proposals Do Not Change Strategy

An approved decision only creates a future proposal. The proposal is saved for
future human review only. It does not edit config, modify filters, update
decision logic, place orders, or implement strategy changes.

The output clearly says:

- no strategy rule was changed
- no trade signal was created
- proposal is saved for future human review only
- final human review is still required

## Why Final Review Is Required

Final human review is still required because a proposal may need more testing,
risk review, data-quality checks, and documentation before implementation is
considered.

This protects capital by keeping approval, proposal, testing, and implementation
as separate steps.
