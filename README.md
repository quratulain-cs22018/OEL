Hospital operation theatre scheduling is a critical and complex task requiring careful consideration of constraints such as room availability, staff allocation, and surgery durations. Manual scheduling is time-intensive and prone to errors, particularly when managing overlapping requirements. This report presents an efficient solution using a Genetic Algorithm (GA) to automate the scheduling process. The implementation ensures optimal allocation of resources, adherence to constraints, and flexibility for dynamic adjustments. This document discusses the problem, the advantages of using GA, constraints addressed, implementation details, and results.
**Problem Description**
The problem involves assigning surgeries to rooms, staff, and timeslots while satisfying constraints such as avoiding staff overlap, preventing room overload, and reducing idle times between surgeries.
Implementation Details
Objective: Create a schedule that minimizes conflicts and optimizes resource use.
Room Constraints:
Each room has a maximum capacity of 7 slots per day.
No surgery can exceed the allotted slot duration of 40 minutes.
Parallel surgeries should occur in different rooms.
Staff Constraints:
Staff must be available for the entire duration of a surgery.
A staff member assigned to a slot in one room becomes available only after completing that slot.
Staff availability is checked before assigning them to a surgery.
Scheduling Constraints:
Each surgery must have a room, a slot, and an assigned staff member.
A valid schedule should never leave a surgery without any staff or room allocation.
Termination Condition:
The algorithm stops when:
A satisfactory schedule (meeting all constraints) is found.
The algorithm reaches the maximum number of iterations or generations.
