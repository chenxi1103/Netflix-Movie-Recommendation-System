## Logic Requirement
	1. Supervisor manages a release of model (containers, and router and A/B testing)
	3. After a certain time, supervisor will generate a report of the new release
	4. Supervisor uses the user engagement data to evaluate model online
	5. Decide when to rollback to revious release 

## Infrastructure Requirement
    1. Build a service to receive user recommendation request forward to related container
	2. Provide api for managing container (operations like start and stop)
	3. Provide mechanism for receiving new configuration
    2. When receiving a new release configuration, supervisor will somehow stop previous containers and start new containers, and change the "routing table"
    3. Provide a mechanism for blocking a new release when previous release test has not completed.
    4. Provide a mechanism for roll back to previous release
    5. Routing user to correct container according to "Routing Table"
    6. Store the recommendation log for report use
