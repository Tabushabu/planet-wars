import sys, logging
sys.path.insert(0, '../')
from planet_wars import issue_order
from random import choice, randint
from heapq import heappush, heappop

# HELPER FUNCTIONS
#--------------------------------------------------------------------------------------- 

def OutRandomFromCollection(s, state, output_key, collection):
    if len(collection) == 0:
        return False
    random_choice = choice(collection)
    if random_choice is None: return False
    s.blackboard[output_key] = random_choice
    return True

# COMPOSITE NODES
#--------------------------------------------------------------------------------------- 

def SequenceWithMemory(s, state):
    working_list = s.child_nodes
    while len(working_list) > 0:
        i = choice(range(0,len(working_list)))
        child = working_list.pop(i)
        if not child.execute(state):
            return False
    
    return True

def Sequence(s, state):
    for child_node in s.child_nodes:
        continue_execution = child_node.execute(state)
        if not continue_execution:
            return False
    else:  # for loop completed without failure; return success
        return True
    
def SelectorWithMemory(s, state):
    working_list = []
    while len(working_list) > 0:
        i = choice(range(0,len(working_list)))
        child = working_list.pop(i)
        if child.execute(state):
            return True
    
    return False

def Selector(s, state):
    for child_node in s.child_nodes:
        continue_execution = child_node.execute(state)
        if not continue_execution:
            return False
    else:  # for loop completed without failure; return success
        return True

# DECORATOR NODES
#--------------------------------------------------------------------------------------- 

def LoopFor(s, state, num_repeats):
    for i in range(int(num_repeats)):
        s.child_node.execute(state)
    return True

def Cooldown (s, state, delay):
    if "count" in s.localBlackboard:
        if s.localBlackboard["count"] > 0:
            s.localBlackboard["count"] -= 1
            return False
    
    s.localBlackboard["count"] = int(delay)
    return s.child_node.execute(state)
    
def LoopUntilFail (s, state):
    while s.child_node.execute(state):
        pass
    return True

def LoopUntilSuccess (s, state):
    while not s.child_node.execute(state):
        pass
    return True

def ForceSuccess(s, state):
    s.child_node.execute(state)
    return True

def ForceFailure(s, state):
    s.child_node.execute(state)
    return False

def Inverter(s, state):
    return not s.child_node.execute(state)

def RunOnce(s, state):
    if "run" in s.localBlackboard and s.localBlackboard["run"] == True:
        return False
    
    s.localBlackboard["run"] = True
    return s.child_node.execute(state)

# ACTION NODES
#---------------------------------------------------------------------------------------

