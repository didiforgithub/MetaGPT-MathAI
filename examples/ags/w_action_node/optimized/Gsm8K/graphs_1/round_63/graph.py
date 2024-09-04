from typing import Literal
from examples.ags.w_action_node.optimized.Gsm8K.graphs.template.operator import *
from examples.ags.w_action_node.optimized.Gsm8K.graphs.round_63.prompt import *
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
        self.generate = Generate(self.llm)
        self.format = Format(self.llm)
        self.custom = Custom(self.llm)
        self.review = Review(self.llm)
        self.sc_ensemble = ScEnsemble(self.llm)
        self.rephrase = Rephrase(self.llm)

    async def __call__(self, problem: str):
        """
        Implementation of the graph
        """
        think = await self.custom(input=problem, instruction=THINK_PROMPT)
        rephrased_problem = await self.rephrase(problem=problem)
        solutions = []
        num_solutions = 3
        max_solutions = 5
        
        while num_solutions <= max_solutions:
            for _ in range(num_solutions):
                solution = await self.generate(problem=problem+think['response']+rephrased_problem['rephrased_problem'])
                reflection = await self.custom(input=solution['response'], instruction=REFLECT_PROMPT)
                solutions.append(solution['response'] + reflection['response'])
            
            best_solution = await self.sc_ensemble(solutions=solutions, problem=problem)
            
            review_result = await self.review(problem=problem, solution=best_solution['solution'])
            if review_result['review_result']:
                break
            
            num_solutions += 1
            solutions = []  # Reset solutions for the next iteration
        
        format_solution = await self.format(problem=problem, solution=best_solution['solution'])
        return format_solution, self.llm.cost_manager.total_cost
                    