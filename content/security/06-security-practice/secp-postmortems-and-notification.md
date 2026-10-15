---
id: secp-postmortems-and-notification
title: Learning and breach notification
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: Turn incident findings into owned safeguards and prepare timely notification decisions.
---

Restoring service does not finish the learning and communication work. A postmortem should explain the conditions that made the incident possible and assign concrete changes. A notification assessment also needs prepared decision-makers: investigation can continue while initial regulatory information is supplied.

### Post-incident activity

Run a **blameless postmortem**: what happened, why, what made it worse, and what will change, with owners and dates. "Blameless" does not mean nobody is accountable; it means you assume people acted reasonably with the information they had, so they tell you the truth. Blaming individuals teaches everyone to hide mistakes.

Also consider legal duties. For a reportable personal-data breach, the UK GDPR controller must notify the ICO without undue delay and, where feasible, within 72 hours of awareness. The exception is where risk to individuals' rights and freedoms is unlikely; delayed notification needs reasons and information may be supplied in phases. EU GDPR Article 33 uses the same core rule for its competent authority. Other duties, such as processor-to-controller notice or high-risk individual notification, differ; seek jurisdiction-specific advice for an actual incident.

## Apply the lessons

For an accidental object-storage exposure, reconstruct the configuration change and the evidence of access. Ask which guardrails could have prevented the exposure, which review or detection could have caught it sooner, and who owns each improvement. Verify whether proposed public-access settings cover the relevant access paths rather than assuming one setting fixes every case.

Record the awareness time, the notification threshold assessment, available facts and any reason for delay. Incomplete scope is a reason to communicate uncertainty and update information, rather than automatically waiting until every forensic question is answered. Separate duties to a regulator, affected individuals and a customer acting as controller: their triggers and timing can differ. These are preparation principles; an actual incident needs the applicable jurisdiction-specific assessment.

## Key takeaways
- Blameless learning records actions and assigns improvement owners without making punishment the primary goal.
- For a reportable UK GDPR breach, notify without undue delay and, where feasible, within 72 hours of awareness.
- The 72-hour point is not permission to wait unnecessarily, and information can be supplied in phases.
- Prepare separate routes for regulator, controller and individual notifications where applicable.

## Further reading
- [Google SRE postmortem culture](https://sre.google/sre-book/postmortem-culture/)
- [ICO breach guidance](https://ico.org.uk/for-organisations/report-a-breach/personal-data-breach/)
- [AWS S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