def attack_weakest_enemy_planet(s, state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_weakest_neutral_planet(s, state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_closest_weakest_planet(s, state):

    # if len(state.my_planets()) >= 1:
    #     strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    # else:
    #     return False
    
    
    for my_planet in state.my_planets():
    
        closest_weak_planet = None
        closest_weakest_maxscore = 1000000000
        
        for planet in state.not_my_planets():
            score = state.distance(my_planet.ID, planet.ID) * 3 + planet.num_ships

            if score < closest_weakest_maxscore:
                closest_weakest_maxscore = score
                closest_weak_planet = planet

        # All planets have ships moving to them
        if closest_weak_planet is None: break
            
        # predict how many ships will be required to take planet
        ships_needed = closest_weak_planet.num_ships + 1
        if closest_weak_planet.owner == 2: 
            ships_needed += closest_weak_planet.growth_rate * state.distance(my_planet.ID, closest_weak_planet.ID)

        if my_planet.num_ships > ships_needed and my_planet.num_ships - ships_needed > 10:
            if not issue_order(state, my_planet.ID, closest_weak_planet.ID, ships_needed): 
                return False
    return True


def DoIHavePlanets(s, state):
    return bool(state.my_planets())

def DoesEnemyHavePlanets(s, state):
    return bool(state.enemy_planets())

def DoNeutralPlanetsExist(s, state):
    return bool(state.neutral_planets())

def IHaveFleetsInMotion(s, state):
    return bool(state.my_fleets())

def EnemyHasFleetsInMotion(s, state):
    return bool(state.enemy_fleets())

def GetPlanetDistance(s, state, planet1_ID, planet2_ID, output_key):
    s.blackboard[output_key] = state.distance(planet1_ID, planet2_ID)
    return True

def Fail(s, state):
    return False

def Success(s, state):
    return True

def FindSmallestEnemyPlanet(s, state, output_key):
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
        
    if not weakest_planet: return False   # If no weakest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = weakest_planet # set ID of planet found to specified blackboard entry
    return True

def FindMySmallestPlanet(s, state, output_key):
    weakest_planet = min(state.my_planets(), key=lambda t: t.num_ships, default=None)
        
    if not weakest_planet: return False   # If no weakest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = weakest_planet # set ID of planet found to specified blackboard entry
    return True

def FindMyLargestPlanet(s, state, output_key):
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
        
    if not strongest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = strongest_planet # set ID of planet found to specified blackboard entry
    return True

def FindLargestEnemyPlanet(s, state, output_key):
    strongest_planet = max(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
        
    if not strongest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = strongest_planet # set ID of planet found to specified blackboard entry
    return True

def PredictPlanetSize(s, state, planet, time_passed, output_key):
    ships_needed = planet.num_ships + 1
    if planet.owner == 2: 
        ships_needed += planet.growth_rate * time_passed
        
    s.blackboard[output_key] = ships_needed
    
    return True

def SendShips(s, state, planet1, planet2, fleet_size):
    if fleet_size == 0:
        return False
    return issue_order(state, planet1.ID, planet2.ID, fleet_size)

def GetPlanetGrowthRate(s, state, planet, output_key):
    s.blackboard[output_key] = planet.growth_rate
    return True

def GetPlanetSize(s, state, planet, output_key):
    s.blackboard[output_key] = planet.num_ships
    return True

def FindHighestGrowthEnemyPlanet(s, state, output_key):
    strongest_planet = max(state.enemy_planets(), key=lambda t: t.growth_rate, default=None)
        
    if not strongest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = strongest_planet # set ID of planet found to specified blackboard entry
    return True

def FindMyHighestGrowthPlanet(s, state, output_key):
    strongest_planet = max(state.my_planets(), key=lambda t: t.growth_rate, default=None)
        
    if not strongest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = strongest_planet # set ID of planet found to specified blackboard entry
    return True

def FindHighestGrowthNeutralPlanet(s, state, output_key):
    strongest_planet = max(state.neutral_planets(), key=lambda t: t.growth_rate, default=None)
        
    if not strongest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = strongest_planet # set ID of planet found to specified blackboard entry
    return True

def FindSlowestGrowthEnemyPlanet(s, state, output_key):
    slowest_planet = min(state.enemy_planets(), key=lambda t: t.growth_rate, default=None)
        
    if not slowest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = slowest_planet # set ID of planet found to specified blackboard entry
    return True

def FindMySlowestGrowthPlanet(s, state, output_key):
    slowest_planet = min(state.my_planets(), key=lambda t: t.growth_rate, default=None)
        
    if not slowest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = slowest_planet # set ID of planet found to specified blackboard entry
    return True

def FindSlowestGrowthNeutralPlanet(s, state, output_key):
    slowest_planet = min(state.neutral_planets(), key=lambda t: t.growth_rate, default=None)
        
    if not slowest_planet: return False   # If no largest planet exists (most likely there are 0 planets) then return False
    
    s.blackboard[output_key] = slowest_planet # set ID of planet found to specified blackboard entry
    return True

def GetRandomNeutralPlanet(s, state, output_key):      
    return OutRandomFromCollection(s, state, output_key, state.neutral_planets())

def GetRandomAllyPlanet(s, state, output_key):      
    return OutRandomFromCollection(s, state, output_key, state.my_planets())

def GetRandomEnemyPlanet(s, state, output_key):
   return OutRandomFromCollection(s, state, output_key, state.enemy_planets())

def GetRandomPlanetNotMine(s, state, output_key):
   return OutRandomFromCollection(s, state, output_key, state.not_my_planets())

def LogMessage(s, state, message):
    logging.info(message)
    return True

def RandomIntRange(s, state, min, max, output_key):
    s.blackboard[output_key] = randint(int(min), int(max))
    return True

# gets the number of ships and the owner of a planet at some time in the future based on the current state
def get_future_planet_ships_and_owner(planet, state, time_later):
    planet_ships = planet.num_ships
    planet_owner = planet.owner
    my_fleets = state.my_fleets()
    enemy_fleets = state.enemy_fleets()
    fleets = my_fleets + enemy_fleets

    fleet_arrivals = []
    for index, fleet in enumerate(fleets):
        if fleet.destination_planet != planet.ID:
            continue
        heappush(fleet_arrivals, (fleet.turns_remaining, fleet.num_ships, fleet.owner)) # (time, amount, owner)

    current_time = 0

    while fleet_arrivals:
        time, fleet_ships, fleet_owner = heappop(fleet_arrivals)
        if planet_owner != 0:
            planet_ships += planet.growth_rate * (time - current_time)
        current_time = time
        while fleet_ships > 0:
            subtract_ships = planet_owner != fleet_owner
            used_ships = fleet_ships
            if subtract_ships:
                if planet_ships < used_ships:
                    used_ships = planet_ships
                planet_ships -= used_ships
                fleet_ships -= used_ships
            else:
                planet_ships += used_ships
                fleet_ships -= used_ships
            if planet_ships == 0 and fleet_ships > 0:
                planet_owner = fleet_owner
    if current_time < time_later and planet_owner != 0:
        planet_ships += planet.growth_rate * (time_later - current_time)

    return planet_ships, planet_owner

# gets the number of ships and the owner of a planet, looking forward the amount of time it would take to send a fleet from source->planet, based on the current state 
def get_future_planet_ships_and_owner_from_source(planet, state, source_planet):
    return get_future_planet_ships_and_owner(planet, state, state.distance(planet.ID, source_planet.ID))

action_lookup_table = {
    "AttackWeakestEnemyPlanet" : attack_weakest_enemy_planet,
    "SpreadToWeakestNeutralPlanet" : spread_to_weakest_neutral_planet,
    "SpreadToWeakestClosestPlanet" : spread_to_closest_weakest_planet,
    
    "DoIHavePlanets" : DoIHavePlanets,
    "DoesEnemyHavePlanets" : DoesEnemyHavePlanets,
    "DoNeutralPlanetsExist" : DoNeutralPlanetsExist,
    
    "IHaveFleetsInMotion" : IHaveFleetsInMotion,
    "EnemyHasFleetsInMotion" : EnemyHasFleetsInMotion,
    
    "GetPlanetDistance" : GetPlanetDistance,
    "AlwaysFailure" : Fail,
    "AlwaysSuccess" : Success,
    
    "FindLargestEnemyPlanet" : FindLargestEnemyPlanet,
    "FindSmallestEnemyPlanet" : FindSmallestEnemyPlanet,
    "FindMyLargestPlanet" : FindMyLargestPlanet,
    "FindMySmallestPlanet" : FindMySmallestPlanet,
    
    "PredictPlanetSize" : PredictPlanetSize,
    "SendShips" : SendShips,
    "GetPlanetGrowthRate" : GetPlanetGrowthRate,
    "GetPlanetDistance" : GetPlanetDistance,
    "GetPlanetSize" : GetPlanetSize,
    
    "FindHighestGrowthEnemyPlanet" : FindHighestGrowthEnemyPlanet,
    "FindMyHighestGrowthPlanet" : FindMyHighestGrowthPlanet,
    "FindHighestGrowthNeutralPlanet" : FindHighestGrowthNeutralPlanet,
    
    "FindSlowestGrowthEnemyPlanet" : FindSlowestGrowthEnemyPlanet,
    "FindMySlowestGrowthPlanet" : FindMySlowestGrowthPlanet,
    "FindSlowestGrowthNeutralPlanet" : FindSlowestGrowthNeutralPlanet,
    
    "GetRandomNeutralPlanet" : GetRandomNeutralPlanet,
    "GetRandomAllyPlanet" : GetRandomAllyPlanet,
    "GetRandomEnemyPlanet" : GetRandomEnemyPlanet,
    "GetRandomPlanetNotMine" : GetRandomPlanetNotMine,
    
    "LogMessage" : LogMessage,
    "RandomIntRange" : RandomIntRange
}

composite_lookup_table = {
    "Sequence" : Sequence,
    "SequenceWithMemory" : SequenceWithMemory,
    "Fallback" : Selector,
    "FallbackWithMemory" : SelectorWithMemory
}

decorator_lookup_table = {
    "ForceSuccess" : ForceSuccess,
    "ForceFailure" : ForceFailure,
    "Repeat" : LoopFor,
    "Cooldown" : Cooldown,
    "KeepRunningUntilFailure" : LoopUntilFail,
    "RetryUntilSuccessful" : LoopUntilSuccess,
    "Inverter" : Inverter,
    "RunOnce" : RunOnce
    
}