
from flask import Flask, render_template, request

app = Flask(__name__)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to generate a surgery schedule based on input
@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        # Get the input values from the form
        num_surgeries = int(request.form['num_surgeries'])
        num_rooms = int(request.form['num_rooms'])
        num_staff = int(request.form['num_staff'])

        # Get the durations of each surgery
        durations = [int(request.form[f'duration_{i+1}']) for i in range(num_surgeries)]

        # Get staff skills for each surgery
        staff_skills = []
        for i in range(num_surgeries):
            skills = [
                int(request.form.get(f'surgery_{i+1}_staff_{j+1}', 0)) 
                for j in range(1, num_staff + 1)
            ] 
            '''request.forms.get Retrieves the value of the form input corresponding to whether staff member j is available for surgery i+1.
Example: If i = 0 (first surgery) and j = 1 (first staff member), it looks for the input field with the name surgery_1_staff_1.
The default value is 0, meaning if the input is missing, it assumes that the staff member is unavailable for that surgery.'''
#Collect the skills (binary values: 0 or 1) of all staff members for the current surgery
            staff_skills.append(skills)
            '''skills is a list Each row corresponds to a surgery.
Each element in a row is 0 or 1, indicating whether a specific staff member is available for that surgery.'''

        # Generate the schedule using the genetic algorithm
        schedule = genetic_algorithm(num_surgeries, num_rooms, num_staff, durations, staff_skills)

 
        """
            If no valid schedule is generated, display an error message.
             This may occur if inputs are inconsistent or constraints cannot be satisfied.
             """
        if not schedule:
            error = "No valid schedule could be generated. Please check the inputs and try again."
            return render_template('index.html', error=error)
        
        # Render the schedule on the page
        return render_template('index.html', schedule=schedule)

    except Exception as e:
        # Handle errors gracefully and display the error message
        return render_template('index.html', error=f"An error occurred: {e}")

# Genetic Algorithm for generating an optimal surgery schedule
def genetic_algorithm(num_surgeries, num_rooms, num_staff, durations, staff_skills, slot_duration=40, max_room_slots=7):
    import random
# Genetic Algorithm to generate an optimal schedule for surgeries.
    
#     Parameters:
#         num_surgeries (int): Total number of surgeries to schedule.
#         num_rooms (int): Number of available operating rooms.
#         num_staff (int): Total staff members available.
#         durations (list): List of surgery durations.
#         staff_skills (list): 2D list indicating staff eligibility for each surgery.
#         slot_duration (int): Duration of each time slot in minutes (default: 40).
#         max_room_slots (int): Maximum time slots available per room (default: 7).
    # Calculate the number of slots required for each surgery
    # (divide surgery duration by slot duration, rounding up for partial slots)
   # Returns:
