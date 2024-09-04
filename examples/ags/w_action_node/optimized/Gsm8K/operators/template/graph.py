# -*- coding: utf-8 -*-
# @Date    : 6/27/2024 22:07 PM
# @Author  : didi
# @Desc    : Basic Graph Class

# from typing import Literal

# from examples.ags.w_action_node.optimized.Gsm8K.operators.template.op_prompt import *
# from examples.ags.w_action_node.optimized.Gsm8K.operators.template.operator import *
# from metagpt.provider.llm_provider_registry import create_llm_instance
# from metagpt.utils.cost_manager import CostManager

# DatasetType = Literal["HumanEval", "MMBP", "Gsm8K", "MATH", "HotpotQa", "MMLU"]


# class SolveGraph:
#     def __init__(
#         self,
#         name: str,
#         llm_config,
#         dataset: DatasetType,
#     ) -> None:
#         self.name = name
#         self.dataset = dataset
#         self.llm = create_llm_instance(llm_config)
#         self.llm.cost_manager = CostManager()
#         self.generate = Generate(self.llm)

#     async def __call__(self, problem: str):
#         """
#         Implementation of the graph based on the generate operator, you can modify it to fit operators you want to use.
#         For Example, for Custom Operator, you can add self.custom = Custom(self.llm) and call it in the __call__ method
#         """
#         solution = await self.generate(problem)
#         return solution, self.llm.cost_manager.total_cost