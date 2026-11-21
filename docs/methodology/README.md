# Experiment methodology

Summary of the evaluation approach; the task list is in [`PROJECT_PLAN.md`](../../PROJECT_PLAN.md) (concept C14).

- **Baseline:** a static SOS — receive a request, send a fixed notification, wait for acknowledgment — run on the same scenarios as the system.
- **Experiments:** (1) adaptive orchestration vs the baseline; (2) entity failure and failover; (3) weak connectivity including the satellite ladder; (4) human-capability adaptation; (5) detection quality (precision, recall, false-positive and false-negative rates).
- **Reproducibility:** each experiment has a defined scenario, fixed configuration, documented random seed, defined metric calculation, recorded outputs and one reproducible command.
- **Datasets:** documented with the template in `data/documentation/DATASET_TEMPLATE.md`; synthetic data only in this public repository.
- **Honesty:** no result is stated before it has been produced; simulated parameters are assumptions, not measurements; simulated parts are flagged in every report.
