from typing import Literal
import examples.ags.w_action_node.optimized.Gsm8K.graphs.template.operator as operator
import examples.ags.w_action_node.optimized.Gsm8K.graphs.round_21.prompt as prompt_custom
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.utils.cost_manager import CostManager

DatasetType = Literal["HumanEval", "MMBP", "Gsm8K", "MATH", "HotpotQa", "MMLU"]

class SolveGraph:
    def __init__(
        self,
        name: str,
        llm_config,
        dataset: DatasetType,
    ) -> None:
        self.name = name
        self.dataset = dataset
        self.llm = create_llm_instance(llm_config)
        self.llm.cost_manager = CostManager()
        self.custom = operator.Custom(self.llm)
        self.sc_ensemble = operator.ScEnsemble(self.llm)
        self.programmer = operator.Programmer(self.llm)

    async def __call__(self, problem: str):
        """
        Implementation of the graph
        """
        solutions = []
        for _ in range(5):  # Generate 5 solutions
            solution = await self.custom(input=problem, instruction=prompt_custom.MATH_SOLVE_PROMPT)
            solutions.append(solution['response'])
        
        final_solution = await self.sc_ensemble(solutions=solutions, problem=problem)
        
        # Add a verification step using the Programmer operator
        verification = await self.programmer(problem=problem, analysis=final_solution['response'])
        
        if verification['output']:
            final_answer = verification['output']
        else:
            final_answer = final_solution['response']

        # Final check to ensure the answer is a single number
        try:
            final_answer = float(final_answer)
        except ValueError:
            final_answer = float(final_answer.split()[-1])

        return str(final_answer), self.llm.cost_manager.total_cost
                    