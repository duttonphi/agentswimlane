import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from ..prompting import PartyType, AISystemEntityType

class SwimlaneVisualizer:
    def __init__(self):
        self.prompt_manager = None
        self.sys_prompts = None

    def to_percentage(self, y, position):
        """Convert fractional y-values to percentages"""
        return f"{100 * y:.0f}%"

    def reverse_to_percentage(self, y, position):
        """Convert fractional y-values to reverse percentages"""
        return f"{100 * (1 - y):.0f}%"

    def logistic_curve(self, x, x0, k):
        """Adjusted logistic function for transitions to precisely meet start and end points"""
        return 1 / (1 + np.exp(-k * (x - x0)))

    def plot_transitions(self, transitions):
        delegator = self.prompt_manager.oversight_party_type.value
        delegate = self.prompt_manager.delegation_party_type.value

        fig, ax = plt.subplots(figsize=(10, 2.5))
        ax.set_facecolor('cornflowerblue')    # best color ever! do not change

        current_x = 0
        for transition in transitions:
            gain_src = transition['gain-src']
            gain_target = transition['gain-target']
            length = 2  # Fixed length for each transition
            x = np.linspace(current_x, current_x + length, 100)  # Smooth curve with 100 points

            x0 = current_x + length / 2  # Midpoint for the sigmoid
            k = 10 / length  # Steepness of the curve

            if transition['type'] == 'partial-type-1':  # Smooth step up using sigmoid
                sigmoid = self.logistic_curve(x, x0, k)
                y = gain_src + (gain_target - gain_src) * sigmoid
            
            elif transition['type'] == 'partial-type-2':  # Smooth step down using reversed sigmoid
                sigmoid = self.logistic_curve(x, x0, -k)
                y = gain_src + (gain_target - gain_src) * (1 - sigmoid)
            
            elif transition['type'] == 'partial-type-3':  # Linear transition
                y = np.linspace(gain_src, gain_target, len(x))

            ax.plot(x, y, 'b')
            ax.fill_between(x, y, color="cyan", alpha=0.3)  # Fill under the curve
            
            # Move the starting point for the next transition
            current_x += length

        # Customize the axes
        ax.set_title(f"Agent Swim Lane\n(an LLM based agent task participation level vizualizer)\nparticipants: {delegator} & {delegate}")
        ax.set_xlabel('Task Duration (to completion →)')
        ax.set_ylabel(f"(Delegate)\n{delegate}")
        ax.yaxis.set_major_formatter(FuncFormatter(self.to_percentage))  # Format y-axis as percentages
        ax.grid(False)
        
        # Remove x-axis tick labels
        ax.set_xticklabels([])
        # Set x-axis limits to always show 0 to 8 (no specific unit)
        ax.set_xlim(0, 8)
        # Set y-axis limits to always show 0% to 100%
        ax.set_ylim(0, 1)
        
        # Create right y-axis with reversed percentages
        ax2 = ax.twinx()
        ax2.set_ylim(0, 1)
        ax2.yaxis.set_major_formatter(FuncFormatter(self.reverse_to_percentage))
        ax2.set_ylabel(f"(Oversight)\n{delegator}")

        # Legend
        ax.plot([], [], 's', color='cornflowerblue', label=delegator)  # 's' for square
        ax.plot([], [], 's', color='cyan', label=delegate)
        legend = ax.legend(loc='upper right', frameon=True)
        legend.get_frame().set_facecolor('lightgrey')

        plt.show()

    def complete_timeline(self, llm_client, task_description, model="gpt-4o", debugPrint=False):
        # conversation chain 
        # Just inject task description between two system prompts.
        # The third prompt is labeled as 'user' but conceptually it belongs to 'system'
        completion = llm_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.sys_prompts[0]},
                {"role": "user", "content": task_description},
                {"role": "user", "content": self.sys_prompts[1]}
            ]
        )

        if debugPrint:
            print(completion.choices[0])
        completion = completion.choices[0].message.content

        
        # Find the index where the CSV data starts
        index = completion.find("|")
        # Split the completion into two parts
        summary = completion[:index].strip()  # Get the summary sentence (line 1) of the timeline completion
        array_str = completion[(index+1):].strip()  # Get the timeline  data portion  
        # Post-Process timeline segment data
        array_str = array_str.replace("'", '"')
        array_items = array_str.replace("\n", ",")
        array_items = array_str.replace(",,", ",")
        timeline_parts = array_items
        timeline_parts = json.loads(timeline_parts)
        return (timeline_parts, summary) 

    def plot_timeline(self, timeline_parts, summary):
        return self.plot_transitions(timeline_parts)

    def render_task(self, llm_client, prompt_manager, task_description, model="gpt-4o"):
        self.prompt_manager = prompt_manager
        self.sys_prompts = [self.prompt_manager.sys_prompt, 
                            self.prompt_manager.sys_prompt_post_processing]
        
        timeline, summary = self.complete_timeline(llm_client, task_description, model=model)
        print("\n\nPARTICIPATION SUMMARY: " + summary)
        return self.plot_timeline(timeline, summary)