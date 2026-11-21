# cloud/

Deployment scripts and environment notes for Huawei Cloud (concept C11). **Nothing is provisioned yet.**

## Readiness checklist (task CLD-01 — must be completed before any provisioning)
- [ ] Account access confirmed
- [ ] Region chosen and the availability of ECS and RDS for MySQL (and DCS for Redis, if needed) confirmed there
- [ ] Instance specifications and quotas confirmed
- [ ] Credits or budget confirmed
- [ ] Owner of provisioning decided (one person at a time)

## Rules
- Do not expose database ports publicly; restrict inbound traffic; apply least privilege.
- Credentials never go into the repository; supply them through the environment or a secret store.
- Record decisions and costs in `docs/` as the work proceeds (CLD-08, CLD-10).
- Deployment commands are added here only after they have been run successfully.
