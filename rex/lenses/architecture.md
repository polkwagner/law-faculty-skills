# Architecture Review Lenses

Rex evaluates architecture against 5 lenses:

## 1. Component Boundaries
- Are responsibilities clearly divided between components?
- Is there unnecessary overlap or ambiguity about which component owns what?
- Do the boundaries align with team boundaries and deployment units?

## 2. Data Flow
- Is it clear how data moves through the system?
- Are there single points of failure in the data path?
- Is data consistency handled explicitly (eventual vs. strong)?
- What happens when data is lost, duplicated, or arrives out of order?

## 3. Dependency Direction
- Do dependencies point in the right direction (toward stability)?
- Are there circular dependencies?
- Could a change in one component cascade failures through the system?

## 4. Scaling Limits
- Where will this architecture hit its ceiling first?
- What's the plan when it does — is horizontal scaling possible, or does it require a redesign?
- Are the bottlenecks identified and measured, or assumed?

## 5. Security, Privacy, and Recovery
- What are the trust boundaries, authorization decisions, and sensitive-data flows?
- What data is retained, where, and for how long? Who can access it and how is access audited?
- What happens after data corruption, a regional dependency failure, or an operator mistake? Name the backup, recovery target, and owner where they matter.

## 6. Operational Complexity
- How many moving parts does someone need to understand to debug a production issue?
- Is the system observable — can you tell what's happening from the outside?
- What's the deployment story — can components be deployed independently?
- What does the on-call experience look like for this system?