#         list: A schedule containing surgery details or None if no valid schedule is found.
    slots_required = [(-(-dur // slot_duration)) for dur in durations] 
    
    #to perform ceiling division using integer arithmetic
    '''Floor division (//) truncates toward zero, while ceiling division needs to round up.
Negating the number "reverses" the truncation direction of //, effectively performing a ceiling operation.(-(-50 // 40))  # Perform step by step
= -((-50) // 40)
= -(-2)  # -50 divided by 40 is -1.25, floored to -2
= 2  '''

    # Validate staff availability for each surgery
    valid_staff = []
    for i in range(num_surgeries):
        """
       Collect a list of staff members eligible for each surgery.
         If no staff is available for a surgery, return None to indicate an invalid schedule.
         """
        staff_for_surgery = [s + 1 for s, can_do in enumerate(staff_skills[i]) ]
        if not staff_for_surgery:
            return None  # If no staff is available for a surgery, return an invalid schedule
        valid_staff.append(staff_for_surgery)

    # Step 1: Initialize the population with random schedules
    population = []
    for _ in range(50):  # Population size of 50
        """
       Create a random schedule for each individual in the population.
         Assign surgeries to random rooms, time slots, and eligible staff members.
         """
        individual = []
        for i in range(num_surgeries):
            room = random.randint(1, num_rooms)  # Assign a random room
            start_slot = random.randint(1, max_room_slots - slots_required[i] + 1)  # Assign a random starting slot
            assigned_staff = random.sample(valid_staff[i], k=1)  # Randomly assign at least one valid staff member
            individual.append({
                "surgery": i + 1,  # Surgery ID
                "room": room,  # Assigned room
                "start_slot": start_slot,  # Starting time slot
                "end_slot": start_slot + slots_required[i] - 1,  # Ending time slot
                "staff": assigned_staff  # Assigned staff members
            })
        population.append(individual)

    # Fitness Function: Evaluate the quality of a schedule
    def fitness(individual):

        """
        Calculate the fitness of a schedule.
        
        Parameters:
            individual (list): A schedule (list of surgeries with room, time slot, and staff assignments).
        
        Returns:
            int: A fitness score based on overlap and staff assignment validity.
        """
        score = 0
        room_schedule = {room: [] for room in range(1, num_rooms + 1)}  # Track room schedules

        for surgery in individual:
            room = surgery["room"]
            start = surgery["start_slot"]
            end = surgery["end_slot"]

            # Penalize overlapping surgeries in the same room
            for booked in room_schedule[room]:
                if not (end < booked[0] or start > booked[1]):  # Overlap detected
                    score -= 10

            # Penalize invalid staff assignments
            for staff in surgery["staff"]:
                if staff not in valid_staff[surgery["surgery"] - 1]:
                    score -= 1   #changed from 15

            # Update the room's schedule
            room_schedule[room].append((start, end))
            score += 1  # Reward valid room and staff assignments changed from 5 to 1

        return score

    # Evolution Function: Create the next generation of schedules
    def evolve(population):
        
        # Sort the population by fitness (higher is better)
        population.sort(key=lambda x: fitness(x), reverse=True)

        # Select the top 10 schedules as parents for the next generation
        new_population = population[:10]

        # Generate new individuals by crossover and mutation until the population is full
        while len(new_population) < 50:
            # Select two parents from the top 10 fittest schedules
            p1, p2 = random.sample(population[:10], 2)

            # Perform crossover by combining parts of the parents
            crossover_point = random.randint(0, num_surgeries - 1)
            child = p1[:crossover_point] + p2[crossover_point:]

            # Mutation: Randomly adjust room or starting slot for some surgeries
            if random.random() < 0.01:  # 1% chance of mutation
                idx = random.randint(0, num_surgeries - 1)  # Select a random surgery to mutate
                child[idx]["room"] = random.randint(1, num_rooms)  # Assign a new random room
                child[idx]["start_slot"] = random.randint(1, max_room_slots - slots_required[idx] + 1)  # Assign a new random start slot

            # Add the mutated child to the new population
            new_population.append(child)

        return new_population

    # Step 2: Run the genetic algorithm for a fixed number of generations
    for _ in range(50):  # Run for 50 generations
        population = evolve(population)  # Evolve the population

    # Step 3: Select the best schedule from the final generation
    best_schedule = max(population, key=lambda x: fitness(x))

    # Format the best schedule for display
    final_schedule = []
    for surgery in best_schedule:
        final_schedule.append({
            "surgery": surgery["surgery"],
            "room": surgery["room"],
            "slots": f"{surgery['start_slot']} - {surgery['end_slot']}",
            "staff": ', '.join(map(str, surgery["staff"])) if surgery["staff"] else "No Staff Assigned"
        })

    return final_schedule

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)




        
#         score = 0
#         room_schedule = {room: [] for room in range(1, num_rooms + 1)}  # Track time slots for each room

#         for surgery in individual:
#             room = surgery["room"]
#             start = surgery["start_slot"]
#             end = surgery["end_slot"]

#             # Penalize overlapping surgeries in the same room
#             for booked in room_schedule[room]:
#                 if not (end < booked[0] or start > booked[1]):  # Overlap detected
#                     score -= 10

#             # Penalize invalid staff assignments
#             for staff in surgery["staff"]:
#                 if staff not in valid_staff[surgery["surgery"] - 1]:
#                     score -= 1

#             # Add surgery to the room's schedule and reward valid assignment
#             room_schedule[room].append((start, end))
#             score += 1

#         return score

#     def evolve(population):
       
#         population.sort(key=lambda x: fitness(x), reverse=True)

#         # Retain the top 10 schedules as parents for the next generation
#         new_population = population[:10]

#         # Create offspring using crossover and mutation
#         while len(new_population) < 50:
#             p1, p2 = random.sample(population[:10], 2)
#             crossover_point = random.randint(0, num_surgeries - 1)
#             child = p1[:crossover_point] + p2[crossover_point:]

#             # Random mutation: Adjust room or time slot for one surgery
#             if random.random() < 0.01:  # 1% mutation chance
#                 idx = random.randint(0, num_surgeries - 1)
#                 child[idx]["room"] = random.randint(1, num_rooms)
#                 child[idx]["start_slot"] = random.randint(1, max_room_slots - slots_required[idx] + 1)

#             new_population.append(child)

#         return new_population

#     # Run the genetic algorithm for 50 generations
#     for _ in range(50):
#         population = evolve(population)

#     # Select the best schedule from the final generation
#     best_schedule = max(population, key=lambda x: fitness(x))

#     # Format the best schedule for display
#     final_schedule = []
#     for surgery in best_schedule:
#         final_schedule.append({
#             "surgery": surgery["surgery"],
#             "room": surgery["room"],
#             "slots": f"{surgery['start_slot']} - {surgery['end_slot']}",
#             "staff": ', '.join(map(str, surgery["staff"])) if surgery["staff"] else "No Staff Assigned"
#         })

#     return final_schedule

# if __name__ == '__main__':
#     """
#     Run the Flask application in debug mode.
#     This starts a local server to handle user requests and generate schedules.
#     """
#     app.run(debug=True)
