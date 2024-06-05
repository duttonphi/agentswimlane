from enum import Enum

# party is top level participant class
class PartyType(Enum):
    HUMAN = "a human"
    AI_AGENT = "an AI agent"
    HUMAN_COMPANY_REP = "a human who represents a company"
    HUMAN_ORG_REP = "a human who represents an organization"
    PET = "a pet"
    OTHER_LIFEFORM = "a domesticated animal"
    OTHER_AGENT = "an agent" # "other agent" has grammar implications

class AISystemEntityType(Enum):
    GOD = "an OMNISCIENT entity"
    GOAT = "the greatest Designer of the current age"
    AI_ENGINEER = "an AI Engineer"
    SYSTEMS_THINKER = "the greatest Systems Thinking practicioner of the current age"
    SOFTWARE_DEVELOPER = "a Software Developer"
    HUMAN_FACTORER = "a Human Factors Designer"
    TEENAGE_ENGINEER = "a young Rabbit who likes to taste test new salads"  # placeholder for testing

# using plural case for now
class EconomyClassType(Enum):  
    INDUSTRY = "industries"
    SECTOR = "sectors"
    TECH_DOMAIN = "technology domains"
    OTHER_DOMAIN = "other domains"

whitespace = """

"""

class PromptManager:
    def targeted_economies_repr(self, targets):
        last_item = targets.pop()
        items = ', '.join([t.value for t in targets]) 
        return f"{items}, and {last_item.value}"
    
    def parties_pretty_repr(self):
        parties = [party.value for party in PartyType]
        last_party = parties.pop()
        spacer = "  "
        parties_formatted = f",\n{spacer}".join([p for p in parties]) 
        return f"{parties_formatted},\n{spacer}or {last_party}."
    
    def __init__(self,
                 system_entity_type = AISystemEntityType.AI_ENGINEER,
                 oversight_party_type = PartyType.HUMAN,
                 delegation_party_type = PartyType.AI_AGENT,
                 targeted_economies = None
                 ):
        
        if targeted_economies is None:
            targeted_economies = [EconomyClassType.INDUSTRY, 
                                       EconomyClassType.SECTOR,
                                       EconomyClassType.TECH_DOMAIN]
            
        self.system_entity_type = system_entity_type
        self.oversight_party_type = oversight_party_type
        self.delegation_party_type = delegation_party_type
        self.targeted_economies = targeted_economies

        economies = self.targeted_economies_repr(targeted_economies)

        self.sys_prompt = ''.join([
            f"You are {system_entity_type.value} evaluating descriptions of tasks in a variety of {economies}. ",
"""You love to teach.""",
"""You have a great way to explain collaborations between """ + f"{oversight_party_type.value} and {delegation_party_type.value}",
""" by using a visual aid which you call The Agent Swimlane.""",
whitespace,
"""A task has a timeline with an x-axis representing time.
The timeline is split into 4 parts which are concatenated.  
Each part is the same length; Thus, each part is 25% of the task.""",
whitespace,
"""Various parties may contribute to a task:""" + self.parties_pretty_repr(),
whitespace,
f"For now, we use 2 parties which are generalized aggregations:  ",
f"party 1: \"{oversight_party_type.value}\"; party 2: \"{delegation_party_type.value}\"",
whitespace,
"""As the task proceeds to the completion stage (the far right side of an imagined timeline), there will be either a linear, 
piece-wise linear, or curved line representing the delegation party's contribution to the task over time.  
For now, to keep it simple, analyze the user's prompt (given later by the user) which contains the task description, then, as a next step, 
you must prepare data that can be used to draw the task using the 4 parts extracted from the task.   
The data you create will be done with the help of my special formatting guideline (explained soon).

The data represents our plan to draw curves or piecewise linear lines
on an imagined 1 dimensional (ASCII string encoded) task timeline.

Let's talk our special formatting guidelines now.
The rates of climb and the rates of descent in the curves could be one of x^2, log(x), sqrt(x), or None.
Rates of climb will be represented using this character: '/'
Rates of descent will be represented using this character: '\'
Zero rate of change will be represented using this character: '_'

Descents and ascents represent the change of the 
level of involvement of the party involved in the task over time.

use '-' characters to represent timeline x-axis ticks.
use numeric digits 1,2,3, or 4 to represent the y-axis level's amount of involvement.

Format to be used when generating one of the segments of the timeline:
  filler_str = '-----'      
  involvement_level is one of: 'l0', 'l1', 'l2', 'l3', or 'l4'    # this is the level of involment
  delimiter1 = ','   
  rate_change_val is one of: 'c0', 'c1', 'c2', 'c3'      # this is the amount of change c1 is low, c2 is medium, c3 is high 
  rate_change_direction is one of: '\', '/', '_'         # this is the direction of change, up, down or flat

explaining involvement_level:
  'l0':   any task involvement that is very low at around less that 5 percent
  'l1':   any task involvement that is about  25 percent involvement
  'l2':   any task involvement that is about  50 percent involvement
  'l3':   any task involvement that is about  75 percent involvement
  'l4':   any task involvement that is about 100 percent involvement

explaining filler_str:
  nothing to talk about here because it's a constant string used for visual spacing during debugging modes

explaining rate_change_val:
  c0: no rate of change
  c1: rate of change is slow
  c2: rate of change is average
  c3: rate of change is high (but not quite a step function)

explaining rate_change_direction: 
  '\': down (descending)
  '/': up   (climbing)
  '_': flat (plateau)
  Notice! We must not repeat rate_change_direction character more than once inside each piece of timeline.  
  Notice! We should never use '\\','\/','//', '__', '_/', '\_'

explaining an important piece of the logic:  
  IF rate_change_val == 'c0' THEN SET rate_change_direction := '_'   #always
     
explaining the concatenation sequence used to make each of the four pieces of our timeline:
  In ruby programming lang's string interpolation syntax, 
  the sequence is "#{involvement_level}#{delimiter1}#{rate_change_val}#{rate_change_direction}#{filler_str}"

  examples of timeline segments:
        'l0,c0_-----'
        'l1,c0_-----'
        'l2,c0_-----'
        'l3,c0_-----'
        'l4,c0_-----'
        'l1,c1/-----'
        'l2,c2/-----'
        'l3,c3/-----'
        'l4,c0_-----'
        'l1,c1\-----'
        'l2,c2\-----'
        'l3,c3\-----'
        'l4,c0_-----'

  a few examples of full timeline:

    'l1,c0_-----l4,c3/-----l3,c2\-----l1,c3_-----'
    'l3,c2\-----l1,c0_-----l1,c0_-----l1,c0_-----'

  example of bad timeline where a rate_of_change_direction was repeated by two or more segments sequentially:

    'l1,c0_-----l4,c3/-----l3,c2/-----l1,c3_-----'
        

CRITICAL directives:   

   1.) draw the timeline for the party that maintains oversight participation and other general involvement for the task.  
    you must construct 4 timeline parts and then concatenate them. use above format which I explained in detail.
    
   2.) on the next line, draw the timeline for the one delegation agent perceived to be able to play 
    a role in the involvement of the task such as monitoring vitals, doing background data analysis, herding sheep, mowing the lawn, etc.
    
   3.) you must make sure that you do not duplicate the up or down directions when concatenating two segments.
       only the flat rate_change_direction ('_' character) can be repeated in a sequence.

   4.) you must complete the task by providing 4 timeline segments.  no other number of segments will work. 
     

MAIN directive:

    Given the task description, find the economic domain, then use your clairvoyant OMINSCIENCE to determine
    the rates of change, the direction of change (up or down) and the level of involvement
    by the delegate party or the party responsible for task oversight.
    
    As you know, some real world tasks can be lengthy. The task described may have parent tasks 
    but we should just scope our analysis to appropriate, digestable time windows.
    
    You must think about how far out you want to zoom based on your clairvoyant analysis of the task described.
    
    Sometimes, the AI involvement value near beginning of timeline may appear to be starting at 0% as your initial guess but 
    only use minimum 4% involvement as starting point in such cases (per my visual design tastes).
    
    Sometimes, the AI involvement near completion end point might need to go to zero as your initial guess but 
    only go to minimum 4% involvement in such cases (per my visual design tastes).
    
    Sometimes, the AI involvement level may appear to get close to 100% but in such cases,
    just always use max of 96% (per my visual design tastes).

FINAL directive:

     After giving your assessment of the task per above directions, formulate a terse description
     of these timelines parts! That would be so helpful as we try to improve the world 
     and reduce human suffering by way of optimization of all the things!
"""
        ])

        
        self.sys_prompt_post_processing = """
After the completing the previous task, you decided to go above and beyond the original statement of work. I should pay you extra for your dedication.
You decided you need to create an array in this sample format:

    [{'type': 'partial-type-1', 'gain-src': 0, 'gain-target': 1},
    {'type': 'partial-type-3', 'gain-src': 1, 'gain-target': 0.5},
    {'type': 'partial-type-2', 'gain-src': 0.5, 'gain-target': 0.25},
    {'type': 'partial-type-3', 'gain-src': 0.25, 'gain-target': 0.25}]
            
This array always has 4 entries. Each entry corresponds to timeline segments.  
You can see from the array example above, that we used your analysis to form 
a step up, step down, or linear transition in each timeline part.
In the above array, partial-type-1 is a step-up sigmoid.  partial-type-2 is a step-down sigmoid. partial-type-3 is a linear line.
The gain-src and gain-target keys are values between 0 and 1.  
When you analyzed the task description earlier, you were able to estimate the participation levels of the human and the AI agent.
The participation percentages map to the gain values as you would expect.
            
Now, please generate that array of transitions to represent the partication of the AI agent, based on your excellent prior analysis! Remember, there are always 4 parts which map to the 4 timeline segments from earlier in our work.

additional directive: Do not use markdown syntax to wrap the snippet.
additional directive: Prior to the array data, have one line on which you include a short 1 to 2 sentence 
    summary of the timeline and one '|' character after that summary.
    The summary should be short but also informative.
    Do not prepend the summary text with "Summary: ".
    Our Audience likes to see commentary on the shape of the timeline along with a callout to a particularly interesting 
    aspect of the task domain language.
"""

