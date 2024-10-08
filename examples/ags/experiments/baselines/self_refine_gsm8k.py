from examples.ags.scripts.operator import Operator
from examples.ags.scripts.graph import SolveGraph
from examples.ags.benchmark.gsm8k import gsm8k_evaluation
from metagpt.actions.action_node import ActionNode 
from metagpt.configs.models_config import ModelsConfig
from metagpt.llm import LLM
from pydantic import BaseModel, Field
from typing import Dict, Any

GSM8K_PROMPT_GPT = """
{question}\nPlease reason step by step. At the end, provide the final answer in the format "Answer is <number>", where <number> is a single number, without any additional information or explanation.
"""

REVIEW_PROMPT = """
Given a problem and a thoughtful solution, your task is to using critical thinking (questioning) to review the solution's correctness and provide a review result in boolean format.

problem: {problem}
solution: {solution}

If you are more than 95 percent confident that the final answer is incorrect, please return False and give a feedback for the error. Otherwise, please return True and give a explanation for the correctness.
"""

REVISE_PROMPT = """
Given a problem and a thoughtful solution which is just reviewed as incorrect, your task is to revise the solution to solve the question and ensure the final answer in the format "Answer is <number>", where <number> is a single number.

problem: {problem}
solution: {solution}
feedback: {feedback}
"""

class GenerateOp(BaseModel):
    solution: str = Field(default="", description="solution for the problem")

class ReviewOp(BaseModel):
    feedback: str = Field(
        default="",
        description="Your FeedBack for this problem based on the criteria. If the review result is true, you can put it 'nothing here'.",
    )
    review_result: bool = Field(
        default=False,
        description="The Review Result (Bool). If you think this solution looks good for you, return 'true'; If not, return 'false'",
    )


class ReviseOp(BaseModel):
    solution: str = Field(default="", description="Based on the feedback, revised solution for this problem")


class CoTGenerate(Operator):
    def __init__(self, llm: LLM, name: str = "Generate"):
        super().__init__(name, llm)

    async def __call__(self, problem, mode: str = "context_fill"):
        prompt = GSM8K_PROMPT_GPT.format(question=problem)
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        node = await ActionNode.from_pydantic(GenerateOp).fill(**fill_kwargs)
        response = node.instruct_content.model_dump()
        return response
    
class Review(Operator):
    def __init__(self, llm: LLM, name: str = "Review"):
        super().__init__(name, llm)

    async def __call__(self, problem, solution, mode: str = "context_fill"):
        prompt = REVIEW_PROMPT.format(problem=problem, solution=solution)
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        node = await ActionNode.from_pydantic(ReviewOp).fill(**fill_kwargs)
        response = node.instruct_content.model_dump()
        return response

class Revise(Operator):
    def __init__(self, llm: LLM, name: str = "Revise"):
        super().__init__(name, llm)

    async def __call__(self, problem, solution, feedback, mode: str = "context_fill"):
        prompt = REVISE_PROMPT.format(problem=problem, solution=solution, feedback=feedback)
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        node = await ActionNode.from_pydantic(ReviseOp).fill(**fill_kwargs)
        response = node.instruct_content.model_dump()
        return response  

class SelfRefineGraph(SolveGraph):
    def __init__(self, name: str, llm_config, dataset: str):
        super().__init__(name, llm_config, dataset)
        self.cot_generate = CoTGenerate(self.llm)
        self.review = Review(self.llm)
        self.revise = Revise(self.llm)

    async def __call__(self, problem):
        solution = await self.cot_generate(problem, mode="context_fill")
        for i in range(3):
            review = await self.review(problem, solution)
            if review["review_result"]:
                break
            solution = await self.revise(problem, solution, review["feedback"])
        return solution, self.llm.cost_manager.total_cost

if __name__ == "__main__":
    async def main():
        llm_config = ModelsConfig.default().get("gpt-4o-mini")
        graph = SelfRefineGraph(name="self-refine", llm_config=llm_config, dataset="Gsm8K")
        file_path = "examples/ags/data/gsm8k.jsonl"
        samples = 264
        path = "examples/ags/data/baselines/general"
        score, cost = await gsm8k_evaluation(graph, file_path, samples, path, test=True)
        return score, cost

    import asyncio
    asyncio.run(main())
