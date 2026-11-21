# experiments/

Reproducible evaluation (concept C14). Methodology: [`docs/methodology`](../docs/methodology/README.md).

| Folder | Content |
|---|---|
| `baselines/` | The static SOS baseline implementation |
| `scenarios/` | Scenario definitions (events, user conditions, entity availability, network conditions) |
| `configs/` | Fixed configurations with documented random seeds, including network and satellite simulation profiles |
| `results/` | Recorded outputs and the results report (measured values only) |

Every experiment needs a defined scenario, a fixed configuration, a documented seed, a defined baseline, a metric definition, recorded outputs and one reproducible command. The experiment harness arrives with task EVL-04. No result exists yet.
